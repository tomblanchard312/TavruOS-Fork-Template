# Migrate an existing product safely

1. Inventory existing repositories, upstream parent, visibility, license/notice requirements, default branches, tags, LFS, submodules, releases, workflow permissions, secrets and branch protections. Inspect metadata first; do not copy proprietary content into an inspection report destined for public GitHub.
2. Back up the existing private repository privately. Do not change its visibility. If the product is already public, assume its published history is public; this pattern cannot retroactively make it private. Handle exposed credentials/assets through the incident process first.
3. Create or choose a clean public fork of the actual upstream. Verify its parent and all proposed public refs. Never derive its initial history from a branded/private product mirror, even if you deleted private files at HEAD.
4. Create a new independent private destination, disable Actions, verify private visibility, and seed it with only the clean public branch as in setup. Preserve the existing private product repository unchanged until migration is accepted.
5. Work inside the private boundary to replay the product changes on a private review branch. Review merge bases and conflicts; if histories diverged or were squashed, port the changes deliberately. Preserve upstream attribution, notices and product history in a private archive as required. Do not force a public history rewrite to simplify migration.
6. Install reviewed tooling, adapt private CI without public-only publication checks, audit imported workflows and rotate narrowly scoped credentials as needed. Compare the resulting product tree with the old version and run its actual tests/build/install checks. Record unresolved platform tests.
7. Enable protections and reviewed CI, verify enforcement and access, and switch releases only after product acceptance. Keep rollback as the unchanged previous private repository/release. Promote future generic fixes through fresh public-only clones.

No bulk migration or visibility changes are performed by this template. Existing public forks and private products are examples of the topology, not automatically approved migration inputs.
