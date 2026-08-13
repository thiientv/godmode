# Design system direction

## Direction brief

Write these decisions before implementing a new surface:

```text
Product and audience:
Primary action:
Visual voice:
Display/body/label type roles:
Color roles and contrast target:
Density and spacing scale:
Shape and elevation language:
Image or illustration strategy:
Motion voice and reduced-motion behavior:
Supported viewports:
Anti-patterns deliberately excluded:
```

## Token layers

Keep the layers separate:

1. **Primitive:** raw color, spacing, radius, type, and shadow values.
2. **Semantic:** surface, text, border, accent, success, warning, danger,
   focus, and disabled roles.
3. **Component:** button, field, navigation, card, table, dialog, and state
   variants that consume semantic roles.

Do not put brand hex values directly in repeated component rules. Define light
and dark surfaces by contrast and elevation, not by blindly inverting values.

## Anti-generic checks

- A chosen type pairing has a reason; it is not the framework default by habit.
- Color has semantic roles and a controlled accent; a purple gradient is not a
  design system.
- The hero or first viewport communicates the job before decoration appears.
- Repeated cards earn their boundaries; hierarchy is not expressed only by
  more containers.
- A deliberate asymmetry, editorial rhythm, texture, or image choice is used
  when the product voice calls for it.
- Variation never removes semantic structure, keyboard access, or readable copy.
