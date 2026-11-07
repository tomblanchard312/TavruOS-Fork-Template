#!/usr/bin/env python3
"""Apply a manually sanitized patch in an isolated public-only checkout. No pushes."""
import argparse
import subprocess
from pathlib import Path
from update import git, public_source


def promote(source, ref, patch, destination):
    destination = Path(destination)
    if destination.exists():
        raise ValueError('Destination must not exist; never reuse a private checkout')
    url = public_source(source)
    subprocess.run(['git', '-c', 'credential.helper=', 'clone', '--single-branch', '--no-tags',
                    '--branch', ref, '--', url, str(destination)], check=True)
    subprocess.run(['git', '-C', str(destination), 'switch', '-c', 'contribution/generic-fix'], check=True)
    # git apply imports file changes, never private commit parents, authors or messages.
    subprocess.run(['git', '-C', str(destination), 'apply', '--check', str(Path(patch).resolve())], check=True)
    subprocess.run(['git', '-C', str(destination), 'apply', str(Path(patch).resolve())], check=True)
    print('Review every changed line and new file; run public checks before committing. Nothing was pushed.')


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('source')
    p.add_argument('ref')
    p.add_argument('patch', help='manually sanitized plain git diff, never format-patch')
    p.add_argument('destination')
    a = p.parse_args()
    promote(a.source, a.ref, a.patch, a.destination)
