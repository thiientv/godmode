#!/usr/bin/env python3
"""Generate a small, deterministic frontend design brief from project inputs."""

from __future__ import annotations

import argparse
import json
import re
from dataclasses import asdict, dataclass
from typing import Sequence

from design_catalog import search_entries, serialize_entries


@dataclass(frozen=True)
class DesignBrief:
    product: str
    tone: str
    stack: str
    style: str
    palette: str
    direction: str
    display_font: str
    body_font: str
    accent: str
    surface: str
    density: str
    spacing: tuple[int, ...]
    radius: str
    motion: str
    layout: str
    ux_priorities: tuple[str, ...]
    anti_patterns: tuple[str, ...]


PRODUCT_RULES: tuple[tuple[tuple[str, ...], str, str, str], ...] = (
    (("dashboard", "analytics", "admin", "ops"), "information-dense", "Space Grotesk", "IBM Plex Sans"),
    (("portfolio", "agency", "studio", "creative"), "editorial", "Fraunces", "General Sans"),
    (("commerce", "shop", "store", "market"), "warm and trustworthy", "Bricolage Grotesque", "Source Sans 3"),
    (("health", "clinic", "medical", "care"), "calm and accessible", "Newsreader", "IBM Plex Sans"),
    (("developer", "api", "infrastructure", "technical"), "technical", "Geist Mono", "Geist"),
)

TONE_RULES: dict[str, tuple[str, str, str, str]] = {
    "editorial": ("Editorial contrast", "Fraunces", "General Sans", "#D97757"),
    "technical": ("Measured utility", "Space Grotesk", "IBM Plex Sans", "#2F6FED"),
    "playful": ("Bright, controlled energy", "Bricolage Grotesque", "General Sans", "#E45756"),
    "calm": ("Quiet confidence", "Newsreader", "IBM Plex Sans", "#2F7D6D"),
    "minimal": ("Restrained clarity", "Geist", "General Sans", "#3854D8"),
}

STACK_NOTES: dict[str, str] = {
    "react": "Keep tokens in the existing styling system and use semantic component boundaries.",
    "nextjs": "Respect server/client boundaries, reserve image space, and verify loading states.",
    "vue": "Keep stateful interaction in composables and preserve semantic template structure.",
    "svelte": "Keep transitions purposeful and ensure stores do not hide loading/error states.",
    "html-tailwind": "Use semantic CSS variables and avoid scattering arbitrary utility values.",
    "swiftui": "Respect Dynamic Type, safe areas, color scheme, and accessibility labels.",
    "flutter": "Respect text scaling, safe areas, semantic labels, and platform touch targets.",
    "unknown": "Extract the repository's established component, token, and styling conventions before choosing an adapter.",
}

STACK_ALIASES: dict[str, str] = {
    "next": "nextjs",
    "next.js": "nextjs",
    "tailwind": "html-tailwind",
    "html": "html-tailwind",
    "css": "html-tailwind",
}

PALETTE_TOKENS: dict[str, tuple[str, str]] = {
    "ink-and-citrus": ("#D97757", "#F7F5F0"),
    "navy-and-sky": ("#2F6FED", "#F4F7FB"),
    "sage-and-coral": ("#D96B55", "#F4F7F1"),
}


def slug_terms(value: str) -> set[str]:
    """Return normalized product terms for deterministic matching."""

    return set(re.findall(r"[a-z0-9]+", value.lower()))


def choose_product_rule(product: str) -> tuple[str, str, str]:
    """Choose direction and type roles from the product vocabulary."""

    terms = slug_terms(product)
    for keywords, direction, display, body in PRODUCT_RULES:
        if terms.intersection(keywords):
            return direction, display, body
    return "Clear, adaptable product utility", "Space Grotesk", "General Sans"


def normalize_stack(stack: str) -> str:
    """Normalize common stack aliases and reject silent generic fallbacks."""

    normalized = stack.strip().lower() or "html-tailwind"
    normalized = STACK_ALIASES.get(normalized, normalized)
    if normalized not in STACK_NOTES:
        supported = ", ".join(sorted(STACK_NOTES))
        raise ValueError(f"Unsupported stack {stack!r}; choose one of: {supported}")
    return normalized


def build_brief(product: str, tone: str, stack: str, density: str, style: str | None = None) -> DesignBrief:
    """Build a design brief without network access or random output."""

    normalized_tone = tone.strip().lower() or "minimal"
    normalized_stack = normalize_stack(stack)
    direction, product_display, product_body = choose_product_rule(product)
    tone_rule = TONE_RULES.get(normalized_tone)
    if tone_rule is None:
        display_font, body_font = product_display, product_body
        direction = f"{direction}; {normalized_tone} tone"
    else:
        direction, display_font, body_font, _tone_accent = tone_rule

    if normalized_tone in TONE_RULES and normalized_tone not in {"minimal", "technical"}:
        direction = f"{direction} for {product}"

    style_matches = search_entries(f"{product} {normalized_tone}", domain="style", limit=1)
    chosen_style = style.strip().lower() if style and style.strip() else (style_matches[0].name if style_matches else "workbench")
    style_entry = next((entry for entry in search_entries(chosen_style, domain="style", limit=5) if entry.name == chosen_style), None)
    if style and style.strip() and style_entry is None:
        raise ValueError(f"Unknown catalog style {style!r}")
    if style_entry is None and style_matches:
        style_entry = style_matches[0]
        chosen_style = style_entry.name

    palette_matches = search_entries(f"{product} {normalized_tone} {chosen_style}", domain="color", limit=1)
    chosen_palette = palette_matches[0].name if palette_matches else "ink-and-citrus"
    accent, surface = PALETTE_TOKENS[chosen_palette]
    ux_matches = search_entries(
        f"{product} responsive accessibility loading error motion",
        domain="ux",
        limit=3,
    )
    ux_priorities = tuple(entry.name for entry in ux_matches)
    if style_entry is not None:
        direction = style_entry.summary if style_entry.summary.lower().startswith(direction.lower()) else f"{direction}: {style_entry.summary}"

    spacing = {
        "spacious": (8, 16, 24, 40, 64, 96),
        "standard": (4, 8, 12, 16, 24, 32, 48, 64),
        "dense": (4, 8, 12, 16, 24, 32),
    }.get(density, (4, 8, 12, 16, 24, 32, 48, 64))
    layout = (
        "Use a stable content rail with a clear primary column and one deliberate secondary rhythm."
        if density != "dense"
        else "Use a compact grid with strong row alignment, visible grouping, and progressive disclosure."
    )
    return DesignBrief(
        product=product,
        tone=normalized_tone,
        stack=normalized_stack,
        style=chosen_style,
        palette=chosen_palette,
        direction=direction,
        display_font=display_font,
        body_font=body_font,
        accent=accent,
        surface=surface,
        density=density,
        spacing=spacing,
        radius="8px controls, 16px containers; avoid radius without hierarchy",
        motion="150–300ms ease-out for state changes; disable non-essential motion when reduced-motion is requested",
        layout=layout,
        ux_priorities=ux_priorities,
        anti_patterns=(
            "default purple gradient without a product reason",
            "unlabeled icon-only controls",
            "nested cards used as the only hierarchy",
            "desktop layout squeezed into a narrow viewport",
            "raw colors and arbitrary spacing scattered across components",
        ),
    )


def render_markdown(brief: DesignBrief) -> str:
    """Render a human-readable design brief."""

    stack_note = STACK_NOTES.get(brief.stack, "Follow the repository's established component and styling conventions.")
    anti_patterns = "\n".join(f"- {item}" for item in brief.anti_patterns)
    spacing = ", ".join(f"{value}px" for value in brief.spacing)
    return f"""# Design brief: {brief.product}

## Direction
- Tone: {brief.tone}
- Style: {brief.style}
- Palette direction: {brief.palette}
- Direction: {brief.direction}
- Stack: {brief.stack}
- Stack note: {stack_note}
- Layout: {brief.layout}

## Tokens
- Display: {brief.display_font}
- Body: {brief.body_font}
- Accent: {brief.accent}
- Surface: {brief.surface}
- Spacing: {spacing}
- Radius: {brief.radius}
- Motion: {brief.motion}
- UX priorities: {", ".join(brief.ux_priorities)}

## Before implementation
- Define semantic text, surface, border, accent, focus, success, warning, and danger roles.
- Create loading, empty, error, disabled, success, and long-content states for the primary flow.
- Verify narrow, intermediate, and desktop widths with real content.

## Avoid
{anti_patterns}
"""


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    """Parse command-line arguments."""

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--product", help="Product or page type, for example 'analytics dashboard'.")
    parser.add_argument("--search", help="Search the bundled design-intelligence catalog instead of generating a brief.")
    parser.add_argument(
        "--domain",
        choices=("all", "style", "color", "typography", "product", "layout", "accessibility", "ux"),
        default="all",
    )
    parser.add_argument("--limit", type=int, default=5, help="Maximum catalog results to print.")
    parser.add_argument("--tone", default="minimal", help="Tone: minimal, technical, editorial, playful, or calm.")
    parser.add_argument("--stack", default="html-tailwind", help="Frontend stack used by the project.")
    parser.add_argument("--style", help="Optional catalog style override, for example 'editorial' or 'workbench'.")
    parser.add_argument("--density", choices=("spacious", "standard", "dense"), default="standard")
    parser.add_argument("--format", choices=("markdown", "json"), default="markdown")
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    """Generate and print a design brief."""

    args = parse_args(argv)
    if args.limit < 1:
        raise SystemExit("--limit must be a positive integer")
    if args.search:
        entries = search_entries(args.search, domain=args.domain, limit=args.limit)
        if args.format == "json":
            print(json.dumps(serialize_entries(entries), indent=2))
        else:
            if not entries:
                print(f"No design-intelligence matches for: {args.search}")
            for entry in entries:
                print(f"## {entry.domain}: {entry.name}\n{entry.summary}")
                for item in entry.guidance:
                    print(f"- {item}")
                print()
        return 0
    if not args.product:
        raise SystemExit("--product is required unless --search is used")
    try:
        brief = build_brief(args.product, args.tone, args.stack, args.density, args.style)
    except ValueError as error:
        raise SystemExit(str(error)) from error
    if args.format == "json":
        print(json.dumps(asdict(brief), indent=2))
    else:
        print(render_markdown(brief), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
