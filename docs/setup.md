# Setup: no upstream history in private products

**Rule: import public source snapshots, never upstream commit ancestry, into private product repositories.** Preserve licenses, attribution and notices. GitHub-native public tracking forks necessarily retain upstream history; the rule governs independent private products. Never seed products with a clone-and-push, mirror, bundle or upstream history merge.

## Public tracking fork

Create or reuse the clean public GitHub fork. Keep private remotes and credentials out. `update.py public` prepares fast-forward-only review branches without pushing. Do not change existing forks unless explicitly authorized.

## Private product initialization

Create the private destination, verify visibility, and disable Actions before importing:

```sh
gh repo create YOUR_OWNER/PRODUCT --private --disable-wiki
gh api --method PUT repos/YOUR_OWNER/PRODUCT/actions/permissions -F enabled=false
gh repo view YOUR_OWNER/PRODUCT --json visibility
mkdir product-work
cd product-work
git init -b main
python3 /path/to/template/scripts/init_product.py YOUR_OWNER/PUBLIC_FORK main
git remote add origin https://github.com/YOUR_OWNER/PRODUCT.git
```

The initializer requires an empty checkout, fetches depth one and creates a new root from the exact source tree, with no upstream parents. It also creates `vendor/public-snapshot`. The source commit remains local in FETCH_HEAD; never push FETCH_HEAD, tags, all refs or a mirror. A shallow clone alone is not a safe product import.

With Actions still disabled, quarantine inherited workflow YAML outside `.github/workflows`. Preserve source notices and licensing. Copy this template's scripts, tests, policy, docs and MIT license into an isolated folder such as `.tavru/fork-template`, preserving application scripts/tests/README. Adapt private CODEOWNERS to authorized reviewers. Install only reviewed workflows with read-only permissions, pinned checkout and no persisted credentials. Run imported application code without publication credentials.

Before product setup commits, verify `git rev-list --count main` equals 1 and `git rev-list --parents -n 1 vendor/public-snapshot` has no parent. Compare the root tree against the source. Add setup changes in a separate product commit; verify the private remote and push only `main` and `vendor/public-snapshot` explicitly. Re-enable Actions only after auditing every active workflow. Configure protections and verify private-plan support separately.

## Snapshot updates

From current private main with a clean checkout and private origin fetched:

```sh
python3 /path/to/template/scripts/update.py private YOUR_OWNER/PUBLIC_FORK main review/public-update
```

Private mode always uses `snapshot_update.py`. It fetches depth one, rejects incoming `.github` changes for separate security review, and creates a snapshot commit whose only parent is the previous private snapshot. It merges that snapshot onto a new review branch, preserving product changes. It never pushes. Source ancestry never becomes product ancestry.

A conflict remains on the review branch; resolve or `git merge --abort`. The snapshot baseline is unchanged after failure. After successful preparation, review/test and push only the private review branch for a PR. After accepting it into private main, push the local `vendor/public-snapshot` branch to private origin. Do not begin another import while one is pending. If abandoning successful preparation, reset the local baseline to `origin/vendor/public-snapshot` before retrying. Fresh clones use the remote baseline if there is no local one.

The inert workflow example only prepares an ephemeral candidate. No workflow pushes or uploads private artifacts. Imported workflows require manual review and quarantine.

## Publication gates

Keep the public publication policy strict; it is not a private-product CI gate. Use maintained private secret scanning and application-specific tests separately. Never put private inventories into public policies. For public candidates, commit and scan locally before pushing: CI is too late to prevent initial disclosure. The scanner checks reachable committed history, not untracked/staged-only data. Review asset and license terms before approving exact hashes or SPDX expressions; hashes are not publication permission. See security and promotion docs for limits.
