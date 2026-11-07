# Security model and protection checklist

## Credentials and automation

Public CI uses only its repository-scoped `GITHUB_TOKEN` with `contents: read`. Checkout does not persist credentials. No PAT, deployment key, private remote, `pull_request_target`, reusable private workflow, source execution in a write-enabled job, self-hosted runner or private artifact is needed. The update example is inert until deliberately installed; its public source is fetched without credentials and it has no push step.

Private updates run in the private destination and read a public source anonymously. Human pushes use the operator's normal access to that destination. If a future automation truly needs writes, use a short-lived GitHub App installation token scoped only to that destination with Contents write and Pull requests write; never give a public workflow an installation/token covering private repositories. Keep administrative credential operations outside build/test jobs.

## Branch protections (configure separately per repo)

For `main` and public contribution branches, require pull requests, a second human reviewer, CODEOWNERS review, dismissal of stale approvals, approval of the latest push, resolved conversations, and passing named checks including `validate` in this template. Require the branch to be up to date; block force pushes and deletion; apply rules to administrators and minimize bypass lists. Update CODEOWNERS to actual independent reviewers: a single owner cannot approve their own PR. Protect `.github`, scripts, security policy, dependency manifests and license/asset approvals. Restrict who may change Actions settings and secrets.

Set default Actions permissions to read-only. Disable Actions creating/approving PRs; require approval for outside contributors, use GitHub-hosted disposable runners and pin actions to reviewed full SHAs. Enable push protection/secret scanning where supported. Do not allow private-repo Actions secrets to be sent to fork PRs. Keep workflows disabled in newly seeded products until each inherited workflow has been audited. Re-enable only reviewed workflows.

Branch protection availability depends on repository visibility and GitHub plan. Verify enforcement through the UI/API and an attempted blocked test push on a disposable branch; do not assume a documented setting exists on a private Free-plan repository. This template documents settings; it does not alter existing repositories or silently claim protections are enabled.

Sources: [GitHub fork model](https://docs.github.com/en/pull-requests/reference/forks), [Actions settings](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/enabling-features-for-your-repository/managing-github-actions-settings-for-a-repository), [protected branches](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches/about-protected-branches).

## Publication scan limits

`scan.py` scans committed blobs at every path across all reachable refs, including deleted files and renamed paths. It rejects common token/private-key patterns, sensitive directories, unapproved assets/binaries, unreviewed license file hashes and SPDX expressions. It prints finding categories and object prefixes, never blob contents. Submodules fail until separately audited. All policy changes require review. Hash approvals describe exact bytes, not permission to reuse modified assets.

This is a deliberately small heuristic gate, not a general secret detector or legal/license classifier. Unknown secret formats, text with no license markers, Unicode obfuscation, Git LFS pointer targets, external dependencies and unreachable Git objects need separate review. Fetch the intended public refs/history before scanning, never fetch private refs into a public checkout. Use a maintained secret scanner and dependency/license inventory for each real application. Locally inspect staged changes before committing and scan again before public push. GitHub CI runs too late to prevent initial disclosure.

## Incident handling

If a secret was published, revoke/rotate it immediately; deletion of a file or a later clean scan does not undo exposure. If private assets/code were published, freeze public pushes and inspect refs, releases, forks, Actions artifacts and caches with the owner. Coordinate history removal with GitHub support and consumers; do not force-push automatically. Review the original permissions and legal obligations before changing visibility. No script here performs destructive cleanup.
