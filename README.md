# ⬡ Deadlock Analysis Simulator

A desktop application for visualizing and simulating OS deadlock concepts — built with Python, Tkinter, NetworkX, and Matplotlib.

> 🎓 Mini Project — developed as a team of 3 for an Operating Systems course.

---

## 👥 Team

| Name | Role |
|------|------|
| **Karthik S** | Algorithm Logic & Backend |
| **Logesh S** | UI Design & Theme System |
| **Aathi Krishnan M** | Graph Visualization & Animation |

---

## 📌 About

This simulator provides an interactive GUI to understand two fundamental OS deadlock concepts:

- **Banker's Algorithm** — checks whether a system is in a safe state by computing a safe execution sequence
- **Deadlock Detection Algorithm** — identifies which processes are deadlocked by analyzing resource allocation and request matrices

Both algorithms are visualized step-by-step on a live **Resource Allocation Graph (RAG)**, making it easier to understand how the system state evolves during execution.

---

## ✨ Features

### Algorithms
- **Banker's Algorithm** — computes the Need matrix, finds a safe sequence, and confirms system safety
- **Deadlock Detection** — identifies deadlocked processes that can never complete given current allocations

### Visualization
- Live **Resource Allocation Graph** with directed edges between processes and resources
- Color-coded nodes — green (active), orange (executing), red (deadlocked), gray (finished), blue (resource)
- **Bidirectional edge separation** — allocation and request edges between the same pair arc in opposite directions to avoid overlap
- Edge weight labels with background boxes for readability
- Auto-scaling node sizes and font sizes based on graph density

### Input & Usability
- Manual matrix entry with live **Need Matrix** preview (updates as you type)
- **Random Fill** — auto-generates valid random values respecting constraints
- **4 built-in presets** — Safe State, Unsafe State, Deadlock Detected, No Deadlock
- Input validation with clear error messages (e.g., allocation > total, max < allocation)

### Execution Modes
- **Auto animation** — steps through the execution sequence with 1.2s delay between steps
- **Step-by-Step mode** — manually advance each execution step using a "Next Step" button

### UI & Extras
- **Dark / Light theme toggle** (GitHub-style dark theme by default)
- Color-coded execution log (green = success, red = error, orange = warning, blue = info)
- Resource utilization stats bar showing available resources and % utilization per resource
- **Export log** — save the execution log to a `.txt` file
- Status bar with live clock
- Scrollable matrix area to handle large inputs

---

## 🖥️ Requirements

- Python 3.8+
- `tkinter` (usually bundled with Python)
- `networkx`
- `matplotlib`

Install dependencies:

```bash
pip install networkx matplotlib
```

---

## 🚀 Running the App

```bash
python deadlock_simulator.py
```

---

## 🧭 How to Use

### Banker's Algorithm
1. Select **Banker's** mode
2. Enter number of processes and resources, click **Generate**
3. Fill in the **Allocation** and **Max Claim** matrices
4. Enter **Total Resources**
5. Click **▶ Run** — the app computes the Need matrix, checks safety, and animates the safe sequence

### Deadlock Detection
1. Select **Detection** mode
2. Enter processes and resources, click **Generate**
3. Fill in the **Allocation** and **Request** matrices
4. Enter **Total Resources**
5. Click **▶ Run** — the app identifies deadlocked processes and animates executable ones

### Presets
Click the **Preset** dropdown and select any example to instantly load a pre-filled scenario.

---

## 📐 Algorithm Overview

### Banker's Algorithm (Safety Check)
```
Need[i][j] = Max[i][j] - Allocation[i][j]

While processes remain unfinished:
    Find process Pi where Need[i] <= Work
    Work = Work + Allocation[i]
    Mark Pi as finished

If all processes finish → SAFE STATE
Else → UNSAFE STATE
```

### Deadlock Detection
```
Work = Available

While unfinished processes exist:
    Find process Pi where Request[i] <= Work
    Work = Work + Allocation[i]
    Mark Pi as finished

Unfinished processes → DEADLOCKED
```

---

## 📁 Project Structure

```
deadlock-simulator/
├── deadlock_simulator.py   # Main application (single file)
└── README.md
```

---

## 📸 Screenshots


## 📸 Graph Color Legend

| Color | Meaning |
|-------|---------|
| 🟢 Green circle | Active process |
| 🟠 Orange circle | Currently executing process |
| 🔴 Red circle | Deadlocked process |
| ⬛ Gray circle | Finished process |
| 🔵 Blue square | Resource node |

---

## 📝 License

This project was built for academic purposes as part of an Operating Systems mini project.
