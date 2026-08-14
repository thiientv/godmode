# CodeTour output

Use a `.tour` artifact when the orientation map should become a durable,
ordered walkthrough for onboarding, architecture review, incident learning, or
a pull request. Keep the normal orientation map for one-off scoping.

## Input specification

Create a small JSON file with repository-relative source anchors:

```json
{
  "title": "Request lifecycle",
  "description": "Follow one request from the public route to persistence.",
  "steps": [
    {
      "file": "src/http/routes.py",
      "line": 18,
      "title": "Public entry point",
      "description": "The route validates the request and hands it to the service boundary."
    }
  ]
}
```

Generate the artifact:

```bash
python3 skills/codebase-orientation/scripts/create_code_tour.py \
  /tmp/orientation.json .tours/request-lifecycle.tour --root .
```

The helper rejects missing files, escaping paths, invalid line anchors, empty
descriptions, and non-`.tour` outputs. Order steps by execution flow or learning
dependency, not directory order. Explain why each anchor matters and keep each
step focused on one transition.
