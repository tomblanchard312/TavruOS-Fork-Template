import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import scan
import update
import promote


def git(cwd, *args):
    return subprocess.check_output(['git', '-C', str(cwd), *args], stderr=subprocess.STDOUT).decode().strip()


def commit(repo, path, content):
    target = repo / path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content)
    git(repo, 'add', '.')
    git(repo, 'commit', '-qm', 'fixture')


class TemplateTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.source = self.root / 'source'
        self.source.mkdir()
        git(self.source, 'init', '-q', '-b', 'main')
        git(self.source, 'config', 'user.name', 'Fixture')
        git(self.source, 'config', 'user.email', 'fixture@example.invalid')
        commit(self.source, 'base.txt', 'base\n')
        self.dest = self.root / 'dest'
        subprocess.run(['git', 'clone', '-q', str(self.source), str(self.dest)], check=True)
        git(self.dest, 'config', 'user.name', 'Fixture')
        git(self.dest, 'config', 'user.email', 'fixture@example.invalid')
        self.previous = Path.cwd()
        os.chdir(self.dest)
        self.addCleanup(os.chdir, self.previous)

    def test_public_fast_forward(self):
        commit(self.source, 'new.txt', 'update\n')
        update.prepare(str(self.source), 'main', 'public', 'review/update')
        self.assertEqual(git(self.dest, 'rev-parse', 'HEAD'), git(self.source, 'rev-parse', 'HEAD'))
        self.assertEqual(git(self.dest, 'rev-parse', 'main'), git(self.source, 'rev-parse', 'HEAD~1'))

    def test_public_rejects_divergence(self):
        commit(self.dest, 'local.txt', 'local\n')
        commit(self.source, 'new.txt', 'update\n')
        with self.assertRaises(subprocess.CalledProcessError):
            update.prepare(str(self.source), 'main', 'public', 'review/update')
        self.assertEqual(git(self.dest, 'branch', '--show-current'), 'main')

    def test_private_preserves_changes(self):
        commit(self.dest, 'private/product.txt', 'product\n')
        commit(self.source, 'new.txt', 'update\n')
        update.prepare(str(self.source), 'main', 'private', 'review/update')
        self.assertTrue((self.dest / 'private/product.txt').exists())
        self.assertTrue((self.dest / 'new.txt').exists())
        self.assertEqual(len(git(self.dest, 'rev-list', '--parents', '-n', '1', 'HEAD').split()), 3)

    def test_rejects_workflows(self):
        commit(self.source, '.github/workflows/unsafe.yml', 'name: unsafe\n')
        with self.assertRaisesRegex(ValueError, '.github'):
            update.prepare(str(self.source), 'main', 'private', 'review/update')

    def test_rejects_dirty_tree(self):
        (self.dest / 'dirty').write_text('dirty')
        with self.assertRaisesRegex(ValueError, 'clean'):
            update.prepare(str(self.source), 'main', 'public', 'review/update')

    def test_rejects_unrelated(self):
        git(self.source, 'checkout', '--orphan', 'other')
        git(self.source, 'rm', '-rf', '.')
        commit(self.source, 'other.txt', 'other\n')
        with self.assertRaises(subprocess.CalledProcessError):
            update.prepare(str(self.source), 'other', 'private', 'review/update')

    def test_conflict_preserves_main(self):
        base = git(self.dest, 'rev-parse', 'main')
        commit(self.dest, 'base.txt', 'private edit\n')
        private = git(self.dest, 'rev-parse', 'main')
        commit(self.source, 'base.txt', 'upstream edit\n')
        with self.assertRaises(subprocess.CalledProcessError):
            update.prepare(str(self.source), 'main', 'private', 'review/conflict')
        self.assertEqual(git(self.dest, 'rev-parse', 'main'), private)
        git(self.dest, 'merge', '--abort')
        self.assertNotEqual(base, private)

    def test_source_validation(self):
        with self.assertRaises(ValueError):
            update.public_source('https://example.invalid/private')
        class Response:
            def __enter__(self): return self
            def __exit__(self, *args): pass
            def read(self): return b'{"private":true,"visibility":"private"}'
        with patch('urllib.request.urlopen', return_value=Response()):
            with self.assertRaises(ValueError): update.public_source('owner/repo')

    def test_scanner(self):
        policy = json.loads((ROOT / 'publication-policy.json').read_text())
        self.assertTrue(scan.violations('private/code.rs', b'hello', policy))
        self.assertTrue(scan.violations('logo.svg', b'<svg/>', policy))
        self.assertTrue(scan.violations('LICENSE', b'Unreviewed terms', policy))
        self.assertTrue(scan.violations('x', ('ghp_' + 'A' * 30).encode(), policy))
        self.assertTrue(scan.violations('x', b'SPDX-License-Identifier: Unknown', policy))
        self.assertFalse(scan.violations('x.rs', b'// SPDX-License-Identifier: MIT', policy))

    def test_deleted_secret_and_renamed_path(self):
        policy = json.loads((ROOT / 'publication-policy.json').read_text())
        commit(self.dest, 'bad.txt', 'ghp_' + 'A' * 30)
        git(self.dest, 'rm', 'bad.txt')
        git(self.dest, 'commit', '-qm', 'remove')
        git(self.dest, 'mv', 'base.txt', 'secrets')
        git(self.dest, 'commit', '-qm', 'rename')
        errors = scan.scan(policy)
        self.assertTrue(any('possible secret' in e for e in errors))
        self.assertTrue(any('private path' in e for e in errors))

    def test_promotion_has_no_private_ancestry(self):
        commit(self.dest, 'private/product.txt', 'private implementation\n')
        private_commit = git(self.dest, 'rev-parse', 'HEAD')
        commit(self.dest, 'base.txt', 'generic fix\n')
        diff = git(self.dest, 'diff', 'HEAD~1', 'HEAD', '--', 'base.txt') + '\n'
        patchfile = self.root / 'sanitized.patch'
        patchfile.write_text(diff)
        clean = self.root / 'clean'
        with patch.object(promote, 'public_source', return_value=str(self.source)):
            promote.promote('owner/repo', 'main', patchfile, clean)
        self.assertEqual((clean / 'base.txt').read_text(), 'generic fix\n')
        self.assertFalse((clean / 'private').exists())
        self.assertNotIn(private_commit, git(clean, 'rev-list', '--all'))
        with self.assertRaises(ValueError):
            promote.promote('owner/repo', 'main', patchfile, clean)


if __name__ == '__main__': unittest.main()
