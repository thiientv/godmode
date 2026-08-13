---
name: frontend-design
description: >-
  Designs, builds, or refactors user-facing web or application interfaces with
  deliberate visual direction, typography, color and spacing tokens, content
  hierarchy, responsive behavior, accessible interaction states, and real
  rendered-surface verification. Use for pages, components, dashboards,
  landing pages, design systems, and frontend polish. Not for backend logic,
  API-only work, or visual claims that cannot be rendered or inspected.
---

# Frontend Design

Build an interface with a point of view and a usable system, not a collection
of default cards.

## Before writing UI code

1. Inspect the existing product, design tokens, routes, components, assets,
   fonts, and responsive conventions. Preserve a real system unless a scoped
   redesign is intended.
2. Identify product type, user context, primary action, content hierarchy,
   brand constraints, supported viewport range, and available visual assets.
3. Extract the existing visual system before inventing one. Inspect CSS
   variables, theme configuration, type loading, spacing, radii, breakpoints,
   component variants, and recurring layout patterns. Use the dependency-free
   helper when the system is spread across source files:

   ```bash
   python3 skills/frontend-design/scripts/extract_design_system.py ./src
   ```

   Read [design-system-extraction.md](references/design-system-extraction.md)
   before replacing or normalizing an existing token system.
4. Choose a visual direction and record the reason: type pairing, color role,
   density, shape language, imagery, and motion voice. Use the local
   `scripts/design_system.py` helper for a deterministic starting brief when a
   project has no design system:

   ```bash
   python3 skills/frontend-design/scripts/design_system.py \
     --product "analytics dashboard" --tone "technical" --stack react
   ```

   Search the small bundled design-intelligence catalog when a choice needs
   comparison; read [design-intelligence.md](references/design-intelligence.md)
   for the supported domains and limits. Do not treat a catalog result as a
   substitute for inspecting the existing product.

5. Define semantic tokens before scattering raw values through components.
6. Sketch the primary flow and all meaningful states: loading, empty, error,
   disabled, success, permission, and long-content cases.

## Build the system

- Use real content, realistic dimensions, and an intentional type scale.
- Prefer composition and hierarchy over decorative gradients, excessive
  shadows, or nested card stacks.
- Make controls semantic, keyboard reachable, focus-visible, and labeled.
- Design mobile and intermediate widths as first-class states, not a desktop
  layout squeezed into a phone.
- Make motion explain state or spatial continuity; provide reduced motion.
- Use icons consistently and never substitute emoji for product controls.

Read [design-system.md](references/design-system.md) for direction, tokens,
and anti-generic heuristics. Read [interaction-states.md](references/interaction-states.md)
for state and accessibility detail. Read [stack-adapters.md](references/stack-adapters.md)
only for the detected implementation stack. Use `browser-testing` for a real
browser flow and `ui-ux-review` for a separate quality pass.

## Visual verification

Render the actual route at the narrow, intermediate, and desktop widths. Check
hierarchy, overflow, focus, contrast, state transitions, content wrapping, and
reduced-motion behavior. Exercise the primary task with keyboard-only input and
run the project's accessibility tooling when available. Capture the state and
viewport matrix from [runtime-validation.md](references/runtime-validation.md).
Record screenshots or observations; source inspection alone cannot prove a
visual claim.

## Completion condition

The primary flow is usable, visual decisions are coherent and intentional,
states and responsive behavior are covered, accessibility is not traded for
appearance, and relevant rendered evidence is fresh.
