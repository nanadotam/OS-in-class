# BACKEND INTEGRATION_GUIDE.md

## 📌 Overview

This document explains how the **frontend team** can connect the PyQt5 GUI with the **memory allocation backend simulator**.
The backend is implemented in `memory_backend.py` (or whichever file you place it in).
The frontend can call the backend using the **`MemorySimulator`** class and its helper methods.

---

## 🔧 Importing the Backend

At the top of your frontend file (e.g., `memory_simulator.py`), import the backend:

```python
from memory_backend import MemorySimulator
```

If the backend is in the same directory, this will work as-is.
If it’s in a subfolder (e.g., `backend/memory_backend.py`), then:

```python
from backend.memory_backend import MemorySimulator
```

---

## 🏗️ Initializing the Simulator

Create an instance of the simulator in your main window or controller class:

```python
# jobs and memory should be provided from backend file or copied in
from memory_backend import MemorySimulator, jobs, memory  

self.simulator = MemorySimulator(jobs, memory)
```

This initializes the simulator with a job list and memory partitions.

---

## ▶️ Running Simulations

There are **two main ways** to run simulations:

### 1. **Full Simulation (Auto-run)**

```python
self.simulator.reset_memory()
self.simulator.run_simulation(strategy="first_fit")   # or "best_fit"
```

This will run the **entire simulation** until completion.

---

### 2. **Step Simulation (Frontend Control)**

Used when the GUI is stepping through time (e.g., Play/Pause/Step buttons):

```python
self.simulator.simulate_step(strategy="first_fit")
```

This advances the simulation **one step forward**.
Useful when connecting to `QTimer` or custom simulation loops in PyQt.

---

## 📊 Fetching State for UI Updates

The frontend can query the simulator for state updates to refresh widgets, tables, and charts.

### Get memory blocks

```python
memory_state = self.simulator.get_memory_state()
```

Each block looks like:

```python
{
  'block': 1,
  'size': 9500,
  'status': 'free' or 'occupied',
  'job': {...} or None,
  'internal_fragmentation': 0
}
```

---

### Get job states

```python
jobs_state = self.simulator.get_jobs_state()
```

Each job includes:

```python
{
  'stream': 1,
  'time': 5,
  'size': 5760,
  'status': 'waiting' | 'queued' | 'running' | 'completed',
  'wait_time': int,
  'allocated_block': None or block_id
}
```

---

### Get waiting queue

```python
waiting_jobs = self.simulator.get_waiting_jobs()
```

---

### Get completed jobs

```python
completed = self.simulator.get_completed_jobs()
```

---

### Get performance metrics

```python
metrics = self.simulator.get_metrics()
```

This returns:

```python
{
  "throughput": float,          # Jobs per unit time
  "avg_wait_time": float,       # Average wait time per job
  "waiting_queue_size": int,    # Current jobs in waiting queue
  "completed_jobs": int,        # Total completed jobs
  "total_jobs": int             # Total jobs processed
}
```

---

## 🔄 Resetting the Simulation

Before starting a new run, always reset:

```python
self.simulator.reset_memory()
```

---

## ⚡ Quick Example

```python
# Inside frontend step loop
self.simulator.simulate_step("First Fit")

# Update charts and tables
memory_state = self.simulator.get_memory_state()
jobs_state = self.simulator.get_jobs_state()
metrics = self.simulator.get_metrics()

# Example: update GUI labels
self.time_label.setText(f"Time: {self.simulator.current_time}")
self.stats_text.setPlainText(f"Throughput: {metrics['throughput']:.2f}")
```

---

## ✅ Key Notes

* Backend **does not depend on PyQt5** — it only exposes plain Python functions.
* Frontend is responsible for calling `.simulate_step()` or `.run_simulation()` depending on how interactive the GUI should be.
* Metrics like **fragmentation %, memory utilization, block usage** can be computed in frontend (or moved to backend if needed).
