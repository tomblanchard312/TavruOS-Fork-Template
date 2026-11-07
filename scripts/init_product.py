#!/usr/bin/env python3
"""Seed an EMPTY checkout with one public tree and zero upstream parents."""
import argparse
from pathlib import Path
import subprocess
from update import git, public_source


def initialize(url, ref):
    if set(p.name for p in Path.cwd().iterdir()) != {'.git'} or git('for-each-ref'):
        raise ValueError('Run only in an empty git init checkout containing .git alone')
    git('check-ref-format', 'refs/heads/' + ref)
    git('-c', 'credential.helper=', 'fetch', '--depth=1', '--no-tags', '--no-recurse-submodules', url, 'refs/heads/' + ref)
    source = git('rev-parse', 'FETCH_HEAD')
    commit = subprocess.check_output(['git', 'commit-tree', source + '^{tree}'],
        input=('Import public snapshot ' + source + '\n\nSource: ' + url + '\n').encode()).decode().strip()
    git('update-ref', 'refs/heads/main', commit)
    git('update-ref', 'refs/heads/vendor/public-snapshot', commit)
    git('symbolic-ref', 'HEAD', 'refs/heads/main')
    git('-c', 'core.hooksPath=/dev/null', 'reset', '--hard', 'main')
    print('Snapshot initialized without upstream parents. Keep Actions disabled; audit inherited workflows before pushing.')


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('source', help='public GitHub owner/repository')
    p.add_argument('ref')
    a = p.parse_args()
    initialize(public_source(a.source), a.ref)
