#!/usr/bin/env python3
"""Build one Docker image and report whether the build succeeded.

The experiment ran inside a cloud sandbox whose network (a) intercepts TLS with
a private certificate authority and (b) only allows HTTPS through a local proxy.
To make ordinary Dockerfiles buildable there, every external base image named in
a FROM line is wrapped in a thin "shim" image that trusts the sandbox CA and
points apt at HTTPS, and the build runs on the host network with proxy build
args. The Dockerfile under test is never edited on disk: a temporary copy with
rewritten FROM lines is passed to `docker build -f`. Scanners always read the
unmodified Dockerfile. Pass --no-shim to build normally outside such a sandbox.
"""
import argparse, json, os, re, subprocess, sys, tempfile, time, shutil

SHIM_DIR = os.environ.get('CCR_SHIM_DIR', '/opt/study-tools/shim')
PROXY = os.environ.get('HTTPS_PROXY', '')
NO_PROXY = os.environ.get('NO_PROXY', '')
SHIM_ENV = {
    'SSL_CERT_FILE': '/etc/ssl/ccr-bundle.crt', 'REQUESTS_CA_BUNDLE': '/etc/ssl/ccr-bundle.crt',
    'PIP_CERT': '/etc/ssl/ccr-bundle.crt', 'CURL_CA_BUNDLE': '/etc/ssl/ccr-bundle.crt',
    'GIT_SSL_CAINFO': '/etc/ssl/ccr-bundle.crt', 'CARGO_HTTP_CAINFO': '/etc/ssl/ccr-bundle.crt',
    'NODE_EXTRA_CA_CERTS': '/etc/ssl/ccr-bundle.crt', 'DENO_CERT': '/etc/ssl/ccr-bundle.crt',
    'JAVA_TOOL_OPTIONS': '"-Djavax.net.ssl.trustStore=/etc/ssl/ccr-java-cacerts '
                         '-Djavax.net.ssl.trustStorePassword=changeit -Dhttps.proxyHost=127.0.0.1 '
                         '-Dhttps.proxyPort=44357"',
}

def run(cmd, timeout=None, **kw):
    return subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, timeout=timeout, **kw)

def subst(s, args):
    def rep(m):
        name = m.group(1) or m.group(3)
        default = m.group(2)
        v = args.get(name)
        return v if v not in (None, '') else (default or '')
    return re.sub(r'\$\{(\w+)(?::?-([^}]*))?\}|\$(\w+)', rep, s)

def parse_froms(text):
    """Return [(line_index, image_token, resolved_image)] for external base images."""
    args, stages, out, seen_from = {}, set(), [], False
    for i, line in enumerate(text.splitlines()):
        m = re.match(r'^\s*ARG\s+(\w+)(?:=(.*))?\s*$', line, re.I)
        if m and not seen_from:
            args[m.group(1)] = (m.group(2) or '').strip().strip('"\'')
            continue
        m = re.match(r'^\s*FROM\s+(.+?)\s*$', line, re.I)
        if not m:
            continue
        seen_from = True
        toks = [t for t in m.group(1).split() if not t.startswith('--')]
        image = toks[0]
        alias = toks[2].lower() if len(toks) >= 3 and toks[1].lower() == 'as' else None
        resolved = subst(image, args)
        if resolved.lower() != 'scratch' and resolved.lower() not in stages:
            out.append((i, image, resolved))
        if alias:
            stages.add(alias)
    return out

def shim_tag(image):
    return 'ccrshim/' + re.sub(r'[^a-z0-9._-]+', '-', image.lower()).strip('-.')[:120] + ':s'

def ensure_shim(image, log):
    tag = shim_tag(image)
    if run(['docker', 'image', 'inspect', tag]).returncode == 0:
        return tag
    for attempt in range(4):
        r = run(['docker', 'pull', '-q', image], timeout=900)
        if r.returncode == 0:
            break
        log.write(f'[shim] pull {image} attempt {attempt+1} failed: {r.stdout[-300:]}\n')
        time.sleep(20 * (attempt + 1))
    else:
        raise RuntimeError(f'cannot pull base image {image}: {r.stdout[-300:]}')
    user = run(['docker', 'image', 'inspect', '-f', '{{.Config.User}}', image]).stdout.strip()
    env_lines = ''.join(f'ENV {k}={v}\n' for k, v in SHIM_ENV.items())
    copy = ('COPY ccr-ca-*.crt /usr/local/share/ca-certificates/\n'
            'COPY ccr-bundle.crt /etc/ssl/ccr-bundle.crt\n'
            'COPY ccr-java-cacerts /etc/ssl/ccr-java-cacerts\n')
    variants = [
        f'FROM {image}\nUSER root\n{copy}COPY ccr-shim.sh /usr/local/share/ccr-shim.sh\n'
        f'RUN sh /usr/local/share/ccr-shim.sh\n{env_lines}' + (f'USER {user}\n' if user else ''),
        f'FROM {image}\n{copy}{env_lines}',          # images without a shell (distroless etc.)
    ]
    for df in variants:
        with tempfile.NamedTemporaryFile('w', suffix='.Dockerfile', delete=False) as f:
            f.write(df)
        r = run(['docker', 'build', '-q', '-f', f.name, '-t', tag, SHIM_DIR], timeout=600)
        os.unlink(f.name)
        if r.returncode == 0:
            return tag
        log.write(f'[shim] variant failed for {image}: {r.stdout[-400:]}\n')
    raise RuntimeError(f'cannot shim base image {image}')

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--context', required=True)
    ap.add_argument('--dockerfile', required=True)
    ap.add_argument('--tag', required=True)
    ap.add_argument('--log', required=True)
    ap.add_argument('--timeout', type=int, default=1500)
    ap.add_argument('--no-shim', action='store_true')
    a = ap.parse_args()
    text = open(a.dockerfile, encoding='utf-8', errors='replace').read()
    res = {'tag': a.tag, 'ok': False, 'seconds': None, 'bases': [], 'error': None}
    t0 = time.time()
    with open(a.log, 'w') as log:
        try:
            dockerfile, cmd = a.dockerfile, ['docker', 'build', '--progress=plain', '-t', a.tag]
            tmp = None
            if not a.no_shim:
                lines = text.splitlines()
                for idx, token, resolved in parse_froms(text):
                    res['bases'].append(resolved)
                    lines[idx] = lines[idx].replace(token, ensure_shim(resolved, log), 1)
                tmp = tempfile.NamedTemporaryFile('w', suffix='.Dockerfile', delete=False)
                tmp.write('\n'.join(lines) + '\n'); tmp.close()
                dockerfile = tmp.name
                cmd += ['--network', 'host']
                for k in ('HTTPS_PROXY', 'https_proxy'):
                    cmd += ['--build-arg', f'{k}={PROXY}']
                for k in ('NO_PROXY', 'no_proxy'):
                    cmd += ['--build-arg', f'{k}={NO_PROXY}']
            else:
                res['bases'] = [r for _, _, r in parse_froms(text)]
            cmd += ['-f', dockerfile, a.context]
            log.write('[build] ' + ' '.join(cmd) + '\n'); log.flush()
            p = subprocess.run(cmd, stdout=log, stderr=subprocess.STDOUT, timeout=a.timeout)
            res['ok'] = p.returncode == 0
            if tmp: os.unlink(tmp.name)
        except subprocess.TimeoutExpired:
            res['error'] = f'timeout after {a.timeout}s'
        except Exception as e:
            res['error'] = str(e)[:500]
            log.write(f'[harness-error] {e}\n')
    res['seconds'] = round(time.time() - t0, 1)
    print(json.dumps(res))

if __name__ == '__main__':
    main()
