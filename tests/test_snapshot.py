import importlib.util
from pathlib import Path
import os
import subprocess
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tests'))
import test_template as fixtures
git, commit = fixtures.git, fixtures.commit
spec = importlib.util.spec_from_file_location('snapshot_update', ROOT / 'scripts/snapshot_update.py')
snapshot = importlib.util.module_from_spec(spec)
spec.loader.exec_module(snapshot)


import init_product


class SnapshotTests(unittest.TestCase):
    setUp = fixtures.TemplateTests.setUp

    def test_new_tree_without_source_ancestry(self):
        commit(self.dest, 'private/product.txt', 'product')
        commit(self.source, 'new.txt', 'upstream update')
        source_sha = git(self.source, 'rev-parse', 'HEAD')
        snapshot.prepare(str(self.source), 'main', 'review/source-update')
        self.assertEqual((self.dest / 'private/product.txt').read_text(), 'product')
        self.assertEqual((self.dest / 'new.txt').read_text(), 'upstream update')
        self.assertNotIn(source_sha, git(self.dest, 'rev-list', '--all'))

    def test_workflow_changes_stop_before_branch(self):
        commit(self.source, '.github/workflows/unsafe.yml', 'unsafe')
        with self.assertRaisesRegex(ValueError, 'manual review'):
            snapshot.prepare(str(self.source), 'main', 'review/source-update')
        self.assertEqual(git(self.dest, 'branch', '--show-current'), 'main')

    def test_unchanged_snapshot(self):
        snapshot.prepare(str(self.source), 'main', 'review/source-update')
        self.assertEqual(git(self.dest, 'branch', '--show-current'), 'main')

    def test_initial_import_is_one_root_with_exact_tree(self):
        empty = self.root / 'empty'
        empty.mkdir()
        git(empty, 'init', '-q')
        git(empty, 'config', 'user.name', 'Fixture')
        git(empty, 'config', 'user.email', 'fixture@example.invalid')
        os.chdir(empty)
        init_product.initialize(str(self.source), 'main')
        self.assertEqual(git(empty, 'rev-list', '--count', 'main'), '1')
        self.assertEqual(git(empty, 'rev-parse', 'main^{tree}'), git(self.source, 'rev-parse', 'main^{tree}'))
        with self.assertRaises(ValueError):
            init_product.initialize(str(self.source), 'main')
