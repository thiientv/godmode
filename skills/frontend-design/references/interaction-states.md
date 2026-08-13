# Interaction and state checklist

## Controls

- Use native links, buttons, fields, dialogs, and headings where they match the
  behavior.
- Give icon-only controls an accessible name and a visible or discoverable
  tooltip where appropriate.
- Preserve focus visibility and logical keyboard order.
- Do not rely on hover to expose essential information.
- Make touch targets usable on the narrowest supported device.

## States

For each async or editable surface, decide what users see in:

| State | Required decision |
| --- | --- |
| Loading | what is stable, what is skeleton/progress, what remains actionable |
| Empty | why it is empty and the next useful action |
| Error | what failed, whether retry is safe, and how to recover |
| Disabled | why unavailable and whether explanation is needed |
| Success | confirmation, next action, and duplicate-submit behavior |
| Permission | what is hidden, blocked, or requestable |

Respect reduced-motion preferences. Never use animation to hide a delayed
response, a layout shift, or an error.
