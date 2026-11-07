#!/usr/bin/env python3
"""Prepare a local review branch from a verified public GitHub source. Never push."""
import argparse
import json
import re
import subprocess
import urllib.request


def git(*args):
    return subprocess.check_output(['git', *args], stderr=subprocess.STDOUT).decode().strip()


def public_source(repo):
    if not re.fullmatch(r'[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+', repo):
        raise ValueError('Expected GitHub owner/repository')
    with urllib.request.urlopen('https://api.github.com/repos/' + repo, timeout=30) as response:
        metadata = json.load(response)
    if metadata.get('private') is not False or metadata.get('visibility') != 'public':
        raise ValueError('Source must be public')
    return 'https://github.com/' + repo + '.git'


def prepare(url, ref, role, branch):
    if role == 'private':
        from snapshot_update import prepare as snapshot_prepare
        return snapshot_prepare(url, ref, branch)
    if git('status', '--porcelain'):
        raise ValueError('Working tree must be clean')
    if not re.fullmatch(r'review/[A-Za-z0-9_-]+', branch):
        raise ValueError('Use a new review/name branch')
    git('check-ref-format', 'refs/heads/' + ref)
    base = git('rev-parse', 'HEAD')
    git('-c', 'credential.helper=', 'fetch', '--no-tags', '--no-recurse-submodules', url, 'refs/heads/' + ref)
    incoming = git('rev-parse', 'FETCH_HEAD')
    git('merge-base', base, incoming)  # refuse unrelated histories
    if role == 'public':
        git('merge-base', '--is-ancestor', base, incoming)  # refuse divergent public history
    # Imported workflows must be audited separately before they can receive a token.
    if git('diff', '--name-only', base + '...' + incoming, '--', '.github'):
        raise ValueError('Incoming .github changes require separate manual security review')
    git('switch', '-c', branch)
    try:
        git('-c', 'core.hooksPath=/dev/null', 'merge', '--ff-only' if role == 'public' else '--no-ff', '--no-edit', incoming)
    except subprocess.CalledProcessError:
        print('Merge failed; resolve only on the review branch, or git merge --abort.')
        raise
    print('Prepared local review branch. Inspect, test, scan, then manually push ONLY to this repository.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('role', choices=['public', 'private'])
    parser.add_argument('source', help='public GitHub owner/repo: upstream for public role, clean fork for private role')
    parser.add_argument('ref')
    parser.add_argument('branch', help='new review/name branch')
    args = parser.parse_args()
    prepare(public_source(args.source), args.ref, args.role, args.branch)
