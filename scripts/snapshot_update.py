#!/usr/bin/env python3
"""Import a public tree as a new private snapshot; never push upstream ancestry."""
import argparse
import subprocess

from update import git, public_source


def prepare(url, ref, branch):
    if git('status', '--porcelain'):
        raise ValueError('Working tree must be clean')
    if not branch.startswith('review/') or not branch.endswith('-update'):
        raise ValueError('Use review/name-update')
    git('check-ref-format', 'refs/heads/' + branch)
    git('check-ref-format', 'refs/heads/' + ref)
    local = 'refs/heads/vendor/public-snapshot'
    try:
        baseline = git('rev-parse', '--verify', local)
        expected = baseline
    except subprocess.CalledProcessError:
        baseline = git('rev-parse', '--verify', 'refs/remotes/origin/vendor/public-snapshot')
        expected = '0' * 40
    git('merge-base', '--is-ancestor', baseline, 'HEAD')
    # Depth one downloads the current source only, not its historical commits.
    git('-c', 'credential.helper=', 'fetch', '--depth=1', '--no-tags', '--no-recurse-submodules', url, 'refs/heads/' + ref)
    source = git('rev-parse', 'FETCH_HEAD')
    if git('diff', '--name-only', baseline, source, '--', '.github'):
        raise ValueError('Incoming .github changes require manual review and quarantine')
    if git('rev-parse', baseline + '^{tree}') == git('rev-parse', source + '^{tree}'):
        print('Public snapshot is unchanged; nothing to import')
        return
    git('switch', '-c', branch)
    message = 'Import public source snapshot ' + source + '\n\nSource: ' + url + '\n'
    incoming = subprocess.check_output(['git', 'commit-tree', source + '^{tree}', '-p', baseline], input=message.encode()).decode().strip()
    # The only parent is OUR previous snapshot, never the source commit.
    try:
        git('-c', 'core.hooksPath=/dev/null', 'merge', '--no-ff', '--no-edit', incoming)
    except subprocess.CalledProcessError:
        print('Resolve on the review branch, then merge; or git merge --abort. Snapshot baseline was not advanced.')
        raise
    git('update-ref', local, incoming, expected)
    print('Review and test locally. Push ONLY the private review branch; advance the private vendor baseline after acceptance. Nothing pushed.')


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('source', help='public owner/repository')
    p.add_argument('ref')
    p.add_argument('branch', help='review/name-update')
    a = p.parse_args()
    prepare(public_source(a.source), a.ref, a.branch)
