# Setup

## Two independent repositories, with shared upstream history

Do not generate an empty template repository and merge unrelated upstream history into it. This is a tooling template, not the application's history. GitHub does not let you make a public fork private; create an independent private product repository instead.

```sh
gh repo fork UPSTREAM_OWNER/PROJECT --clone=false
# Confirm the actual fork name first; it is normally PROJECT.
gh repo view YOUR_OWNER/PROJECT --json nameWithOwner,visibility,isFork,parent
# Disable inherited workflows before cloning or importing code.
gh api --method PUT repos/YOUR_OWNER/PROJECT/actions/permissions -F enabled=false
git clone https://github.com/YOUR_OWNER/PROJECT.git public-work
# Never add a private remote to public-work.
gh repo create YOUR_OWNER/PRODUCT --private --disable-wiki
# Confirm PRIVATE before the first push:
gh repo view YOUR_OWNER/PRODUCT --json nameWithOwner,visibility
gh api --method PUT repos/YOUR_OWNER/PRODUCT/actions/permissions -F enabled=false
# This starts from PUBLIC history only, not a mirror of a proprietary repository.
git clone https://github.com/YOUR_OWNER/PROJECT.git product-work
git -C product-work remote set-url origin https://github.com/YOUR_OWNER/PRODUCT.git
git -C product-work push -u origin HEAD:main
```

Replace placeholders explicitly. Do not use `--mirror`, `push --all`, or `push --tags`. Do not initialize the private destination with a README: preserve common ancestry. Disable Actions in each new repository before its first push. Audit workflows already inherited by the public fork; a fork can include upstream automation unrelated to this pattern.

Copy `scripts/`, `tests/`, `publication-policy.json`, and the desired workflow from this template into a review branch in each repository, preserving application files and licenses. If any path collides, integrate manually. Keep existing CODEOWNERS entries and add real security reviewers. Adapt tests and policy for the upstream baseline rather than deleting upstream content just to pass a scan.

The strict default policy needs explicit asset and license approvals. Review the source and terms, record why a hash was approved in the PR, then add its `sha256sum` to the appropriate policy list. SPDX expressions are exact reviewed values. Review upstream license/dependency compatibility at setup and every license change. Notice exceptions apply only to the restricted-notice heuristic, never to secret checks. Do not approve a restricted license merely to make CI green.

In private products, retain the public publication policy unchanged; it is intended for public candidates, and correctly rejects private paths. Configure private product CI to run application checks and a dedicated secret scanner without demanding that private assets pass a public publication gate. Keep this template's full validation in the public fork or tooling repository. Never put private hashes, paths or inventory in a public policy.

## Update process

Start on the current destination default branch with a clean working tree. Run `update.py` with role `public` for upstream → public fork, or `private` for public fork → private product. Only GitHub repositories confirmed public through the unauthenticated metadata API are accepted. No private access token is needed to fetch. Repository names/ref values are passed as arguments, not evaluated as shell code.

The result is a new local `review/...` branch. Public updates must fast-forward; private updates preserve product commits with a merge. Unrelated history or incoming `.github` changes stop before creating the branch. A conflict leaves the review branch available for inspection; run `git merge --abort` to abandon that merge. Existing main stays unchanged.

Inspect the exact changes, licensing, and any build scripts. Resolve conflicts on the review branch and run the application's tests in a credential-free environment. Review incoming CI separately before merging it. For public candidates, also commit the candidate locally and run `python3 scripts/scan.py` with all relevant history fetched. Stage/commit review is essential: the scanner reads committed reachable history, not untracked or uncommitted files.

Only after local review:

```sh
git remote -v  # check destination, especially before public publication
git push origin HEAD:refs/heads/review/source-update
gh pr create --base main --head review/source-update
```

Keep private PR logs and artifacts private. Never upload private merge reports to the public fork. Recheck branch protection before merging. Do not auto-merge imported code.

The example manual update workflow has no write permission and publishes no artifact; it only checks preparation in an ephemeral runner. Repeat preparation locally to create the PR. Automation that later pushes requires a separate audited design; this template intentionally uses no PAT or cross-repository secret.
