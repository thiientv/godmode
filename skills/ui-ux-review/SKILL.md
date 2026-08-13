---
name: ui-ux-review
description: >-
  Audits an existing rendered interface or frontend diff for hierarchy,
  content clarity, interaction states, accessibility, responsive behavior,
  visual consistency, performance-sensitive UI patterns, and anti-generic
  design defects. Use for a UI/UX review, redesign audit, screenshot review,
  pre-release visual check, or design-system consistency pass. Not for building
  a new interface from scratch or for backend-only review.
---

# UI/UX Review

Review the interface users actually receive, not only the component source.

## Establish the surface

1. Identify routes, primary flows, target users, supported viewports, themes,
   content states, and the design system or brand constraints.
2. Inspect the diff and direct consumers before forming findings.
3. Run the deterministic audit helper against relevant HTML/CSS/JS when a
   static surface is available:

   ```bash
   python3 skills/ui-ux-review/scripts/audit_ui.py ./path/to/ui
   ```

   Zero supported source files is inconclusive and exits with status 2. Use
   `--allow-empty` only when an empty UI scope is intentional; it is not proof
   that a surface is clean.

4. Extract the current token and component system with `frontend-design` when
   consistency claims depend on it; compare against existing tokens before
   proposing a redesign language.
5. Render the surface in a browser. Capture normal, empty, error, loading,
   permission, narrow, intermediate, and desktop states that matter to the
   request. If runtime access is blocked, mark visual findings unverified.

## Review passes

### Experience and hierarchy

Check whether the first viewport explains the page, the primary action is
obvious, copy is scannable, labels are specific, and repeated containers add
meaning rather than noise.

### Interaction and accessibility

Check semantics, names, keyboard order, focus visibility, contrast, target
size, error recovery, reduced motion, screen-reader announcements, and whether
color is the only signal. Run axe or the repository's equivalent when
available, then manually traverse the primary flow by keyboard; automated
accessibility scans do not prove task usability.

### Responsive and visual system

Check narrow/intermediate/desktop reflow, long content, tables, dialogs,
overflow, theme contrast, tokens, type rhythm, spacing, icon consistency, and
layout stability.

### Performance and trust

Check image dimensions and loading, layout shift, blocking work, feedback during
async actions, destructive confirmation, and misleading placeholder or proof
content.

Use [review-checklist.md](references/review-checklist.md) and report only
actionable findings with priority, exact location/route, failure mode, impact,
and the smallest correction. Separate static findings from unverified visual
claims. Use the runtime state/viewport matrix supplied by `frontend-design`
rather than treating a single desktop screenshot as evidence.

## Completion condition

The report covers the requested surface and states, every finding is
evidence-backed or marked unverified, and the next design or engineering action
is clear.
