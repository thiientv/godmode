# Stack adapters

Load only the relevant section.

## React and Next.js

Keep semantic tokens outside individual components. Preserve server/client
boundaries, reserve image and async layout space, and verify hydration, route
loading, and error boundaries. Prefer composition over boolean-variant sprawl.

## Vue and Nuxt

Keep visual state explicit in templates and reusable behavior in composables.
Verify scoped styles do not duplicate tokens and transitions respect reduced
motion.

## Svelte and SvelteKit

Keep stores from hiding loading and error ownership. Verify action enhancement,
route states, and transition cleanup on navigation.

## Tailwind or utility CSS

Use the project's theme and CSS variables before arbitrary values. Extract a
component when a repeated utility group represents one semantic variant; do not
create wrappers solely to shorten class strings.

## SwiftUI

Verify Dynamic Type, VoiceOver names and order, safe areas, color schemes,
reduce-motion, platform navigation, and state restoration.

## Flutter

Verify text scaling, semantics, safe areas, focus traversal, platform target
sizes, theme extensions, and narrow/wide adaptive layout.
