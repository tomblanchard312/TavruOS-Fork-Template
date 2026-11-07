# Promote generic fixes manually

1. In the private environment, identify a small upstream-compatible fix. Reimplement it against the clean public baseline if it depends on private APIs. Confirm authorship and permission to publish.
2. Create a plain diff for explicitly selected source/test paths, for example `git diff BASE FIX -- src/generic.rs tests/generic.rs > /tmp/generic.patch`. Never use `format-patch`, a private branch, a bundle, a mirror, or a whole-tree diff. Private commit messages and ancestry must stay private.
3. Inspect the entire patch locally: context lines, filenames, new files, comments, URLs, identifiers, tests, secrets, binary content, icons and licenses. Remove every private reference; reject binary patches. The patch itself is private until cleared. Never upload it as a public artifact for review.
4. In an isolated location, run the template's trusted script:

```sh
python3 /path/to/template/scripts/promote.py YOUR_OWNER/CLEAN_PUBLIC_FORK main /tmp/generic.patch /tmp/public-generic-review
```

5. Inspect `git diff` and `git status --short` in that new clone. The script applies without staging and never commits or pushes. It imports no private commit objects. It is not a sanitizer: the human review in step 3 is mandatory.
6. Run the public application's tests without any private credentials. Stage only the reviewed paths and create a new generic commit with a new public-safe message. Run this template's scanner against that checkout using its reviewed public policy, and a maintained secret scanner. Review policy exceptions and upstream license obligations.
7. Verify `git remote -v`, then manually push only `HEAD:refs/heads/contribution/generic-fix` to the clean public fork. Open a PR for review against upstream. Disable maintainer edits if that is your contribution policy. Never enable auto-promotion.

The fresh clone is the history boundary. It is not permission to publish whatever a patch contains. No public workflow ever fetches a private repo or receives a private token.
