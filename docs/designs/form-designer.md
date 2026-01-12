# Form Designer (Draft)

This document captures the initial form designer schema, event model, and code generation plan for VisualAsic.

## Overview
- File format: `.form` JSON (schema_version: 1)
- Purpose: WYSIWYG design of UI for Asic (VB6-like), with codegen to both VB-like form and target C++ (TFT_eSPI / sprites).

## Example .form
```json
{
  "schema_version": 1,
  "form": {
    "id": "MainForm",
    "title": "Settings",
    "size": { "w": 320, "h": 240 },
    "tags": ["settings", "main"]
  },
  "controls": [
    {
      "type": "Button",
      "id": "btnOk",
      "bounds": { "x": 220, "y": 200, "w": 80, "h": 30 },
      "text": "OK",
      "properties": { "bg": "#008800", "fontSize": 12 },
      "events": { "Click": "btnOk_Click", "Right_Click": "btnOk_RightClick" },
      "tags": ["primary", "submit"]
    }
  ]
}
```

## Event model
- Controls expose a set of events (e.g., Button: Click, Right_Click, Double_Click).
- The property inspector exposes an event dropdown. Selecting or double-clicking an event opens or creates a handler stub in the editor.
- Handler naming: `{controlId}_{EventName}` (e.g., `btnOk_RightClick`).

## Codegen examples (conceptual)
- VB-style (keeps round-trip semantics) and generated C++ stubs:

```cpp
SpriteButton btnOk(220,200,80,30,"OK");
void setup() { btnOk.create(); }
void loop() {
  if (btnOk.wasRightClicked()) btnOk_RightClick();
}
void btnOk_RightClick() { /* user code */ }
```

## Tags & metadata
- `form.tags` and `control.tags` used for grouping, bindings, and codegen hints (e.g., `persist:*`).

## Preview & WYSIWYG
- Live Preview Mode: simulate touch/keyboard, trigger handlers in a sandboxed preview runtime.

---

Next steps: prototype canvas and property inspector, add sample `.form` files and codegen tests.
