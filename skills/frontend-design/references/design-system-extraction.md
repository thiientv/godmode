# Design-system extraction

Inspect before normalizing:

- primitive and semantic CSS variables;
- theme or utility configuration;
- loaded fonts and type roles;
- spacing, radius, shadow, and motion scales;
- breakpoints, container widths, and density modes;
- component variants and state ownership;
- light/dark/high-contrast behavior;
- repeated raw values that may reveal an undocumented token.

The extraction helper reports lexical evidence, not token intent. Confirm high
frequency values in rendered components and distinguish deliberate exceptions
from drift. Preserve public token names or provide a migration path when other
packages consume them.

Produce a short system record with current tokens, inconsistencies, proposed
semantic roles, compatibility impact, and the rendered surfaces used as proof.
