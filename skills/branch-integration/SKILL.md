---
name: branch-integration
description: >-
  Closes a completed development branch by checking the final diff and proof,
  presenting merge, pull-request, keep, or discard options, and cleaning up
  only after the user or repository workflow chooses a path. Use when feature
  work is complete and the branch must be integrated or retired. Not for
  claiming a feature is complete before verification.
---

# Branch Integration

Finishing is a decision gate, not an automatic merge.

## Final inspection

1. Run `git status` and inspect the full diff from the intended base.
2. Check for untracked files, generated artifacts, secrets, unrelated edits,
   and migration or release notes that belong in the branch.
3. Run the relevant focused and broad checks with fresh output.
4. Summarize the behavior, evidence, limits, and known follow-ups.

Use `completion-verification`; a green suite alone does not choose the
integration path.

## Present explicit options

- **Merge locally:** integrate into the target branch after review.
- **Open a pull request:** preserve the branch for collaborative review.
- **Keep the branch:** leave it available for later work.
- **Discard:** delete only after confirming no unique work remains.

Do not push, merge, delete a branch, or remove a worktree unless the user or
the repository's explicit automation authorizes that action. If checks are
blocked, present the blocked state instead of hiding it in a success summary.

## Completion condition

The chosen integration path is recorded, the final diff and evidence match the
scope, and cleanup is either performed safely or intentionally deferred.
