# TavruOS Fork Template

Reusable tools and operating instructions for a clean public upstream fork and a separate private product repository.

```text
upstream (public) → clean fork (public) → product (private)
                         ↑
            manually reviewed generic patch
            applied in a fresh public-only clone
```

The public fork contains only upstream-compatible code. Product integration, private icons, credentials, and restricted assets belong in the separate private repository. No public automation can read or write a private product repo. Neither script pushes anything, changes repository visibility, force-pushes, or rewrites existing branches.

**Rule: no upstream commit history in private forked products.** Initialize with `init_product.py`; private `update.py` mode imports later snapshots. Public GitHub-native tracking forks retain their ancestry. Preserve source licenses and attribution.

## Start here

1. Follow [setup](docs/setup.md) to fork upstream and create an independent private repository using a source snapshot without upstream history.
2. Use [the update script](scripts/update.py) to prepare a new local review branch; test and merge through a pull request.
3. Use [the promotion procedure](docs/promotion.md) for generic fixes. Never merge or cherry-pick a private branch into a public checkout.
4. Configure [protections and credentials](docs/security.md) before enabling automation.
5. For existing products, follow [migration](docs/migration.md). This template does not migrate repositories automatically.

Requires Git, Python 3.10+, and GitHub CLI for setup and PRs. The scripts have no third-party Python dependencies. Run from the destination checkout:

```sh
python3 scripts/update.py public UPSTREAM_OWNER/PROJECT main review/upstream-update
# In a separate PRIVATE product checkout:
python3 scripts/update.py private YOUR_OWNER/CLEAN_PUBLIC_FORK main review/fork-update
python3 -m unittest discover -s tests -v
python3 scripts/scan.py
```

An incoming `.github` change stops the update for manual review. Scripts never run upstream builds, hooks or submodules. Perform build tests separately with no publication credentials available. Local Git configuration, filters, merge drivers and hooks are part of your trusted environment; use isolated checkouts and inspect them before imports.

## Included

- Snapshot-only private initialization and updates, with no upstream commit parents.
- Public-only source verification, public fast-forward-only sync, and private snapshot merge review branches.
- Fresh-clone patch promotion without importing private Git objects.
- Read-only, pinned-checkout GitHub Actions validation. An inert manual update workflow example is under `examples/`.
- Full reachable-history secret heuristics, blocked-path checks, asset hash approvals, and license notice/SPDX review gates.
- Integration tests for the boundaries and failure cases.

The scan is a supplemental publication gate, not proof that content is safe. It does not discover every secret, identify ownership of arbitrary source, or establish license compatibility. Audit content, history, dependencies, LFS objects, submodules, releases and attachments separately. A failed public CI scan happens **after upload**: scan locally before any public push. See [security](docs/security.md).

Template code uses [MIT](LICENSE). Upstream code and assets retain their own terms. Private hosting does not remove obligations attached to distributing open-source derivatives.
