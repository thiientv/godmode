# UI runtime validation matrix

Use representative real content and record target URL/build plus browser or
device version. Treat each width as a separate check, not a promise that one
breakpoint represents the entire range.

| State | Narrow (360/390px) | Intermediate (768/1024px) | Desktop (1280/1440px) | Keyboard | Accessibility scan |
| --- | --- | --- | --- | --- | --- |
| Primary flow |  |  |  |  |  |
| Loading |  |  |  |  |  |
| Empty |  |  |  |  |  |
| Error and retry |  |  |  |  |  |
| Success/confirmation |  |  |  |  |  |
| Permission/disabled |  |  |  |  |  |
| Long/localized content |  |  |  |  |  |

Mark every cell `pass`, `fail`, or `blocked`, with a screenshot, trace, or note
that identifies the exact build and viewport. A fresh check means the current
build was loaded or reloaded after the relevant change; a stale browser tab is
not evidence. `Pass` means the state was exercised and met the observable
criteria. `Fail` records a reproducible defect. `Blocked` records why the state
could not be exercised and what evidence is still missing.

Capture screenshots with animation stabilized for a documented reason. Check
console errors, failed requests, focus movement, accessible names, layout shift,
overflow, zoom/text scaling, and reduced motion. A visual diff must use a known
baseline and a documented threshold; pixel equality is not a usability oracle.
