#!/usr/bin/env python3
"""Fail-closed publication gate over every reachable Git blob; never print contents."""
import hashlib
import json
import re
import subprocess
import sys
from pathlib import PurePosixPath


def git(*args):
    return subprocess.check_output(['git', *args])


def violations(path, data, policy):
    issues = []
    parts = PurePosixPath(path.lower()).parts
    if any(p in policy['blocked_components'] for p in parts) or PurePosixPath(path).name.lower().startswith('.env'):
        issues.append('private path')
    if len(data) > 2_000_000 or b'\0' in data or PurePosixPath(path).suffix.lower() in policy['asset_extensions']:
        if hashlib.sha256(data).hexdigest() not in policy['approved_asset_sha256']:
            issues.append('unapproved asset/binary/large blob')
    text = data.decode('utf-8', errors='replace')
    patterns = [r'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----',
                r'gh[pousr]_[A-Za-z0-9]{20,}', r'github_pat_[A-Za-z0-9_]{20,}',
                r'AKIA[0-9A-Z]{16}',
                r'(?i)(?:password|api[_-]?key|client[_-]?secret)\s*[:=]\s*["\x27][^"\x27\s]{12,}["\x27]']
    if any(re.search(pattern, text) for pattern in patterns):
        issues.append('possible secret')
    if re.search(r'(?i)all rights reserved|confidential|proprietary', text) and path not in policy['notice_exceptions']:
        issues.append('restricted notice')
    if PurePosixPath(path).name.upper().startswith(('LICENSE', 'COPYING', 'NOTICE')):
        if hashlib.sha256(data).hexdigest() not in policy['approved_license_sha256']:
            issues.append('license text needs review')
    for expression in re.findall(r'(?m)^\s*(?://|#|/\*|\*|--)?\s*SPDX-License-Identifier:[ \t]*([^\r\n]+)', text):
        if expression.strip() not in policy['allowed_spdx_expressions']:
            issues.append('unreviewed SPDX expression')
    return issues


def scan(policy):
    errors = []
    # Check each historical path, including renames of an already-seen blob.
    seen = set()
    for commit in git('rev-list', '--all').splitlines():
        for row in git('ls-tree', '-rz', '--full-tree', commit.decode()).split(b'\0'):
            if not row:
                continue
            metadata, rawpath = row.split(b'\t', 1)
            mode, kind, oid = metadata.split()
            if kind != b'blob':
                errors.append('submodule requires separate publication audit')
                continue
            if (oid, rawpath) in seen:
                continue
            seen.add((oid, rawpath))
            path = rawpath.decode('utf-8', errors='replace')
            for issue in violations(path, git('cat-file', 'blob', oid.decode()), policy):
                errors.append(f'{oid.decode()[:12]}: {issue}')
    return errors


if __name__ == '__main__':
    policy = json.load(open(sys.argv[1] if len(sys.argv) > 1 else 'publication-policy.json'))
    errors = scan(policy)
    print('\n'.join(errors) if errors else 'Publication policy scan passed')
    sys.exit(bool(errors))
