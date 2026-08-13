#!/usr/bin/env python3
"""Small original design-intelligence catalog used by the frontend helper."""

from __future__ import annotations

from dataclasses import asdict, dataclass
import re
from typing import Iterable


@dataclass(frozen=True)
class CatalogEntry:
    domain: str
    name: str
    summary: str
    tags: tuple[str, ...]
    guidance: tuple[str, ...]


ENTRIES: tuple[CatalogEntry, ...] = (
    CatalogEntry(
        "style", "editorial", "High-contrast type and paced content for narrative products.",
        ("editorial", "story", "brand", "portfolio", "magazine"),
        ("Pair an expressive display face with a restrained body face.", "Use whitespace and rule lines as structure, not decoration.", "Keep interactions quiet enough for reading."),
    ),
    CatalogEntry(
        "style", "technical", "Measured utility for developer tools, infrastructure, and dense workflows.",
        ("technical", "developer", "api", "infrastructure", "dashboard", "dense"),
        ("Use a strong grid and explicit status hierarchy.", "Reserve monospace for code, data, or a deliberate label role.", "Make loading, latency, and failure states visible."),
    ),
    CatalogEntry(
        "style", "soft", "Calm surfaces and readable rhythm for care, wellness, and supportive tools.",
        ("soft", "calm", "health", "wellness", "care", "trust"),
        ("Use low-noise surfaces with a clear semantic accent.", "Keep contrast and focus stronger than the palette's softness.", "Avoid making recovery actions visually timid."),
    ),
    CatalogEntry(
        "style", "playful", "Controlled color, expressive type, and clear interaction feedback for consumer products.",
        ("playful", "consumer", "social", "education", "creative", "bright"),
        ("Give the primary action one unmistakable visual voice.", "Use asymmetry or illustration with a reason tied to the audience.", "Keep motion optional and content legible."),
    ),
    CatalogEntry(
        "style", "workbench", "Practical, compact interface language for internal tools and operations.",
        ("workbench", "ops", "admin", "internal", "workflow", "table"),
        ("Optimize scanning, keyboard flow, and predictable density.", "Use dividers and alignment before adding containers.", "Preserve destructive-action clarity in dense layouts."),
    ),
    CatalogEntry(
        "color", "ink-and-citrus", "Warm paper, near-black text, and a restrained orange action accent.",
        ("warm", "paper", "orange", "editorial", "citrus", "accessible"),
        ("Surface #F7F5F0; text #1A1A1A; accent #D97757; success #2F7D6D.", "Use the orange for action and emphasis, not body copy.", "Check dark-theme roles separately."),
    ),
    CatalogEntry(
        "color", "navy-and-sky", "Cool, dependable contrast for technical products and status-heavy screens.",
        ("navy", "blue", "technical", "saas", "status", "dashboard"),
        ("Surface #F4F7FB; text #152033; accent #2F6FED; warning #B76E00.", "Use blue for action and links, not every semantic state.", "Pair status colors with labels or icons."),
    ),
    CatalogEntry(
        "color", "sage-and-coral", "Human, calm palette with a visible action and recovery hierarchy.",
        ("sage", "coral", "health", "care", "wellness", "calm"),
        ("Surface #F4F7F1; text #18211B; accent #D96B55; success #2F7D6D.", "Keep coral away from error-only semantics if it is the brand accent.", "Test contrast on muted surfaces."),
    ),
    CatalogEntry(
        "typography", "display-contrast", "Expressive display face with a neutral, highly readable UI body.",
        ("editorial", "brand", "display", "serif", "contrast"),
        ("Try Fraunces, Newsreader, or Bricolage Grotesque for display.", "Pair with General Sans, IBM Plex Sans, or Switzer for body.", "Keep line length near 45–75 characters."),
    ),
    CatalogEntry(
        "typography", "technical-utility", "Strong grotesque or mono display with an engineering body face.",
        ("technical", "developer", "mono", "dashboard", "data"),
        ("Try Space Grotesk or Geist Mono for display moments.", "Pair with IBM Plex Sans, Geist, or Switzer for body.", "Use mono as a role, not as decoration everywhere."),
    ),
    CatalogEntry(
        "typography", "quiet-reading", "Soft display contrast and generous body measure for supportive content.",
        ("calm", "health", "reading", "care", "serif"),
        ("Try Newsreader or Source Serif 4 for display/body pairing.", "Use a neutral sans for controls and labels.", "Do not let softness reduce label clarity or focus."),
    ),
    CatalogEntry(
        "ux", "async-feedback", "Make progress, failure, retry, and success legible at the action boundary.",
        ("loading", "error", "retry", "success", "async", "feedback"),
        ("Reserve space before data arrives.", "Put recovery next to the failed action.", "Prevent duplicate submits and announce state changes."),
    ),
    CatalogEntry(
        "ux", "responsive-resilience", "Protect hierarchy and interaction across narrow, intermediate, and desktop widths.",
        ("responsive", "mobile", "breakpoint", "overflow", "layout"),
        ("Test long headings, tables, dialogs, and controls.", "Prefer reflow and progressive disclosure to clipped content.", "Do not hide horizontal overflow without investigating why it exists."),
    ),
    CatalogEntry(
        "ux", "motion-with-purpose", "Use motion for feedback and spatial continuity with a reduced-motion path.",
        ("motion", "animation", "reduced-motion", "transition", "interaction"),
        ("Prefer transform/opacity and short state transitions.", "Avoid decorative motion that competes with reading or input.", "Freeze motion for visual tests for a documented reason."),
    ),
    CatalogEntry(
        "product", "developer-tool", "High-signal workflows for code, infrastructure, debugging, and technical decisions.",
        ("developer", "code", "api", "infrastructure", "debugging", "technical"),
        ("Keep status, latency, and failure evidence close to the action.", "Give code and data a dedicated typographic role.", "Optimize keyboard flow before decorative density."),
    ),
    CatalogEntry(
        "product", "operations-console", "Dense operational control with explicit risk, ownership, and state change feedback.",
        ("operations", "admin", "monitoring", "incident", "table", "workflow"),
        ("Separate observation from mutation.", "Show freshness and source for important status.", "Make destructive and irreversible actions visually distinct."),
    ),
    CatalogEntry(
        "product", "commerce", "Trust-led discovery and purchase flows with visible totals and recovery.",
        ("commerce", "store", "checkout", "catalog", "payment", "trust"),
        ("Keep price, availability, delivery, and return information near decisions.", "Preserve cart state through failure.", "Avoid decorative urgency that undermines trust."),
    ),
    CatalogEntry(
        "product", "care-service", "Calm, legible workflows for health, support, and high-anxiety tasks.",
        ("health", "care", "support", "appointment", "accessible", "calm"),
        ("Use plain language and visible recovery.", "Treat privacy and consent as interface states.", "Do not trade contrast or target size for visual softness."),
    ),
    CatalogEntry(
        "layout", "command-center", "A stable command rail with one primary workspace and contextual secondary detail.",
        ("dashboard", "workspace", "sidebar", "detail", "dense", "operations"),
        ("Keep global navigation and task controls distinct.", "Let detail collapse before the primary workspace.", "Preserve selection and scroll context."),
    ),
    CatalogEntry(
        "layout", "narrative-rail", "A paced editorial rail for explanation, evidence, and conversion.",
        ("landing", "editorial", "story", "marketing", "portfolio", "content"),
        ("Vary section rhythm without losing the reading order.", "Keep one message and action per major beat.", "Use imagery as evidence or atmosphere, not filler."),
    ),
    CatalogEntry(
        "layout", "focused-form", "A narrow decision flow with progressive disclosure and persistent recovery context.",
        ("form", "onboarding", "checkout", "settings", "wizard", "input"),
        ("Group fields by user decision, not database shape.", "Place validation at the owning field and summary.", "Preserve entered data after recoverable failure."),
    ),
    CatalogEntry(
        "layout", "comparison-grid", "Parallel alternatives with aligned criteria and a legible recommendation.",
        ("pricing", "compare", "plans", "features", "decision", "grid"),
        ("Align equivalent attributes across options.", "Keep differences visible without hiding limitations.", "Reflow to sequential sections on narrow screens."),
    ),
    CatalogEntry(
        "accessibility", "keyboard-first", "All primary tasks remain understandable and operable without a pointer.",
        ("keyboard", "focus", "dialog", "menu", "shortcut", "accessibility"),
        ("Use semantic controls and predictable focus order.", "Restore focus when overlays close.", "Do not make shortcuts the only path."),
    ),
    CatalogEntry(
        "accessibility", "form-recovery", "Errors are identified, associated, announced, and recoverable without losing work.",
        ("form", "error", "validation", "aria", "recovery", "accessibility"),
        ("Keep labels visible and errors programmatically associated.", "Move focus to a useful summary only when it helps.", "Preserve valid input across retries."),
    ),
    CatalogEntry(
        "accessibility", "adaptive-reading", "Content survives zoom, text scaling, localization, and user contrast preferences.",
        ("zoom", "localization", "contrast", "text", "responsive", "reading"),
        ("Avoid fixed-height text containers.", "Test long labels and 200% zoom.", "Keep meaning independent of color and spatial position alone."),
    ),
    CatalogEntry(
        "ux", "optimistic-with-recovery", "Fast perceived response with explicit pending, failure, and reconciliation states.",
        ("optimistic", "pending", "rollback", "sync", "offline", "mutation"),
        ("Show which state is not yet confirmed.", "Provide a deterministic recovery path.", "Never display success before the durable boundary accepts the change."),
    ),
    CatalogEntry(
        "ux", "trust-and-provenance", "Expose freshness, source, scope, and uncertainty for consequential information.",
        ("trust", "source", "freshness", "ai", "evidence", "status"),
        ("Label generated or inferred content.", "Keep source and update time near decisions.", "Distinguish unavailable, unknown, stale, and empty."),
    ),
    CatalogEntry(
        "ux", "destructive-safety", "Make high-impact actions intentional, scoped, and recoverable where possible.",
        ("delete", "destructive", "confirm", "undo", "risk", "permission"),
        ("State the object and blast radius in confirmation.", "Prefer undo for reversible actions.", "Require stronger friction only as irreversibility rises."),
    ),
)


def terms(value: str) -> set[str]:
    """Normalize search text into comparable terms."""

    return set(re.findall(r"[a-z0-9]+", value.lower()))


def search_entries(query: str, domain: str | None = None, limit: int = 5) -> list[CatalogEntry]:
    """Return deterministic catalog matches ranked by tag/name overlap."""

    if limit < 1:
        return []
    query_terms = terms(query)
    candidates = [entry for entry in ENTRIES if domain in {None, "all", entry.domain}]
    scored: list[tuple[float, CatalogEntry]] = []
    for entry in candidates:
        entry_terms = terms(" ".join((entry.name, entry.summary, *entry.tags)))
        score = len(query_terms.intersection(entry_terms))
        if score:
            scored.append((float(score), entry))
    scored.sort(key=lambda item: (-item[0], item[1].domain, item[1].name))
    return [entry for _, entry in scored[:limit]]


def serialize_entries(entries: Iterable[CatalogEntry]) -> list[dict[str, object]]:
    """Convert catalog entries to JSON-compatible dictionaries."""

    return [asdict(entry) for entry in entries]
