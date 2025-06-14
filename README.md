# Python Profiler Viewer

A **streaming log viewer and profiler visualizer** built for large-scale Python profiling data.

---

## 🚀 Features

- 🔄 **Streaming JSONL file processing** — processes log files while loading
- 🌳 **Virtualized expandable Call Tree** — smooth scroll & expand, even for millions of calls
- 📊 **Timeline view (Plotly powered)** — visual execution timeline
- 📈 **Summary table** — aggregated total time per function
- ⚡ **Fully browser-based** — no backend server required

---

## 📄 Log Format

Profiler expects newline-delimited JSON arrays (`.jsonl`), where each line represents one event:

```json
["17:54:12.457", "start", "function_name", 123, 122, "sync"]