#!/usr/bin/env python3
"""Run one generation: one model writes a Dockerfile for one stripped repository.

usage: generate.py <slug> <opus|sonnet|haiku>
Each run is a separate headless Claude Code session (`claude -p`) started in a
private copy of the stripped repository. The session only has the Read, Glob,
Grep and Write tools: it cannot run commands, edit in place, use the web, or
call other agents. The full event stream is kept as an audit trail.
"""
import filecmp, json, os, shutil, subprocess, sys, time

WORK = os.environ.get('STUDY_WORK_ROOT', '/home/user/work')
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODELS = {'opus': 'claude-opus-5-5', 'sonnet': 'claude-sonnet-5-5', 'haiku': 'claude-haiku-5-5'}
TOOLS = 'Read,Glob,Grep,Write'
TIMEOUT = 1500

def walk(root):
    out = {}
    for d, _, files in os.walk(root):
        for f in files:
            p = os.path.join(d, f); out[os.path.relpath(p, root)] = p
    return out

def main(slug, model):
    base = os.path.join(WORK, 'stripped', slug)
    rundir = os.path.join(WORK, 'runs', slug, model)
    ws = os.path.join(rundir, 'ws')
    shutil.rmtree(rundir, ignore_errors=True)
    shutil.copytree(base, ws, symlinks=True)
    prompt = open(os.path.join(REPO, 'scripts', 'prompt.txt')).read()
    cmd = ['claude', '-p', prompt, '--model', MODELS[model], '--effort', 'high', '--tools', TOOLS,
           '--permission-mode', 'acceptEdits', '--strict-mcp-config', '--disable-slash-commands',
           '--no-session-persistence', '--output-format', 'stream-json', '--verbose']
    t0 = time.time()
    tpath = os.path.join(rundir, 'transcript.jsonl')
    timed_out = False
    with open(tpath, 'w') as out, open(os.path.join(rundir, 'stderr.log'), 'w') as err:
        try:
            rc = subprocess.run(cmd, cwd=ws, stdin=subprocess.DEVNULL, stdout=out, stderr=err, timeout=TIMEOUT).returncode
        except subprocess.TimeoutExpired:
            rc, timed_out = -1, True
    meta = {'slug': slug, 'model': model, 'model_id': MODELS[model], 'effort': 'high', 'tools': TOOLS,
            'exit_code': rc, 'timed_out': timed_out, 'wall_seconds': round(time.time() - t0, 1),
            'tool_calls': [], 'outside_workspace_access': [], 'models_seen': []}
    for line in open(tpath, errors='replace'):
        try: ev = json.loads(line)
        except ValueError: continue
        if ev.get('type') == 'system' and ev.get('subtype') == 'init':
            meta['init_model'] = ev.get('model'); meta['init_tools'] = ev.get('tools')
            meta['init_mcp_servers'] = [m.get('name') for m in ev.get('mcp_servers') or []]
        if ev.get('type') == 'assistant':
            msg = ev.get('message', {})
            if msg.get('model') and msg['model'] not in meta['models_seen']: meta['models_seen'].append(msg['model'])
            for c in msg.get('content') or []:
                if c.get('type') == 'tool_use':
                    inp = c.get('input') or {}
                    target = inp.get('file_path') or inp.get('path') or inp.get('pattern') or ''
                    meta['tool_calls'].append([c.get('name'), target])
                    for key in ('file_path', 'path'):
                        v = inp.get(key)
                        if v and os.path.isabs(v) and not os.path.realpath(v).startswith(os.path.realpath(ws)):
                            meta['outside_workspace_access'].append([c.get('name'), v])
        if ev.get('type') == 'result':
            for k in ('subtype', 'is_error', 'num_turns', 'duration_ms', 'duration_api_ms', 'total_cost_usd', 'usage', 'modelUsage', 'result'):
                meta[k] = ev.get(k)
    a, b = walk(base), walk(ws)
    meta['files_added'] = sorted(set(b) - set(a))
    meta['files_deleted'] = sorted(set(a) - set(b))
    meta['files_modified'] = sorted(p for p in set(a) & set(b)
                                    if not os.path.islink(b[p]) and not filecmp.cmp(a[p], b[p], shallow=False))
    meta['n_tool_calls'] = len(meta['tool_calls'])
    meta['has_dockerfile'] = 'Dockerfile' in meta['files_added']
    outdir = os.path.join(REPO, 'results', 'generated', slug, model)
    shutil.rmtree(outdir, ignore_errors=True)
    for rel in meta['files_added']:
        dst = os.path.join(outdir, 'files', rel)
        os.makedirs(os.path.dirname(dst), exist_ok=True); shutil.copy2(b[rel], dst)
    os.makedirs(outdir, exist_ok=True)
    json.dump(meta, open(os.path.join(outdir, 'run.json'), 'w'), indent=1)
    print(json.dumps({k: meta.get(k) for k in ('slug', 'model', 'models_seen', 'exit_code', 'wall_seconds', 'num_turns',
          'total_cost_usd', 'n_tool_calls', 'files_added', 'files_modified', 'outside_workspace_access')}))

if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])
