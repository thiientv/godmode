---
name: incident-response
description: >-
  Coordinates an active production incident by establishing command, reducing
  blast radius, preserving evidence, communicating verified impact, restoring
  service, validating recovery, and creating owned follow-up actions. Use for
  outages, severe degradation, security or data-integrity events, failed
  releases, and urgent operational triage. Not for a normal local bug, routine
  alert tuning, or a postmortem after the incident is already closed.
---

# Incident Response

Stabilize first, learn second. Do not let diagnosis delay a safe reversible
mitigation.

## Establish control

Record start time, incident commander, responders, severity, affected users and
regions, known symptoms, recent changes, communication channel, and next update
time. Use [incident-record.md](references/incident-record.md) as the live log.
Separate confirmed facts from hypotheses.

## Contain and recover

1. Protect people, data integrity, credentials, and irreversible state.
2. Reduce blast radius with a kill switch, traffic shift, dependency isolation,
   rollback, rate limit, or safe degradation when authorized.
3. Preserve timestamps, deploy identifiers, logs, metrics, traces, and commands
   before ephemeral evidence disappears.
4. Test ranked hypotheses without making several uncontrolled production
   changes at once.
5. Verify recovery from user-facing behavior and service-level signals, not one
   green dashboard.

Use `release-engineering` for a failed rollout, `security-and-hardening` for an
active security boundary, and `root-cause-debugging` for deeper diagnosis after
the service is stable. Production mutations require the repository's normal
authority and approval; this skill does not grant it.

## Communicate and close

Publish concise updates with verified impact, current mitigation, user action if
any, and next update time. Avoid speculative root causes. Close the incident
only after critical paths, backlog recovery, data reconciliation, and alert
state are checked.

Create a blameless timeline and a small set of owned, dated actions: regression
proof, detection gap, recovery improvement, and prevention at the correct owner
boundary. Track them outside the incident document.

## Completion condition

Impact has ended, recovery is independently verified, data and queued work are
reconciled or explicitly owned, communications are complete, and follow-up
actions have owners and due dates.
