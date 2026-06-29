# BYO Digital Twin Factory — Team IronFaries

**Zurich Hyper Challenge 2026 | Track: Bring Your Own Use Case**

11 AI agents analyse your job (voice, video, docs) and auto-build a personal Digital Twin in 10 minutes — zero coding. The twin runs 4 daily skills at $0.42/day, self-improves with every correction, and never acts without human approval.

---

## 1. Live Prototype

**Try it now:** [Digital Twin Factory on Streamlit](https://byodigitaltwinfactoryironfaries-skmvxbzlgjxamd6fze5nj7.streamlit.app)

5 tabs: Create My Twin → My Twin Design → Talk to My Twin → Twin's Output → Measure of Success

---

## 2. Prototype Source Code

| File | Description |
|------|-------------|
| [`app.py`](app.py) | Streamlit prototype — 1354 lines of Python |
| [`requirements.txt`](requirements.txt) | Dependencies (`streamlit`, `python-dotenv`) |
| [`.env.example`](.env.example) | Environment variable template |
| [`sample_inputs/`](sample_inputs/) | Sample documents for testing (JD, SOP, Org Chart, etc.) |

**Run locally:**
```bash
pip install -r requirements.txt
streamlit run app.py
```

---

## 3. Submission Deliverables

All deliverables are in the [`submission/`](submission/) folder:

| File | Description |
|------|-------------|
| `IronFaries_Demo_Walkthrough.mp4` | 3-minute demo video |
| `IronFaries_VideoTranscript.md` | Video transcript |
| `IronFaries_Solution_Summary_Deck.pdf` | Pitch deck (PDF) |
| `IronFaries_Solution_Summary_Deck.html` | Pitch deck (HTML — better layout) |
| `IronFaries_Technical_Summary.md` | Full technical documentation |
| `IronFaries_Process_Design_Map.pdf` | End-to-end process flow |
| `IronFaries_GitHub_Repository.url` | Link to this repo |
| `IronFaries_URL_to_Prototype.url` | Link to live prototype |

---

## 4. Supporting Visuals

[`final_slides/`](final_slides/) — 8 presentation slide screenshots used in the deck and video.

---

## 5. How This Was Built

Prototype built using **Claude Code** (VS Code extension) as the development tool. Claude Code generates the Python source code (`app.py`); no traditional coding required — citizen developer workflow.

---

## Team

- **Gigi Ma** — AI Evangelist, Zurich Insurance Hong Kong
