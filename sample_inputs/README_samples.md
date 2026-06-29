# Sample Input Files — For Demo Purposes

These files simulate what a real user would upload to the Digital Twin Factory.
They are realistic but contain NO real personal data or company-sensitive information.

## Files in this folder:

| File | Simulates | Used in Demo |
|------|-----------|--------------|
| `Sample_Claims_SOP_2024.md` | Legacy SOP with outdated steps | Gap Analysis (A2) detects 40% obsolete steps |
| `My_JD_Claims_Handler.md` | Job description + KPIs | Role profiling (A1) |
| `My_Org_Chart.md` | Team structure + stakeholders | Relationship mapping |
| `Who_I_Am_Daily_Workflow.md` | Daily routine with triggers/inputs/outputs | Process mining (A2) |
| `voice_recording_transcript.md` | Transcribed voice note (simulated) | Voice-to-process pipeline |

## Note on .mp3 / .mp4 files
The app.py buttons simulate processing audio/video files. For the demo:
- The "Process Voice Recording" button shows instant success
- The actual SOP upload (`.md` or `.txt`) IS functional — it calls Claude API for real Gap Analysis
- No real audio/video processing is needed for the hackathon demo

## To test the REAL API features:
1. Set your `ANTHROPIC_API_KEY` in `.env`
2. Upload `Sample_Claims_SOP_2024.md` (rename to .txt if needed)
3. Click "Generate My Digital Twin"
4. Watch REAL AI analysis appear (not hardcoded!)
