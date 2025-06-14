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
```

![image](https://github.com/user-attachments/assets/3f38d4f1-f72f-473e-92b0-1431ef5fbadc)
![image](https://github.com/user-attachments/assets/f1b39497-af44-405b-89cb-5a538a4803f2)
![image](https://github.com/user-attachments/assets/85d34f20-bb10-4fcb-83de-7b2097d13a22)
![image](https://github.com/user-attachments/assets/024e34b6-5856-43ee-9ced-dbcce97ebedb)
