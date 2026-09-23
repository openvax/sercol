# Release sercol 1.0.2: compatible dependency metadata

## Specification

Complete and release existing PR #5 for issue #4. Keep its compatible
`serializable>=1.0.0,<2.0.0` bound and serialization regression tests, and
remove the unused direct simplejson requirement. Serializable owns its own
JSON dependency. Preserve the existing pandas range and collection behavior.
Bump the current source version 1.0.1 to 1.0.2; PyPI currently has 1.0.0.

The current PR has a failed Coveralls upload despite passing installation,
lint, and tests. File this workflow defect and coordinate the matrix uploads
using Coveralls' documented parallel flags and a single finalization job.
Keep coverage failures visible and preserve the existing test matrix.

Validate both the supported serializable 1.0.0 floor and the current local
development checkout, including actual package resolution with current
varcode. Inspect built wheel and sdist dependency metadata, review the final
diff, and require green CI before merging. Deploy using the repository script
from clean master, then verify downloaded PyPI artifacts against local builds.

## Plan

- [x] Inspect the issue, existing PR, source dependencies, and CI failure.
- [x] Record the CI defect (#6) and complete the version/workflow changes.
- [x] Run lint and tests with serializable 1.0.0 and current development sources.
- [x] Verify clean dependency resolution and wheel/sdist metadata.
- [ ] Review the complete diff, update PR #5, and verify CI.
- [ ] Merge, deploy 1.0.2 from clean master, and record publication verification
      on PR #5 after the release occurs.

## Review

The dependency and three regression-test changes originated in PR #5; this
release preserves that work instead of creating a competing fix. The shared
sercol checkout remains on master while preparation uses an isolated worktree.

All eight tests pass with both serializable 1.0.0 and the remote-verified
local development checkout of 1.1.0 (19c38ce). Lint passes and `pip check`
reports no broken requirements. Reproduced the old source-install conflict;
the corrected source resolves together with current local serializable,
varcode, pyensembl, datacache, and gtfparse without overriding dependency bounds.

Both built distributions identify version 1.0.2 and declare exactly
`serializable>=1.0.0,<2.0.0` and `pandas>=2.0.0,<3.0.0`; no direct simplejson
requirement remains. Twine metadata checks pass. The pinned Coveralls action
supports both parallel upload and finalization inputs. The final workflow
preserves Python 3.9–3.11 and keeps upload failures visible.
