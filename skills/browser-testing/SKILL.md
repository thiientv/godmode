---
name: browser-testing
description: >-
  Tests a real web user flow with a browser by asserting semantic behavior,
  network and loading states, keyboard access, responsive layouts, and stable
  visual evidence. Use for browser bugs, end-to-end UI behavior, responsive or
  accessibility checks, and screenshot baselines. Not for static source review
  without a browser or for backend-only tests.
---

# Browser Testing

Exercise the user boundary with deterministic data and meaningful assertions.

## Build the test

1. Identify the route, user role, starting state, and supported viewport.
2. Wait on semantic readiness—role, label, URL, response, or visible state—not
   arbitrary sleeps.
3. Assert the user outcome, important error path, and relevant network/API
   behavior. Prefer accessible locators over CSS implementation details.
4. Cover keyboard flow and at least the narrowest supported viewport for
   responsive work.
5. Freeze clocks, animations, random IDs, remote data, and fonts only when the
   test requires stable visual evidence; do not hide real regressions.
6. Capture screenshots at stable component/page boundaries and review diffs
   before updating baselines.

Use [browser-checklist.md](references/browser-checklist.md) for Playwright,
DevTools, and non-Playwright equivalents. Use `frontend-design` for design
decisions and `ui-ux-review` for an independent visual pass.

## Safety and flake control

Use test accounts and fixtures. Do not send destructive actions to production.
Record browser, viewport, locale, timezone, and feature flags. Investigate
flakes instead of increasing timeouts until they disappear.

## Completion condition

The browser test proves the requested user behavior at the real boundary, is
repeatable, covers the relevant state/viewport, and reports visual or
environment limits.
