# Browser test checklist

- [ ] Start from a known fixture and authenticated role.
- [ ] Assert semantic readiness instead of `sleep`/`waitForTimeout`.
- [ ] Use roles, labels, text, or stable test IDs according to the repository.
- [ ] Cover success and the requested empty/error/loading path.
- [ ] Exercise keyboard focus and submit/cancel behavior where relevant.
- [ ] Check narrow and desktop viewport behavior for layout changes.
- [ ] Freeze dynamic values only for a reason and document masks.
- [ ] Review screenshot diffs before updating a baseline.
- [ ] Capture console, network, and trace artifacts when diagnosing a failure.
- [ ] For post-deploy checks, confirm the deployed build/version marker first.
- [ ] Compare production observations with a named baseline and watch window.
