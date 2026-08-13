---
name: using-git-worktrees
description: >-
  Creates and manages isolated Git worktrees for parallel agents, risky
  experiments, or long-running feature work while preserving the user's
  current checkout. Use before concurrent branch edits or when isolation makes
  rollback safer. Not for a trivial one-file change that is already isolated.
---

# Using Git Worktrees

Isolation is a safety boundary, not a way to hide unreviewed changes.

## Before creating one

1. Inspect `git status`, current branch, repository root, and existing
   worktrees.
2. Preserve uncommitted user work; never reset, checkout, or clean it away.
3. Choose an explicit branch name and a worktree path outside the main working
   tree when practical.
4. Confirm the base ref and whether ignored/generated files are needed.

## Create safely

```bash
git worktree list
git worktree add ../<repo>-<task> -b <task-branch> <base-ref>
```

Run repository setup in the new worktree, record the exact base commit, and
keep secrets and local environment files out of the branch. Do not use the same
worktree for two writers.

## Finish or discard

- Review and test the branch before integrating it.
- Merge or cherry-pick only the intended commits after checking the diff.
- Remove a disposable worktree only after confirming its commits and needed
  artifacts are preserved:

```bash
git worktree remove ../<repo>-<task>
git worktree prune
```

Do not force removal when it contains unreviewed work. If a worktree is stale,
inspect its branch and status before deciding whether it is recoverable.

## Completion condition

The branch's base, ownership, integration path, and cleanup decision are
explicit; the main checkout remains intact.
