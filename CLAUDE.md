# Decision Tree Coverage Tracker

A local tool for documenting and tracking test coverage of form-based public service flows.
The user edits `tree.json` in their editor (neovim), runs a local Python server, and views the
rendered graph in a browser.

---

## Project Structure

```
project/
├── CLAUDE.md
├── server.py          # Simple Python HTTP server
├── tree.json          # Decision tree data (user edits this)
└── index.html         # Single-page app, reads tree.json via fetch
```

---

## Running the App

```bash
python3 server.py
# then open http://localhost:8000 in the browser
```

No npm, no build step. Plain HTML + vanilla JS in a single file.

---

## tree.json Schema

The tree is a **flat array of nodes**. Nodes reference each other by `id`.
There are two node types: `decision` and `action`.

### Decision node

A step where the user picks a branch.

```json
{
  "id": "interruptions_6mo",
  "type": "decision",
  "question": "Have there been any interruptions in the stay in Germany of more than 6 months?",
  "covered": true,
  "branches": [
    { "label": "yes", "next": "period_abroad" },
    { "label": "no", "next": "maintenance_payments" }
  ]
}
```

### Action node

A step where the user must perform one or more actions (upload docs, fill fields, etc.)
before moving on. No branching — single `next`.

```json
{
  "id": "period_abroad",
  "type": "action",
  "actions": [
    "Upload proof of time spent abroad",
    "Select dates of absence"
  ],
  "covered": false,
  "next": "maintenance_payments"
}
```

### Root node

The entry point of the tree. There is always exactly one root node.
It is the node not referenced by any other node's `next` or `branches[].next`.

### Field reference

| Field       | Type              | Required          | Description                                         |
|-------------|-------------------|-------------------|-----------------------------------------------------|
| `id`        | string            | yes               | Unique identifier, used to link nodes               |
| `type`      | `decision/action` | yes               | Controls which other fields are expected            |
| `question`  | string            | if decision       | The question shown at this decision point           |
| `branches`  | array             | if decision       | Each branch has a `label` (string) and `next` (id) |
| `actions`   | array of strings  | if action         | List of things to do at this step                  |
| `next`      | string (id)       | if action         | ID of the next node after actions are done          |
| `covered`   | boolean           | yes               | Whether this node is covered by an automated test   |

### Notes

- A node with no `next` and no `branches` is a **terminal node** (end of flow).
- Multiple nodes can point to the same `next` (converging paths are valid).
- `covered` should be set on every node, including terminal ones.

---

## Example tree.json

This example mirrors the flow visible in the app screenshot for reference.

```json
[
  {
    "id": "apply_for",
    "type": "decision",
    "question": "What would you like to apply for?",
    "covered": true,
    "branches": [
      { "label": "Renew residence permit", "next": "upload_permit_renew" },
      { "label": "Residence permit for the first time", "next": "reason_for_application" }
    ]
  },
  {
    "id": "upload_permit_renew",
    "type": "action",
    "actions": ["Upload copy of current residence permit"],
    "covered": true,
    "next": "interruptions_6mo"
  },
  {
    "id": "interruptions_6mo",
    "type": "decision",
    "question": "Have there been any interruptions in the stay in Germany of more than 6 months?",
    "covered": true,
    "branches": [
      { "label": "yes", "next": "period_abroad" },
      { "label": "no", "next": "maintenance_payments" }
    ]
  },
  {
    "id": "period_abroad",
    "type": "action",
    "actions": [
      "Upload proof of time spent abroad",
      "Select dates of absence"
    ],
    "covered": false,
    "next": "maintenance_payments"
  },
  {
    "id": "maintenance_payments",
    "type": "decision",
    "question": "Are you obliged to make maintenance payments to other persons?",
    "covered": false,
    "branches": [
      { "label": "yes", "next": "maintenance_payments_component" },
      { "label": "no", "next": "criminal_record" }
    ]
  },
  {
    "id": "maintenance_payments_component",
    "type": "action",
    "actions": ["Fill in maintenance payments details"],
    "covered": false,
    "next": "criminal_record"
  },
  {
    "id": "criminal_record",
    "type": "decision",
    "question": "Do you have a criminal record?",
    "covered": false,
    "branches": [
      { "label": "yes", "next": "criminal_record_details" },
      { "label": "no", "next": "end_renew" }
    ]
  },
  {
    "id": "criminal_record_details",
    "type": "action",
    "actions": ["Provide criminal record details"],
    "covered": false,
    "next": "end_renew"
  },
  {
    "id": "end_renew",
    "type": "action",
    "actions": ["Submit application"],
    "covered": false
  },
  {
    "id": "reason_for_application",
    "type": "decision",
    "question": "What is the reason for your application?",
    "covered": true,
    "branches": [
      { "label": "Asylum was approved", "next": "step_had_temporary_residence_permit" },
      { "label": "War in Ukraine", "next": "step_group_of_people" },
      { "label": "Humanitarian admission program", "next": "step_has_german_diplomatic_mission_visa" },
      { "label": "Right of residence", "next": "upload_permit_first_time" },
      { "label": "Temporary period / urgent reason", "next": "upload_permit_urgent" }
    ]
  },
  {
    "id": "step_had_temporary_residence_permit",
    "type": "action",
    "actions": ["Complete temporary residence permit step"],
    "covered": true
  },
  {
    "id": "step_group_of_people",
    "type": "action",
    "actions": ["Complete group of people step"],
    "covered": true
  },
  {
    "id": "step_has_german_diplomatic_mission_visa",
    "type": "action",
    "actions": ["Complete German diplomatic mission visa step"],
    "covered": true
  },
  {
    "id": "upload_permit_first_time",
    "type": "action",
    "actions": ["Upload copy of residence permit"],
    "covered": false,
    "next": "step_is_over_27"
  },
  {
    "id": "step_is_over_27",
    "type": "action",
    "actions": ["Complete age verification step"],
    "covered": false
  },
  {
    "id": "upload_permit_urgent",
    "type": "action",
    "actions": [
      "Upload copy of residence permit",
      "Select date of first entry in Germany"
    ],
    "covered": false,
    "next": "step_desired_length_of_stay"
  },
  {
    "id": "step_desired_length_of_stay",
    "type": "action",
    "actions": ["Fill in desired length of stay"],
    "covered": true
  }
]
```

---

## index.html Requirements

- Single HTML file, no build step, no external dependencies except a CDN graph library
- Use **D3.js** (from CDN) to render the graph as an SVG
- On page load: `fetch('./tree.json')`, parse, render
- Add a **Refresh** button to re-fetch and re-render without a full page reload

### Graph rendering

- Lay out the graph top-to-bottom (root at top, terminals at bottom)
- **Decision nodes**: diamond shape, labelled with the `question` text (truncated if long)
- **Action nodes**: rectangle, labelled with the node `id` and lists `actions` items below
- **Edges**: labelled with `branch.label` for decision branches; no label for action `next` edges
- **Coverage colors**:
  - `covered: true` → green (`#2d5a2d` fill, `#4caf50` border)
  - `covered: false` → red (`#5a2d2d` fill, `#e57373` border)
- Node text: white, readable font size

### Coverage summary

Show a small panel (top-right corner or below the graph) with:
- Total nodes
- Covered count
- Not covered count
- Coverage percentage (e.g. `9 / 17 covered (53%)`)

### Tooltip on hover

On hovering a node, show a tooltip with:
- Full question text (for decision nodes)
- Full list of actions (for action nodes)
- Covered status

---

## server.py Requirements

Simple Python 3 HTTP server, no dependencies beyond stdlib.

```python
# Serves current directory on port 8000
# Should print the URL on startup
# python3 server.py
```

Use `http.server.SimpleHTTPRequestHandler`. No routing needed.

---

## What this tool is NOT

- Not a test runner
- Not connected to any test framework
- Not auto-synced with the form — the user maintains `tree.json` manually
- No authentication, no deployment — local use only
