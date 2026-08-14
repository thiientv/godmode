# Client compatibility

Compatibility claims are evidence-scoped. A standard layout or valid manifest
does not prove that every client discovers, routes, and executes a skill in the
same way.

<!-- compatibility-table:start -->
| Surface | Current evidence | Status |
| --- | --- | --- |
| Agent Skills directory layout | Repository validator checks frontmatter, names, links, body limits, and routing fixtures | Structurally supported |
| Claude Code plugin | Marketplace manifest passed local plugin validation; SessionStart hook emitted valid JSON context | Adapter validated locally |
| Codex plugin | Direct and packaged manifests pass repository schema checks | Manifest validated; clean-profile install pending |
| Explicit Codex skill use | Independent forward runs can load skills by path | Forward-test surface available |
| Cursor, Gemini CLI, OpenCode, and other clients | Standard skill directories can be copied; no native trace is recorded | Unverified |
<!-- compatibility-table:end -->

Record future checks with client version, model, installation method, prompt,
activated skills, sanitized public trace, output artifacts, and limitations.
Do not upgrade a status based only on successful copying or a screenshot of the
skill list. Update `compatibility/evidence.json`, then run
`python3 scripts/compatibility.py write`; CI rejects stale rendered evidence.
