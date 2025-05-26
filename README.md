# PythonProfiler

# PythonProfiler

Light-weight, decorator-based **time & memory profiler** that streams events to a central TCP server.  
Add `@time_profile` or `@memory_profile` to any Python function and get a unified, time-ordered trace across multiple scripts, processes, or hosts without installing heavyweight agents or sharing files.
![image](https://github.com/user-attachments/assets/0e3f7a74-de75-4c52-9826-9d0c21f9de36)


---

## ✨ Features

|                                   | What it does | Why it matters |
|-----------------------------------|--------------|----------------|
| **Two-line integration** | `from logic.decorators import ProfilingDecorators as P` → decorate functions. | Leaves your business-logic untouched; `functools.wraps` keeps signatures & docstrings. |
| **Wall-clock latency** | Captures `datetime.now()` on entry/exit and ships a pair of timestamps. | Perfect for I/O-bound or distributed workflows where “what waited for what?” matters. :contentReference[oaicite:0]{index=0} |
| **Resident-set memory** | Reads `ru_maxrss` via the `resource` module before & after the call. | Spot leaks and unexpected growth at function granularity on Unix systems. :contentReference[oaicite:1]{index=1} |
| **Global ordering** | Every event carries a Version-1 UUID. | Collision-free merging when dozens of clients fire events in parallel. :contentReference[oaicite:2]{index=2} |
| **Zero external deps** | Uses only the Python standard library (`socket`, `uuid`, `resource`, `datetime`). | Works anywhere Python ≥ 3.8 runs. |

---

## Quick start

```bash
git clone https://github.com/Saher-Amasha/PythonProfiler.git

cd PythonProfiler
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt     # only std-lib, but black & pytest for dev helpers

```
