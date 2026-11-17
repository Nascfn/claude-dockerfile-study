#!/usr/bin/env python3
"""Build one image, scan it with Trivy (image mode), record the facts, delete it.

usage: image_eval.py <context_dir> <Dockerfile> <tag> <outdir> [--timeout N]
Writes into <outdir>: build.json, build.log.gz, and (if the build succeeded)
trivy_image.json.gz and image.json (summary). The Trivy vulnerability database
is downloaded once up front and reused (--skip-db-update) so that every image
is judged against the same database.
"""
import gzip, json, os, shutil, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
SEVS = ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW', 'UNKNOWN']

def sh(cmd, timeout=None):
    return subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)

def evaluate(context, dockerfile, tag, outdir, timeout=1500):
    os.makedirs(outdir, exist_ok=True)
    log = os.path.join(outdir, 'build.log')
    r = sh([sys.executable, os.path.join(HERE, 'build_image.py'), '--context', context, '--dockerfile', dockerfile,
            '--tag', tag, '--log', log, '--timeout', str(timeout)], timeout=timeout + 2400)
    try: build = json.loads(r.stdout.strip().splitlines()[-1])
    except Exception: build = {'ok': False, 'error': 'harness crashed: ' + (r.stdout + r.stderr)[-300:]}
    if os.path.exists(log):
        lines = open(log, errors='replace').read().splitlines()
        build['log_tail'] = lines[-25:] if not build.get('ok') else []
        with gzip.open(log + '.gz', 'wt') as g: g.write('\n'.join(lines[-4000:]))
        os.unlink(log)
    json.dump(build, open(os.path.join(outdir, 'build.json'), 'w'), indent=1)
    summary = None
    if build.get('ok'):
        insp = json.loads(sh(['docker', 'image', 'inspect', tag]).stdout)[0]
        cfg = insp.get('Config') or {}
        tj = os.path.join(outdir, 'trivy_image.json')
        t = sh(['trivy', 'image', '--quiet', '--skip-db-update', '--skip-java-db-update', '--scanners', 'vuln,secret',
                '--format', 'json', '--output', tj, '--timeout', '20m', tag], timeout=1500)
        summary = {'tag': tag, 'size_bytes': insp.get('Size'), 'user': cfg.get('User') or '',
                   'runs_as_root': (cfg.get('User') or '').split(':')[0] in ('', '0', 'root'),
                   'exposed_ports': sorted((cfg.get('ExposedPorts') or {}).keys()),
                   'has_healthcheck': bool(cfg.get('Healthcheck')), 'trivy_ok': t.returncode == 0,
                   'vulns': {s: 0 for s in SEVS}, 'vulns_fixable': {s: 0 for s in SEVS},
                   'vulns_by_class': {}, 'secrets': 0, 'os': None}
        if t.returncode == 0 and os.path.exists(tj):
            d = json.load(open(tj))
            summary['os'] = ((d.get('Metadata') or {}).get('OS') or {})
            for res in d.get('Results') or []:
                cls = res.get('Class', '?')
                for v in res.get('Vulnerabilities') or []:
                    s = v.get('Severity', 'UNKNOWN')
                    summary['vulns'][s] += 1
                    if v.get('FixedVersion'): summary['vulns_fixable'][s] += 1
                    summary['vulns_by_class'][cls] = summary['vulns_by_class'].get(cls, 0) + 1
                summary['secrets'] += len(res.get('Secrets') or [])
            summary['vulns_total'] = sum(summary['vulns'].values())
            with open(tj, 'rb') as f, gzip.open(tj + '.gz', 'wb') as g: shutil.copyfileobj(f, g)
            os.unlink(tj)
        else:
            summary['trivy_error'] = (t.stdout + t.stderr)[-400:]
        json.dump(summary, open(os.path.join(outdir, 'image.json'), 'w'), indent=1)
    sh(['docker', 'image', 'rm', '-f', tag])
    return build, summary

if __name__ == '__main__':
    to = int(sys.argv[sys.argv.index('--timeout') + 1]) if '--timeout' in sys.argv else 1500
    b, s = evaluate(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4], to)
    print(json.dumps({'ok': b.get('ok'), 'seconds': b.get('seconds'), 'error': b.get('error'),
                      'vulns': s and s.get('vulns'), 'user': s and s.get('user'), 'size_mb': s and round((s.get('size_bytes') or 0) / 1e6)}))
