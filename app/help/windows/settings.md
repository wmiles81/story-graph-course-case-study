# Settings

Opened from **⚙️ Settings** in the header.

## AI Model

Choose a provider — **OpenRouter**, or a local **Ollama** / **LM Studio** server — and a
model. The key is written to `.env` beside the app.

This setting affects the **Ask** tab only. Nothing else in the app calls a model, and
nothing calls one unless you press a button.

The app can list a provider's available models and test a key without leaving the panel. A
local provider that is not running reports a failed probe rather than hanging.

## Display & accessibility

| Setting | Effect |
|---|---|
| **Text size** | Scales the whole interface (S / M / L / XL). |
| **Letter spacing** | Normal, wide, extra wide. |
| **Line height** | Tightens or opens vertical rhythm. |
| **High contrast** | Pure black/white with heavier rules. |
| **Dyslexia-friendly font** | OpenDyslexic where installed, with a fallback stack. |
| **Reduce motion** | Disables transitions and animations. |
| **Minimum font size** | Lifts the small print — hints, axis labels, node labels. |

Choices persist in your browser's local storage, so they survive a restart. They are
per-browser, not per-graph.

The app also follows your operating system's light/dark preference automatically.
