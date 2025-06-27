# Python Profiler Viewer

A **streaming log viewer and profiler visualizer** built for Python programs.

---

## 🚀 Features

- 🔄 **Streaming JSONL file processing** — processes log files while loading
- 🌳 **Virtualized expandable Call Tree** — smooth scroll & expand
- 📊 **Timeline view (Plotly powered)** — visual execution timeline
- 🔥 **FlameGraph View** — visualizing time spent in functions.
- 📈 **Summary table** — aggregated total time per function
- ⚡ **Fully browser-based** — no backend server required

---

## 📄 Log Format

Profiler expects newline-delimited JSON arrays (`.jsonl`), where each line represents one event:

```json
["0.4930", "0.0290", "dominates", 19, 5, 1]
```
Flame Graph Tab:
See the program Flame Graph.
![image](https://github.com/user-attachments/assets/f3cf1648-6492-4904-8ae1-aa7507bc6059)
Timeline Tab:
See the visual execution timeline.
![image](https://github.com/user-attachments/assets/df9a9861-b920-4da3-aca5-8a4779e4e967)
Summary Tab: 
Overall summary for all functions (average runtimes, number of calls, ...).
![image](https://github.com/user-attachments/assets/38fdc074-3bec-41bb-b234-9084f496aa35)
Details Tab: 
Click on any function in the call tree to see details.
![image](https://github.com/user-attachments/assets/ff3dddfb-2e8e-41f9-a8fd-251359887dc4)
Compare Tab:
Load two log files and see what has improved or worsened.
![image](https://github.com/user-attachments/assets/974f9e8a-54d1-4294-b6a6-751173026e24)
