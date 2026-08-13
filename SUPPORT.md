# Support policy

Godmode is a pre-1.0 community project. Maintainers support defects in the
published skill instructions, repository validators, deterministic helpers,
and bundled Claude/Codex manifests on a best-effort basis.

## Supported reports

- a skill reliably activates for the wrong task or fails to activate for a
  realistic task;
- instructions produce a reproducible unsafe, contradictory, or unusable
  workflow;
- validators, helpers, manifests, installation instructions, or packaged files
  are broken;
- behavior differs across a named client and version with a reproducible trace;
- documentation misstates a tested capability.

Include the Godmode version or commit, client and model version, operating
system, exact prompt, relevant repository shape, sanitized public trace, output
artifacts, and expected behavior. Use the security process for credentials,
private data, prompt-injection exploits, or other sensitive reports.

## Boundaries

Godmode cannot guarantee identical activation or output across models and
clients. Provider APIs, deployment environments, model availability, external
plugins, and copied or locally modified skills are outside maintainer control.

Breaking skill-name and routing changes may occur before 1.0 and will be listed
in the changelog. Published releases receive fixes on the latest minor version;
older pre-1.0 versions are not maintained as long-lived branches.
