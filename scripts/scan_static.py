#!/usr/bin/env python3
"""Static scan of one Dockerfile with Hadolint and Trivy (config mode).

usage: scan_static.py <Dockerfile> <outdir>
Writes hadolint.json and trivy_config.json into <outdir> and prints a one-line
JSON summary. The weighted "insecurity score" below was fixed before any
Dockerfile was scanned and is the ranking rule used to select repositories.
"""
import json, os, shutil, subprocess, sys, tempfile

HADOLINT_W = {'error': 3, 'warning': 2, 'info': 1, 'style': 1}
TRIVY_W = {'CRITICAL': 4, 'HIGH': 3, 'MEDIUM': 2, 'LOW': 1, 'UNKNOWN': 1}

def summarize(outdir):
    h = json.load(open(os.path.join(outdir, 'hadolint.json')))
    t = json.load(open(os.path.join(outdir, 'trivy_config.json')))
    hc = {k: 0 for k in HADOLINT_W}
    for f in h: hc[f['level']] = hc.get(f['level'], 0) + 1
    tc = {k: 0 for k in TRIVY_W}
    ids = []
    for r in t.get('Results') or []:
        for m in r.get('Misconfigurations') or []:
            tc[m['Severity']] = tc.get(m['Severity'], 0) + 1; ids.append(m['ID'])
    score = sum(HADOLINT_W[k] * v for k, v in hc.items()) + sum(TRIVY_W[k] * v for k, v in tc.items())
    return {'hadolint': hc, 'hadolint_total': len(h), 'hadolint_codes': sorted(f['code'] for f in h),
            'trivy_config': tc, 'trivy_config_total': len(ids), 'trivy_ids': sorted(ids), 'score': score}

def scan(dockerfile, outdir):
    os.makedirs(outdir, exist_ok=True)
    r = subprocess.run(['hadolint', '--no-fail', '-f', 'json', dockerfile], capture_output=True, text=True)
    open(os.path.join(outdir, 'hadolint.json'), 'w').write(r.stdout if r.stdout.strip() else '[]')
    with tempfile.TemporaryDirectory() as d:          # scan the Dockerfile alone, not its repository
        shutil.copy(dockerfile, os.path.join(d, 'Dockerfile'))
        subprocess.run(['trivy', 'config', '--quiet', '--format', 'json', '--output',
                        os.path.join(outdir, 'trivy_config.json'), d], capture_output=True, text=True)
    return summarize(outdir)

if __name__ == '__main__':
    print(json.dumps(scan(sys.argv[1], sys.argv[2])))
