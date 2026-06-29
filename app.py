import streamlit as st
import streamlit.components.v1 as components
import time
import os

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

HAS_API = False

st.set_page_config(page_title="Digital Twin Factory | Zurich AI", page_icon="🧬", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""<style>
.stApp { background-color: #0a0a0f; color: #e0e0e0; }
.stTabs [data-baseweb="tab-list"] { gap: 4px; }
.stTabs [data-baseweb="tab"] { background-color: #1a1a2e; border-radius: 8px; padding: 8px 14px; color: #fff; font-weight: 600; font-size: 12px; }
.stTabs [aria-selected="true"] { background-color: #0066cc; }
.agent-step { background: #0d0d1a; border-left: 3px solid #0099ff; padding: 8px 12px; margin: 4px 0; border-radius: 4px; font-size: 12px; color: #ccc; }
.whitebox { background: #1a1a2e; border: 1px solid #333; border-radius: 10px; padding: 14px; margin: 8px 0; }
.arch-card { border-radius: 10px; padding: 14px; text-align: left; }
.arch-reject { background: #1a0a0a; border: 2px solid #ff4444; }
.arch-mid { background: #1a1a0a; border: 2px solid #ff9900; }
.arch-accept { background: #0a1a0a; border: 2px solid #00ff88; }
.metric-card { background: linear-gradient(135deg, #1a1a2e 0%, #0d0d1a 100%); border: 1px solid #333; border-radius: 10px; padding: 14px; text-align: center; }
.email-card { background: #111122; border: 1px solid #2a2a3e; border-radius: 8px; padding: 10px; margin: 5px 0; font-size: 12px; }
.skill-card { background: #0d1a2e; border: 1px solid #0066cc; border-radius: 10px; padding: 12px; margin: 6px 0; }
.chat-msg { border-radius: 10px; padding: 12px; margin: 6px 0; font-size: 13px; }
.chat-user { background: #1a2a1a; border: 1px solid #00ff88; }
.chat-twin { background: #1a1a2e; border: 1px solid #0099ff; }
.success-msg { background: #0a2e0a; border: 2px solid #00ff88; border-radius: 10px; padding: 16px; text-align: center; margin: 10px 0; }
.urgent-card { background: #2e0a0a; border: 2px solid #ff4444; border-radius: 10px; padding: 12px; margin: 8px 0; }
h1, h2, h3 { color: #ffffff; }
.stButton > button { background: linear-gradient(90deg, #0066cc, #0099ff); color: white; border: none; border-radius: 8px; padding: 10px 20px; font-weight: 600; font-size: 14px; }
.stButton > button:hover { background: linear-gradient(90deg, #0099ff, #00ccff); }
</style>""", unsafe_allow_html=True)

# --- Session State ---
if "phase" not in st.session_state:
    st.session_state.phase = "idle"
if "clarify_step" not in st.session_state:
    st.session_state.clarify_step = 0
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# --- Hidden demo trigger via URL param ?demo=1 ---
if st.query_params.get("demo") == "1" and st.session_state.phase == "idle":
    st.session_state.phase = "complete"
    st.rerun()

st.markdown("## 🧬 Digital Twin Factory")
st.markdown("*11 Factory Agents build my personal AI twin — in minutes, not months.*")
st.markdown("---")

tab1, tab2, tab3, tab4, tab5 = st.tabs(["🏭 Create My Twin", "🤖 My Twin Design", "💬 Talk to My Twin", "📋 Twin's Output", "📊 Measure of Success"])

# --- Auto-jump to tab via JS ---
if "jump_tab" in st.session_state and st.session_state.jump_tab is not None:
    tab_idx = st.session_state.jump_tab
    st.session_state.jump_tab = None
    components.html(f"""<script>
    var tabs = window.parent.document.querySelectorAll('[data-baseweb="tab"]');
    if (tabs.length > {tab_idx}) {{ tabs[{tab_idx}].click(); }}
    </script>""", height=0)

# ==========================================
# TAB 1: CREATE MY TWIN
# ==========================================
with tab1:
    st.markdown("### 📥 Teach the Factory About Me")
    st.markdown("*Choose my style: dump everything at once, or answer step-by-step.*")

    # --- MODE SELECTOR ---
    if "teach_mode" not in st.session_state:
        st.session_state.teach_mode = "guided"
    col_mode1, col_mode2 = st.columns(2)
    with col_mode1:
        if st.button("🚀 Quick Mode", key="btn_quick", type="primary" if st.session_state.teach_mode == "quick" else "secondary"):
            st.session_state.teach_mode = "quick"
            st.rerun()
    with col_mode2:
        if st.button("📋 Guided Mode", key="btn_guided", type="primary" if st.session_state.teach_mode == "guided" else "secondary"):
            st.session_state.teach_mode = "guided"
            st.rerun()
    mode = "Quick" if st.session_state.teach_mode == "quick" else "Guided"

    if "Quick" in mode:
        st.markdown("""<div class="whitebox" style="border-color:#00ff88;">
<h6 style="color:#00ff88; margin:0;">🚀 Quick Mode</h6>
<p style="font-size:11px; color:#888;">Upload anything — SOPs, JDs, org charts, voice notes, screen recordings, handover files. Even messy is fine.<br/>
The 11 Factory Agents will analyze everything and figure out my role, processes, and how to build my twin.</p>
</div>""", unsafe_allow_html=True)

        st.file_uploader("📦 Drop all my files here (any format, any order):",
                         type=["pdf", "docx", "txt", "md", "png", "jpg", "mp4", "mp3", "wav", "mov", "xlsx", "pptx"],
                         accept_multiple_files=True, key="quick_upload")
        st.markdown('<p style="font-size:10px; color:#888;">Examples: JD_ClaimsManager.pdf, SOP.pdf, workflow_diagram.png, Handover_File.docx, org_chart.png, my_voice_note.mp3, process_walkthrough.mp4</p>', unsafe_allow_html=True)

        col_qv, col_qr, col_qe = st.columns(3)
        with col_qv:
            if st.button("🎤 Record voice of what I do", key="quick_voice"):
                st.success("✅ 2m 15s recorded — Factory Agents will extract everything from this")
            st.markdown('<p style="font-size:10px; color:#888;">Cantonese/English OK! Just talk naturally: who I am, what I do, how my day looks.</p>', unsafe_allow_html=True)
        with col_qr:
            if st.button("🖥️ Record my screen (job shadow)", key="quick_screen"):
                st.success("✅ 5m 30s recorded — Factory Agents will learn my workflow by watching")
            st.markdown('<p style="font-size:10px; color:#888;">Let the Factory Agent watch how I work — like training a new hire.</p>', unsafe_allow_html=True)
        with col_qe:
            if st.button("📧 Connect My Outlook", key="quick_email"):
                st.success("✅ Connected! 847 emails indexed. My tone + patterns learned.")
            st.markdown('<p style="font-size:10px; color:#888;">Twin learns my reply style, VIP contacts, common phrases.</p>', unsafe_allow_html=True)

        st.markdown('<p style="font-size:10px; color:#ff9900;">⚠️ Quick mode works great! Results may need 1-2 more clarification questions from the Factory Agents.</p>', unsafe_allow_html=True)

    else:
        # --- Q1: WHO AM I ---
        st.markdown("""<div class="whitebox" style="border-color:#0099ff;">
<h6 style="color:#0099ff; margin:0;">Q1. 👤 Who Am I?</h6>
<p style="font-size:11px; color:#888;">My role, mission, KPIs, what success looks like.</p>
</div>""", unsafe_allow_html=True)

        col_q1a, col_q1b = st.columns([2, 1])
        with col_q1a:
            st.text_area("✍️ Describe myself (Cantonese or English):",
                         placeholder='Example: "I am Sarah Chen, Manager of Commercial Claims. My mission is to process claims fairly and fast while maintaining cover ratio above 85%. My KPIs: cycle time <5 days, accuracy >98%, TNPS >60, zero SLA breaches. Success = 40+ cases/week with zero compliance issues."',
                         height=80, key="q1_text")
        with col_q1b:
            st.file_uploader("📄 Upload JD (e.g. JD_ClaimsManager.docx)", type=["pdf", "docx", "txt"], key="q1_jd")
            if st.button("🎤 Record voice of what I do", key="q1_voice"):
                st.success("✅ 45s recorded — role & KPIs extracted")
            st.markdown('<p style="font-size:9px; color:#888;">Cantonese/English OK!</p>', unsafe_allow_html=True)

        # --- Q2: WHO I WORK WITH ---
        st.markdown("""<div class="whitebox" style="border-color:#0099ff;">
<h6 style="color:#0099ff; margin:0;">Q2. 👥 Who Do I Work With?</h6>
<p style="font-size:11px; color:#888;">My boss, team, reporting line, key stakeholders.</p>
</div>""", unsafe_allow_html=True)

        col_q2a, col_q2b = st.columns([2, 1])
        with col_q2a:
            st.text_area("✍️ Describe my team (Cantonese or English):",
                         placeholder='Example: "I report to James Wong (Head of Claims). He cares about cover ratio, fraud, SLA. I manage 3 handlers: Amy, Ben, Carol. I work with Finance, Compliance, and Reinsurance. Key brokers: David Chan, Michael Lee."',
                         height=80, key="q2_text")
        with col_q2b:
            st.file_uploader("🏢 Org Chart (e.g. org_chart.png)", type=["pdf", "png", "xlsx"], key="q2_org")
            if st.button("🎤 Record voice of what I do", key="q2_voice"):
                st.success("✅ 30s recorded — org structure extracted")
            st.markdown('<p style="font-size:9px; color:#888;">Cantonese/English OK!</p>', unsafe_allow_html=True)

        # --- Q3: MY DAY-TO-DAY PROCESSES ---
        st.markdown("""<div class="whitebox" style="border-color:#0099ff;">
<h6 style="color:#0099ff; margin:0;">Q3. 📋 What Are My Day-to-Day Processes?</h6>
<p style="font-size:11px; color:#888;">Add each major task I do. Upload any related docs — SOPs, workflow diagrams, training recordings, handover files.</p>
</div>""", unsafe_allow_html=True)

        num_processes = st.session_state.get("num_processes", 2)

        for i in range(num_processes):
            with st.expander(f"📋 Process {i+1}", expanded=(i == 0)):
                st.text_input("Process name:", placeholder="e.g. Claim Handling, Coverage & Inquiry Email Reply, Reporting & Insights, EXCO Update...", key=f"p{i}_name")
                col_desc, col_voice = st.columns([3, 1])
                with col_desc:
                    st.text_area("Describe (Cantonese or English):",
                                 placeholder='e.g. "Step 1: I receive new claim from CPS inbox. Step 2: I check coverage against policy wording. Step 3: I calculate settlement. Step 4: If >$100K, I escalate to boss. Step 5: I email broker with outcome. Frequency: 8x/day. Output: settled claim + CPS update."',
                                 height=50, key=f"p{i}_desc")
                with col_voice:
                    if st.button("🎤 Record voice of what I do", key=f"p{i}_voice"):
                        st.success("✅ Recorded")
                    st.markdown('<p style="font-size:9px; color:#888;">Cantonese/English OK!</p>', unsafe_allow_html=True)

                st.file_uploader(
                    "📎 Tell me about this workflow (e.g. SOP.pdf, workflow.png, UserManual.docx)",
                    type=["pdf", "md", "txt", "docx", "png", "jpg", "mp4", "mov", "xlsx"],
                    accept_multiple_files=True, key=f"p{i}_files")
                st.markdown('<p style="font-size:9px; color:#ff9900;">💡 Tip: upload example input (e.g. claim_form.pdf) and expected output (e.g. settlement_email.msg) to help the Factory learn your standards</p>', unsafe_allow_html=True)
                col_screen, col_sys = st.columns([1, 1])
                with col_screen:
                    if st.button("🖥️ Record screen (job shadow)", key=f"p{i}_screen"):
                        st.success("✅ Recording saved — Factory Agent will learn by watching me work")
                with col_sys:
                    st.selectbox("💻 Involves which system?", ["Select...", "CPS (Claims)", "Outlook (Email)", "Excel", "SharePoint", "Bordereaux Portal", "HKIO Submission", "Other", "No system"], key=f"p{i}_sys")

        if st.button("➕ Add another process"):
            st.session_state.num_processes = num_processes + 1
            st.rerun()

        # --- Q4: EMAIL ---
        st.markdown("""<div class="whitebox" style="border-color:#0099ff;">
<h6 style="color:#0099ff; margin:0;">Q4. 📧 What Emails Do I Handle Daily?</h6>
<p style="font-size:11px; color:#888;">Connect my mailbox so the twin learns my tone, who I reply fast to, and common phrases.</p>
</div>""", unsafe_allow_html=True)

        col_q4a, col_q4b = st.columns([1, 1])
        with col_q4a:
            if st.button("📧 Connect My Outlook", key="q4_connect"):
                st.success("✅ Connected! 847 emails indexed. My tone + reply patterns learned.")
            st.markdown('<p style="font-size:10px; color:#888;">Twin learns: who I reply fast to, my greeting style, sign-off, common phrases.</p>', unsafe_allow_html=True)
        with col_q4b:
            st.text_area("Or describe my email types (Cantonese/English):",
                         placeholder='Example: "I get ~60 emails/week. Most are brokers asking claim status. VIP brokers get same-day reply. Internal emails from boss, Finance, Compliance."',
                         height=60, key="q4_text")

    if "Guided" in mode:
        if st.button("🚀 Switch to Quick Mode", key="switch_quick"):
            st.session_state.teach_mode = "quick"
            st.rerun()

    st.markdown("---")

    if st.session_state.phase == "idle":
        if st.button("🚀 Generate My Digital Twin", type="primary"):
            st.session_state.phase = "analyzing"
            st.rerun()

    if st.session_state.phase == "analyzing":
        st.markdown("### ⚙️ 11 Factory Agents Working...")

        agent_names = ["#1 Consultant", "#2 Streamliner", "#3 Architect", "#4 Explainer", "#5 Quality",
                       "#6 Builder", "#7 Cost-Benefit", "#8 Profile", "#9 Skills", "#10 Parallel Run", "#11 Orchestrator"]
        status_placeholder = st.empty()
        pb = st.progress(0)
        log_container = st.container()

        steps = [
            (0, "🔍 Agent #1 (Consultant) — Analyzing uploads... Commercial Claims Manager identified"),
            (1, "📋 Agent #2 (Process Streamliner) — Found 4 processes: Claims, Email, Reporting, EXCO"),
            (1, "⚠️ Agent #2 — Process Streamlining: 38% outdated steps detected across SOPs"),
            (4, "🔒 Agent #5 (Compliance) — PII scan: 5 HKIDs, 12 Policy Numbers masked ✅"),
            (2, "🏗️ Agent #3 (Architect) — Evaluating 3 architecture options..."),
            (2, "✅ Agent #3 — Winner: Option C (Orchestrated Skills) — Score 94/100"),
            (6, "💰 Agent #7 (Cost-Benefit) — Projected: 14.5 hrs/wk | pennies/day | ROI 204x"),
            (3, "💡 Agent #4 (Explainer) — Preparing white-box reasoning for review"),
            (7, "📝 Agent #8 (Profile) — Twin Profile generated: tone, thresholds, corrections"),
            (8, "⚡ Agent #9 (Skills) — 4 Skills constructed: Claims, Email, Reporting, EXCO"),
            (4, "✅ Agent #5 (Quality) — Good Agent Criteria: 8/8 PASSED"),
            (10, "🎉 Agent #11 (Factory Orchestrator) — Design complete. Ready for my review!"),
        ]

        completed_agents = set()
        for i, (agent_idx, msg) in enumerate(steps):
            time.sleep(0.5)
            completed_agents.add(agent_idx)
            pb.progress((i + 1) / len(steps))

            status_cells = ""
            for j, name in enumerate(agent_names):
                if j in completed_agents:
                    status_cells += f'<span style="background:#0a2e0a; border:1px solid #00ff88; border-radius:4px; padding:2px 6px; margin:2px; font-size:9px; color:#00ff88; display:inline-block;">✅ {name}</span>'
                elif j == agent_idx:
                    status_cells += f'<span style="background:#1a1a2e; border:1px solid #0099ff; border-radius:4px; padding:2px 6px; margin:2px; font-size:9px; color:#0099ff; display:inline-block; animation:pulse 1s infinite;">⚙️ {name}</span>'
                else:
                    status_cells += f'<span style="background:#0d0d1a; border:1px solid #333; border-radius:4px; padding:2px 6px; margin:2px; font-size:9px; color:#555; display:inline-block;">⏳ {name}</span>'
            status_placeholder.markdown(f'<div style="margin:8px 0; line-height:2;">{status_cells}</div>', unsafe_allow_html=True)

            with log_container:
                st.markdown(f'<div class="agent-step">{msg}</div>', unsafe_allow_html=True)

        st.session_state.phase = "clarify"
        st.session_state.clarify_step = 0
        st.rerun()

    if st.session_state.phase == "clarify":
        st.markdown("---")
        st.markdown("### 🔍 Factory Agent #2 (Process Streamliner) Needs My Input")
        st.markdown("*Confirming which outdated steps to remove before building my twin:*")

        questions = [
            ("📋 **SOP 1 (Claims):** Step 5 'Manual Excel logging' — my recording shows I skip this. Remove?",
             "✅ Remove — CPS already logs it", "🔄 Keep for quarterly audit"),
            ("📋 **SOP 1 (Claims):** Steps 9-10 'Print → Sign → Scan → File'. I use digital sign-off. Remove physical steps?",
             "✅ Remove physical steps", "🔄 Keep for claims >$100K"),
            ("📋 **SOP 3 (Reporting):** 'Manually copy to HKIO template' — auto-populate from CPS?",
             "✅ Auto-generate from data", "🔄 Keep manual (custom commentary)"),
            ("📋 **SOP 4 (EXCO):** I spend ~45min building slides weekly. Auto-generate + I review?",
             "✅ Auto-generate + review", "🔄 Keep manual narrative"),
        ]

        step = st.session_state.clarify_step
        if step < len(questions):
            q, opt_a, opt_b = questions[step]
            st.markdown(f"""<div class="whitebox" style="border-color:#ff9900;">
<p style="color:#ff9900; font-size:11px;">Question {step+1} of {len(questions)}</p>
<p style="font-size:13px;">{q}</p>
</div>""", unsafe_allow_html=True)
            c1, c2 = st.columns(2)
            with c1:
                if st.button(opt_a, key=f"qa_{step}"):
                    st.session_state.clarify_step += 1
                    st.rerun()
            with c2:
                if st.button(opt_b, key=f"qb_{step}"):
                    st.session_state.clarify_step += 1
                    st.rerun()
        else:
            st.markdown("""<div class="success-msg">
<p>✅ All gaps confirmed! My twin design is ready.</p>
</div>""", unsafe_allow_html=True)
            if st.button("➡️ View My Twin Design", type="primary"):
                st.session_state.phase = "designed"
                st.session_state.jump_tab = 1
                st.rerun()


# ==========================================
# TAB 2: MY TWIN DESIGN
# ==========================================
with tab2:
    if st.session_state.phase in ("idle", "analyzing", "clarify"):
        st.info("⏳ Complete Tab 1 first — Factory Agents are still analyzing.")
    else:
        # --- Understanding ---
        st.markdown("### 🪞 How the Factory Understands Me")
        col_role, col_tasks = st.columns([1, 1])
        with col_role:
            st.markdown("""<div class="whitebox">
<p style="font-size:12px;">
👤 <strong>Sarah Chen</strong> — Manager, Commercial Claims<br/>
👥 Team: Amy, Ben, Carol (3 handlers)<br/>
👔 Boss: James Wong (Head of Commercial Claims)<br/><br/>
🎯 <strong>My Core Mission:</strong> Process claims fairly and fast, maintain cover ratio above 85%<br/>
👥 <strong>Team Core Mission:</strong> 40+ cases/week, zero compliance issues, zero SLA breaches<br/><br/>
📊 <strong>My KPIs:</strong> Cycle time &lt;5d • Accuracy &gt;98% • TNPS &gt;60 • Zero SLA breaches<br/>
📈 <strong>My Boss's KPIs:</strong> Cover ratio • Fraud detection rate • SLA compliance • Backlog count • TNPS<br/><br/>
💻 Systems: CPS • Outlook • Excel • SharePoint • Bordereaux Portal
</p>
</div>""", unsafe_allow_html=True)
        with col_tasks:
            st.markdown("""<div class="whitebox">
<p style="font-size:12px;">
📋 <strong>My 4 daily tasks (from SOPs + screen recording):</strong><br/><br/>
⚡ <strong>Task 1: Claim Handling</strong> — triage → coverage → settlement → close<br/>
📧 <strong>Task 2: Coverage & Inquiry Reply</strong> — broker/client emails<br/>
📋 <strong>Task 3: Reporting & Insights</strong> — IA returns, bordereaux, analytics<br/>
📊 <strong>Task 4: EXCO & Boss Prep</strong> — weekly brief, monthly slide
</p>
</div>""", unsafe_allow_html=True)

        # --- Visual: Org Chart + SOP Workflow ---
        st.markdown("---")
        st.markdown("#### 📊 Learnt from My Input")
        st.markdown("*Even from unorganized voice, video, or documents — the Factory turns it into structured knowledge:*")
        col_org, col_sop = st.columns(2)
        with col_org:
            st.markdown("""<div class="whitebox" style="border-color:#0099ff; text-align:center;">
<p style="color:#0099ff; font-size:11px; font-weight:bold; margin-bottom:6px;">🏢 Org Structure (generated from input)</p>
<p style="font-family:monospace; font-size:9px; color:#ccc; line-height:1.8; margin:0;">
┌─────────────────────────────┐<br/>
│  Eric (CEO Greater China)   │<br/>
└──────────────┬──────────────┘<br/>
┌──────────────┴──────────────┐<br/>
│  James Wong (Head Claims)   │<br/>
└──────────────┬──────────────┘<br/>
┌──────────────┴──────────────┐<br/>
│  <span style="color:#00ff88;">Sarah Chen (Me)</span>             │<br/>
└──┬────────┬────────┬────────┘<br/>
┌──┴──┐  ┌──┴──┐  ┌──┴──┐<br/>
│ Amy │  │ Ben │  │Carol│<br/>
└─────┘  └─────┘  └─────┘
</p>
</div>""", unsafe_allow_html=True)
        with col_sop:
            st.markdown("""<div class="whitebox" style="border-color:#ff9900; text-align:center;">
<p style="color:#ff9900; font-size:11px; font-weight:bold; margin-bottom:6px;">📋 Process Flow (generated + streamlined)</p>
<p style="font-family:monospace; font-size:9px; color:#ccc; line-height:1.8; margin:0;">
① New Claim → ② Triage<br/>
→ ③ Coverage Check → ④ Settlement Calc<br/>
→ <span style="color:#ff4444; text-decoration:line-through;">⑤ Manual Excel Log</span> <span style="color:#ff4444;">❌ REMOVED</span><br/>
→ ⑥ Approval/Escalation<br/>
→ <span style="color:#ff4444; text-decoration:line-through;">⑦ Print→Sign→Scan</span> <span style="color:#ff4444;">❌ REMOVED</span><br/>
→ ⑧ Broker Notification → ⑨ Close<br/><br/>
<span style="color:#00ff88;">✅ Optimized: 9 steps → 7 steps (38% friction removed)</span>
</p>
</div>""", unsafe_allow_html=True)

        # --- Architecture Comparison ---
        st.markdown("---")
        st.markdown("### 🏗️ Architecture Options (3 evaluated, 1 selected)")
        col_a, col_b, col_c = st.columns(3)
        with col_a:
            st.markdown("""<div class="arch-card arch-reject">
<p style="font-size:12px;"><strong style="color:#ff4444;">❌ Option A: Single Mega-Prompt</strong> — <span style="color:#ff8888;">34/100</span></p>
<p style="font-family:monospace; font-size:9px; color:#ff8888; margin:4px 0;">
┌───────────────────┐<br/>
│ ONE GIANT PROMPT  │<br/>
│ (does everything) │<br/>
└───────────────────┘
</p>
<p style="font-size:10px; color:#88ff88;">✓ Simplest to build<br/>✓ Single entry point</p>
<p style="font-size:10px; color:#ff8888;">✗ 3000+ tokens/call ($2.80/day)<br/>✗ Forgets context mid-task<br/>✗ Single point of failure</p>
</div>""", unsafe_allow_html=True)
        with col_b:
            st.markdown("""<div class="arch-card arch-mid">
<p style="font-size:12px;"><strong style="color:#ff9900;">❌ Option B: Flat Network</strong> — <span style="color:#ffcc88;">52/100</span></p>
<p style="font-family:monospace; font-size:9px; color:#ffcc88; margin:4px 0;">
┌────┐ ┌────┐ ┌────┐<br/>
│ S1 │↔│ S2 │↔│ S3 │<br/>
└──┬─┘ └──┬─┘ └──┬─┘<br/>
   └──────┼──────┘<br/>
       ┌──┴──┐<br/>
       │ S4  │<br/>
       └─────┘
</p>
<p style="font-size:10px; color:#88ff88;">✓ Agents collaborate freely<br/>✓ Flexible routing</p>
<p style="font-size:10px; color:#ffcc88;">✗ Unpredictable paths<br/>✗ Circular token waste<br/>✗ No quality gate</p>
</div>""", unsafe_allow_html=True)
        with col_c:
            st.markdown("""<div class="arch-card arch-accept">
<p style="font-size:12px;"><strong style="color:#00ff88;">✅ Option C: Orchestrated Skills</strong> — <span style="color:#00ff88;">94/100</span></p>
<p style="font-family:monospace; font-size:9px; color:#88ffaa; margin:4px 0;">
   ┌──────────────┐<br/>
   │ 🎯 Orchestrator│<br/>
   └─┬──┬──┬──┬──┘<br/>
     │  │  │  │<br/>
   ┌─┴┐┌┴─┐┌┴─┐┌┴─┐<br/>
   │S1││S2││S3││S4│<br/>
   └──┘└──┘└──┘└──┘
</p>
<p style="font-size:10px; color:#88ffaa;">✓ Each skill testable alone<br/>✓ $0.42/day (85% cheaper)<br/>✓ Built-in governance<br/>✓ Scales to N skills independently</p>
<p style="font-size:10px; color:#ff8888;">✗ More complex initial setup</p>
</div>""", unsafe_allow_html=True)

        # --- Twin Profile ---
        st.markdown("---")
        st.markdown("### 📝 My Twin Profile")
        st.markdown("*My twin's personality file — it reads this before every action:*")
        st.markdown("""<div class="whitebox" style="border-color:#00ff88; font-family:monospace; font-size:10px; line-height:1.5;">
<span style="color:#888;"># twin_profile.md — Sarah Chen</span><br/><br/>
<span style="color:#00ccff;">role:</span> Manager, Commercial Claims<br/>
<span style="color:#00ccff;">boss:</span> James Wong | <span style="color:#00ccff;">boss_kpis:</span> cover_ratio, fraud_rate, SLA, backlog, TNPS<br/><br/>
<span style="color:#888;"># Thresholds</span><br/>
escalate_to_boss: amount > $100K OR fraud_flag OR SLA_day >= 4<br/>
auto_approve: routine AND amount < $10K AND coverage_clear<br/>
vip_brokers: [David Chan, Michael Lee, Pacific Re] → same-day reply<br/><br/>
<span style="color:#888;"># Communication Style</span><br/>
tone_brokers: casual ("Hi David") | tone_regulators: formal ("Dear Sir")<br/>
boss_format: bullets, KPIs first, cover_ratio always mentioned<br/><br/>
<span style="color:#888;"># Learned Corrections (self-improving)</span><br/>
- 2026-06-10: "bullets not paragraphs for James" → applied ✅<br/>
- 2026-06-12: "cover ratio first in all boss updates" → applied ✅<br/>
- 2026-06-14: "flag ALL water damage claims regardless of amount" → updated ✅
</div>""", unsafe_allow_html=True)

        # --- Skill Breakdown ---
        st.markdown("---")
        st.markdown("### 🛠️ My Twin's 4 Skills")
        st.markdown("*Each skill = 1 task automated. Reasons, plans, decides, self-improves independently:*")

        skills = [
            {"icon": "⚡", "name": "Twin Skill #1: Claim Handling Automation",
             "mission": "End-to-end claim processing — triage to close",
             "trigger": "New claim in CPS", "input": "claim_form.pdf, policy_CL442.pdf, LA_report.pdf, CPS data",
             "output": "Triage decision, settlement calc, approval email, CPS update",
             "reasons": "Cross-checks claim vs policy Clause-by-Clause; flags >$100K or fraud",
             "plans": "Fast-track (<$10K clear) vs investigate (missing docs) vs escalate",
             "decides": "'Case #4415: $55K motor, Day 4/5 → escalate on SLA (not fraud)'",
             "improves": "You: 'all water damage escalate regardless' → threshold updated"},
            {"icon": "📧", "name": "Twin Skill #2: Coverage & Inquiry Reply",
             "mission": "Auto-draft replies to brokers/clients on coverage & status",
             "trigger": "Email with claim/policy reference", "input": "inbox_email.eml, case_data.json, policy.pdf",
             "output": "Draft reply (I approve), CPS status update",
             "reasons": "Detects intent: coverage Q? status check? complaint? Reads sender history",
             "plans": "Coverage Q → policy wording + answer. Status → CPS summary. Complaint → escalate",
             "decides": "'Hi David' not 'Dear Mr Chan' — casual (VIP broker, learned from corrections)",
             "improves": "Edit rate dropped 40% → 12% after 5 corrections to tone"},
            {"icon": "📋", "name": "Twin Skill #3: Reporting & Insights",
             "mission": "Auto-generate IA returns, bordereaux, fraud analytics on schedule",
             "trigger": "Monthly Day 3 (IA) | Quarterly Day 7 (bordereaux)", "input": "cps_export.csv, SharePoint, claims history, fraud log",
             "output": "ia_return.xlsx, bordereaux_Q2.xlsx, fraud summary, insights",
             "reasons": "Checks completeness: all fields, all periods, cross-ref with Finance",
             "plans": "Day 3: generate → Day 4: self-check → Day 5: submit (alerts only if anomaly)",
             "decides": "'3 claims missing Week 2 → auto-pulled from CPS backup → included'",
             "improves": "Regulator rejected Q1 (wrong date format) → learned DD/MM/YYYY permanently"},
            {"icon": "📊", "name": "Twin Skill #4: EXCO Update & Boss Prep",
             "mission": "Weekly boss brief + monthly EXCO leadership slide",
             "trigger": "Thursday 7am (boss 1:1) | Monthly Monday before EXCO", "input": "cps_weekly_kpi.json, case outcomes, handler_performance.xlsx",
             "output": "boss_brief.md (talking points), exco_slide.pptx (data populated)",
             "reasons": "Picks James's top topics: cover ratio → fraud → SLA (from 12 weeks of patterns)",
             "plans": "Structure: Wins → Risks → Asks → Recommendations",
             "decides": "'$180K = APAC proof point → lead with this. Motor backlog = risk with plan'",
             "improves": "I deleted 'team morale' 3x → learned: James doesn't want soft metrics"},
        ]

        for s in skills:
            st.markdown(f"""<div class="skill-card">
<p style="margin:0; font-size:13px;"><strong style="color:#00ccff;">{s['icon']} {s['name']}</strong></p>
<p style="font-size:11px; color:#aaa; margin:2px 0;">{s['mission']}</p>
<table style="width:100%; font-size:10px; color:#ccc; margin:4px 0;">
<tr><td style="padding:2px; width:12%; color:#ff9900;">⏰ Trigger</td><td style="padding:2px;">{s['trigger']}</td><td style="padding:2px; width:12%; color:#00ff88;">📥 Input</td><td style="padding:2px;">{s['input']}</td></tr>
<tr><td style="padding:2px; color:#0099ff;">📤 Output</td><td style="padding:2px;">{s['output']}</td><td></td><td></td></tr>
</table>
<p style="font-size:9px; color:#ff9900; margin:6px 0 2px 0; font-style:italic;">▶ Example of how this skill reasons, plans, decides & self-improves:</p>
<table style="width:100%; font-size:10px; color:#888; margin-top:2px; background:#0a0a14; border-radius:4px;">
<tr>
<td style="padding:4px; width:25%; vertical-align:top;"><span style="color:#00ff88;">🧠 Reasons:</span> {s['reasons']}</td>
<td style="padding:4px; width:25%; vertical-align:top;"><span style="color:#ffcc00;">📋 Plans:</span> {s['plans']}</td>
<td style="padding:4px; width:25%; vertical-align:top;"><span style="color:#0099ff;">⚡ Decides:</span> {s['decides']}</td>
<td style="padding:4px; width:25%; vertical-align:top;"><span style="color:#ff88ff;">🔄 Improves:</span> {s['improves']}</td>
</tr>
</table>
</div>""", unsafe_allow_html=True)

        # --- Self-Review: Good Agent Criteria ---
        st.markdown("---")
        st.markdown("### ✅ Self-Review: Does My Twin Meet 'Good Agent' Criteria?")
        st.markdown("*Factory Agent #5 (Quality Self-Assessor) runs this check automatically before deployment:*")

        st.markdown("""<div class="whitebox" style="border-color:#00ff88; padding:12px;">
<table style="width:100%; font-size:11px; color:#e0e0e0; border-collapse:collapse;">
<tr style="border-bottom:2px solid #00ff88; color:#00ff88;">
<th style="padding:5px; text-align:left;">Criterion</th>
<th style="padding:5px; text-align:center;">Score</th>
<th style="padding:5px;">Evidence</th>
</tr>
<tr style="border-bottom:1px solid #222;">
<td style="padding:5px;">🔄 Reusability</td>
<td style="padding:5px; text-align:center; color:#00ff88; font-weight:bold;">9.5</td>
<td style="padding:5px; color:#aaa;">4 skills independently deployable; Twin Profile portable to any role</td>
</tr>
<tr style="border-bottom:1px solid #222;">
<td style="padding:5px;">⚡ Token Efficiency</td>
<td style="padding:5px; text-align:center; color:#00ff88; font-weight:bold;">9.2</td>
<td style="padding:5px; color:#aaa;">$0.42/day (85% cheaper than mega-prompt); cached profile avoids re-reading</td>
</tr>
<tr style="border-bottom:1px solid #222;">
<td style="padding:5px;">🔒 Security</td>
<td style="padding:5px; text-align:center; color:#00ff88; font-weight:bold;">10</td>
<td style="padding:5px; color:#aaa;">PII masked (HKIDs, policy numbers); no data leaves tenant</td>
</tr>
<tr style="border-bottom:1px solid #222;">
<td style="padding:5px;">🙋 Human Approval</td>
<td style="padding:5px; text-align:center; color:#00ff88; font-weight:bold;">10</td>
<td style="padding:5px; color:#aaa;">Nothing sent without explicit sign-off; MS Teams notifications at every step</td>
</tr>
<tr style="border-bottom:1px solid #222;">
<td style="padding:5px;">📈 Self-Improvement</td>
<td style="padding:5px; text-align:center; color:#00ff88; font-weight:bold;">9.0</td>
<td style="padding:5px; color:#aaa;">Twin Profile stores corrections permanently; edit rate dropped 40%→12%</td>
</tr>
<tr style="border-bottom:1px solid #222;">
<td style="padding:5px;">🛡️ Safety</td>
<td style="padding:5px; text-align:center; color:#00ff88; font-weight:bold;">10</td>
<td style="padding:5px; color:#aaa;">Cannot escalate, send, or submit without human approval</td>
</tr>
<tr style="border-top:2px solid #00ff88;">
<td style="padding:5px; font-weight:bold;">Overall</td>
<td style="padding:5px; text-align:center; color:#00ff88; font-weight:bold; font-size:14px;">9.4/10</td>
<td style="padding:5px; color:#00ff88; font-weight:bold;">✅ APPROVED — meets all Good Agent criteria</td>
</tr>
</table>
</div>""", unsafe_allow_html=True)

        # --- Build Button ---
        st.markdown("---")
        if st.session_state.phase == "designed":
            if st.button("🔨 Confirm & Build My Digital Twin", type="primary"):
                st.session_state.phase = "building"
                st.rerun()

        if st.session_state.phase == "building":
            st.markdown("### ⚙️ Factory Agent #6 — Building...")
            bp = st.progress(0)
            build_steps = [
                "🎯 Building Twin Agent (Orchestrator)... Twin Profile loaded... ✅",
                "⚡ Building Skill #1: Claim Handling... CPS connected... rules mapped... ✅",
                "📧 Building Skill #2: Email Reply... Outlook connected... 847 patterns... ✅",
                "📋 Building Skill #3: Reporting... templates + schedule set... ✅",
                "📊 Building Skill #4: EXCO Prep... KPI sources + boss patterns... ✅",
                "🔒 Agent #5 (Quality): Final check — PII ✅ Human Approval ✅ Budget ✅ All criteria ✅",
                "🎉 Agent #11 (Orchestrator): Twin deployed! 2-week parallel run activated.",
            ]
            for i, s in enumerate(build_steps):
                time.sleep(0.3)
                bp.progress((i + 1) / len(build_steps))
                st.markdown(f'<div class="agent-step">{s}</div>', unsafe_allow_html=True)
            st.balloons()
            st.session_state.phase = "complete"
            time.sleep(0.5)
            st.rerun()

        if st.session_state.phase == "complete":
            st.markdown("""<div class="success-msg">
<h4>🎉 My Digital Twin is LIVE!</h4>
<p style="font-size:12px;">2-week parallel run active — twin works alongside me, I approve everything.</p>
</div>""", unsafe_allow_html=True)
            if st.button("💬 Talk to My Twin →", type="primary"):
                st.session_state.jump_tab = 2
                st.rerun()


# ==========================================
# TAB 3: TALK TO MY TWIN
# ==========================================
with tab3:
    if st.session_state.phase not in ("complete", "designed", "building"):
        st.info("⏳ Complete Tab 1 first — Factory Agents are still building my twin.")
    else:
        st.markdown("### 💬 Chat with My Digital Twin")
        st.markdown("*Ask anything. My twin knows my cases, emails, KPIs, and schedule.*")

        # Chat display
        full_details_note = '<br/><br/><span style="color:#ff9900; font-size:10px; background:#1a1a0a; border:1px solid #ff9900; border-radius:4px; padding:3px 8px; display:inline-block;">📋 Full details by skill → see Twin\'s Output tab (actions awaiting my approval)</span>'
        for msg in st.session_state.chat_history:
            if msg["role"] == "user":
                st.markdown(f'<div class="chat-msg chat-user">🧑 <strong>Me:</strong> {msg["text"]}</div>', unsafe_allow_html=True)
            else:
                if msg.get("new"):
                    st.markdown('<div class="chat-msg chat-twin"><p style="color:#0099ff; margin:0;">🤖 <strong>Twin is thinking...</strong></p></div>', unsafe_allow_html=True)
                    time.sleep(1.5)
                    msg["new"] = False
                st.markdown(f'<div class="chat-msg chat-twin">🤖 <strong>Twin:</strong> {msg["text"]}{full_details_note}</div>', unsafe_allow_html=True)

        if st.session_state.chat_history:
            if st.button("📋 View full details → Twin's Output tab", key="btn_jump_tab4"):
                st.session_state.jump_tab = 3
                st.rerun()

        # Pre-set responses for demo
        demo_responses = {
            "how are we doing?": """📊 <strong>Executive Summary — Monday Morning</strong><br/><br/>
<strong>✅ Good news:</strong> Cover ratio 87% (above 85% target) | Cycle time 3.2 days (best in division) | Zero SLA breaches<br/>
<strong>⚠️ Watch:</strong> Motor backlog at 12 cases (typhoon surge) — clearing plan active (4/day)<br/>
<strong>🚨 Urgent:</strong> Case #4415 ($55K motor) hitting Day 4/5 SLA — escalation to James recommended<br/><br/>
<strong>📬 Overnight:</strong> 8 emails processed (3 drafts ready for you) | 5 cases progressed (2 auto-closed)<br/>
<strong>📋 Reports:</strong> IA monthly return ready for submission (due Thursday)<br/>
<strong>💡 Boss prep:</strong> Thursday 1:1 brief generated — lead with $180K ABC Corp + cover ratio<br/><br/>
<em>💰 I've saved 14.5 hrs this week. Token cost: $0.42/day.</em>""",
            "what's urgent?": """🚨 <strong>1 urgent item:</strong><br/><br/>
⚡ <strong>Case #4415 — Motor $55K — Day 4 of 5 SLA</strong><br/>
→ Twin recommends: Escalate to James now (amount >$50K + SLA pressure)<br/>
→ Escalation email drafted, waiting my approval<br/><br/>
📧 <strong>1 VIP email pending:</strong> David Chan (same-day SLA) — draft ready, needs my review<br/><br/>
Everything else is on track. No fraud flags. Cover ratio stable.""",
            "prep my boss meeting": """💡 <strong>1:1 with James Wong — Thursday 10am</strong><br/><br/>
🏆 <strong>Lead with:</strong> $180K ABC Corp resolved + cover ratio 87% (APAC proof point for Eric's call)<br/>
📈 <strong>KPIs:</strong> Cycle 3.2d ↓ | TNPS 62 ↑ | Backlog 12 ⚠️ | Fraud: 2 flagged<br/>
⚠️ <strong>Risk:</strong> Motor backlog 12 (typhoon) — plan: 4/day with Ben + Carol<br/>
🙋 <strong>Ask:</strong> Onboard Amy + Ben onto Twin | Temp resource if backlog persists | APAC slot July<br/>
💡 <strong>Tip:</strong> James mentioned $180K twice last week — offer 1-slide for Eric's call<br/><br/>
<em>🧠 Reasoning: Cover ratio first (his #1). $180K as lead (he asked twice). Motor flag (he reports to Eric weekly).</em>""",
        }

        # Chat input
        user_input = st.text_input("Ask my twin:", placeholder="How are we doing?", key="chat_input")

        col_send, col_clear = st.columns([1, 4])
        with col_send:
            if st.button("Send 💬"):
                if user_input:
                    st.session_state.chat_history.append({"role": "user", "text": user_input})
                    response = demo_responses.get(user_input.lower().strip().rstrip("?").rstrip(".") + "?",
                               demo_responses.get(user_input.lower().strip(),
                               f"📊 Based on my Twin Profile and today's data:<br/><br/>• 47 cases closed this week (target 40) ✅<br/>• 3 pending my approval<br/>• Cover ratio: 87% | SLA: zero breaches<br/>• Next: Thursday boss 1:1 (brief ready)<br/><br/><em>Ask me about specific cases, emails, or reports for details.</em>"))
                    st.session_state.chat_history.append({"role": "twin", "text": response, "new": True})
                    st.rerun()
        with col_clear:
            if st.button("🗑️ Clear chat"):
                st.session_state.chat_history = []
                st.rerun()

        # Quick prompts
        st.markdown("---")
        st.markdown("**💡 Try asking:**")
        qcol1, qcol2, qcol3 = st.columns(3)
        with qcol1:
            if st.button("☕ How are we doing?"):
                st.session_state.chat_history.append({"role": "user", "text": "How are we doing?"})
                st.session_state.chat_history.append({"role": "twin", "text": demo_responses["how are we doing?"], "new": True})
                st.rerun()
        with qcol2:
            if st.button("🚨 What's urgent?"):
                st.session_state.chat_history.append({"role": "user", "text": "What's urgent?"})
                st.session_state.chat_history.append({"role": "twin", "text": demo_responses["what's urgent?"], "new": True})
                st.rerun()
        with qcol3:
            if st.button("💡 Prep my boss meeting"):
                st.session_state.chat_history.append({"role": "user", "text": "Prep my boss meeting"})
                st.session_state.chat_history.append({"role": "twin", "text": demo_responses["prep my boss meeting"], "new": True})
                st.rerun()


# ==========================================
# TAB 4: TWIN'S OUTPUT
# ==========================================
with tab4:
    if st.session_state.phase not in ("complete", "designed", "building"):
        st.info("⏳ Complete Tab 1 first — Factory Agents are still building my twin.")
    else:
        st.markdown("""<div class="urgent-card">
<p style="margin:0; font-size:12px;">🚨 <strong>Urgent:</strong> Case #4415 ($55K motor, Day 4/5 SLA) — escalation recommended → <em>MS Teams notification sent</em></p>
</div>""", unsafe_allow_html=True)

        sk_brief, sk_boss, sk1, sk2, sk3, sk4 = st.tabs(["☕ Morning Brief", "💡 Boss 1:1", "⚡ Claims", "📧 Email", "📋 Reporting", "📊 EXCO"])

        with sk_brief:
            st.markdown("#### ☕ Morning Brief")

            st.markdown("""<div class="whitebox" style="border-color:#ff4444; padding:12px;">
<h6 style="color:#ff4444; margin:0;">🚨 Urgent / Attention Required</h6>
<table style="width:100%; font-size:11px; color:#e0e0e0; margin-top:6px;">
<tr style="border-bottom:1px solid #333;"><td style="padding:4px; color:#ff4444;">⚡ Case #4415</td><td>Motor $55K — Day 4/5 SLA. Escalate to James NOW.</td><td style="color:#ff9900;">→ Approve escalation</td></tr>
<tr><td style="padding:4px; color:#ff4444;">📧 David Chan</td><td>VIP broker same-day SLA — draft ready</td><td style="color:#ff9900;">→ Review & send</td></tr>
</table>
</div>""", unsafe_allow_html=True)

            st.markdown("""<div class="whitebox" style="border-color:#00ff88; padding:12px;">
<h6 style="color:#00ff88; margin:0;">✅ Work Done (Overnight)</h6>
<table style="width:100%; font-size:11px; color:#ccc; margin-top:6px;">
<tr style="border-bottom:1px solid #222;"><td style="padding:3px; width:20%;">⚡ Claims</td><td>5 processed: 2 auto-closed, 1 docs requested, 2 assigned handlers</td></tr>
<tr style="border-bottom:1px solid #222;"><td style="padding:3px;">📧 Email</td><td>8 emails processed: 2 auto-sent, 3 drafts ready, 3 filed as FYI</td></tr>
<tr style="border-bottom:1px solid #222;"><td style="padding:3px;">📋 Reporting</td><td>IA monthly return (Jun) generated on schedule</td></tr>
<tr><td style="padding:3px;">📊 EXCO</td><td>Boss 1:1 brief generated for Thursday</td></tr>
</table>
</div>""", unsafe_allow_html=True)

            st.markdown("""<div class="whitebox" style="border-color:#0099ff; padding:12px;">
<h6 style="color:#0099ff; margin:0;">📋 Next Steps</h6>
<table style="width:100%; font-size:11px; color:#ccc; margin-top:6px;">
<tr style="border-bottom:1px solid #222;"><td style="padding:3px; width:20%;">⚡ Claims</td><td>Settlement #4412 sign-off • Chase broker #4418 EOD • 3 new claims expected</td></tr>
<tr style="border-bottom:1px solid #222;"><td style="padding:3px;">📧 Email</td><td>Send David Chan reply • Send James backlog update</td></tr>
<tr style="border-bottom:1px solid #222;"><td style="padding:3px;">📋 Reporting</td><td>Submit IA return (due Thu) • Bordereaux Q2 in progress</td></tr>
<tr><td style="padding:3px;">📊 EXCO</td><td>Review boss brief (meeting Thu 10am)</td></tr>
</table>
</div>""", unsafe_allow_html=True)

            st.markdown("""<div class="whitebox" style="border-color:#ff9900; padding:12px;">
<h6 style="color:#ff9900; margin:0;">🙋 Action Required from Me (My Approval Required)</h6>
<table style="width:100%; font-size:11px; color:#e0e0e0; margin-top:6px;">
<tr style="border-bottom:1px solid #222;"><td style="padding:4px; width:5%;">1</td><td style="width:25%;">Approve escalation #4415</td><td style="color:#888;">Claims → James</td><td style="color:#00ff88; font-size:10px;">🔔 MS Teams notified</td></tr>
<tr style="border-bottom:1px solid #222;"><td style="padding:4px;">2</td><td>Sign off settlement #4412</td><td style="color:#888;">Claims → Broker</td><td style="color:#00ff88; font-size:10px;">🔔 MS Teams notified</td></tr>
<tr style="border-bottom:1px solid #222;"><td style="padding:4px;">3</td><td>Review & send 2 email drafts</td><td style="color:#888;">David Chan + James</td><td style="color:#00ff88; font-size:10px;">🔔 MS Teams notified</td></tr>
<tr><td style="padding:4px;">4</td><td>Approve IA return submission</td><td style="color:#888;">Due Thursday</td><td style="color:#00ff88; font-size:10px;">🔔 MS Teams notified</td></tr>
</table>
</div>""", unsafe_allow_html=True)

        with sk_boss:
            st.markdown("#### 💡 1:1 with James Wong (Head of Commercial Claims)")
            st.markdown('<p style="font-size:11px; color:#888;">Auto-generated based on 12 weeks of meeting patterns • Updated live from CPS + email data</p>', unsafe_allow_html=True)

            st.markdown("""<div class="whitebox" style="border-color:#00ff88; padding:12px;">
<h6 style="color:#00ff88; margin:0;">🏆 Achievements This Period</h6>
<table style="width:100%; font-size:11px; color:#e0e0e0; margin-top:6px;">
<tr style="border-bottom:1px solid #222;"><td style="padding:4px;">$180K ABC Corp claim resolved — APAC proof point for Eric's call</td></tr>
<tr style="border-bottom:1px solid #222;"><td style="padding:4px;">Cover ratio 87% (target 85%) — best in 6 months</td></tr>
<tr style="border-bottom:1px solid #222;"><td style="padding:4px;">Cycle time 3.2 days (target 5) — division leading</td></tr>
<tr><td style="padding:4px;">TNPS 62 (target 60) — steady improvement</td></tr>
</table>
</div>""", unsafe_allow_html=True)

            st.markdown("""<div class="whitebox" style="border-color:#0099ff; padding:12px;">
<h6 style="color:#0099ff; margin:0;">🎯 Focus Next Period</h6>
<table style="width:100%; font-size:11px; color:#e0e0e0; margin-top:6px;">
<tr style="border-bottom:1px solid #222;"><td style="padding:4px;">Clear motor backlog (12 cases → 0) — typhoon surge, plan 4/day with Ben + Carol</td></tr>
<tr style="border-bottom:1px solid #222;"><td style="padding:4px;">Bordereaux Q2 submission (due Jul 10)</td></tr>
<tr><td style="padding:4px;">Onboard Amy + Ben onto Digital Twin (parallel run)</td></tr>
</table>
</div>""", unsafe_allow_html=True)

            st.markdown("""<div class="whitebox" style="border-color:#ff9900; padding:12px;">
<h6 style="color:#ff9900; margin:0;">💬 Topics to Discuss</h6>
<table style="width:100%; font-size:11px; color:#e0e0e0; margin-top:6px;">
<tr style="border-bottom:1px solid #222;"><td style="padding:4px; width:5%;">1</td><td>Motor backlog risk — request temp resource if not cleared by Fri</td></tr>
<tr style="border-bottom:1px solid #222;"><td style="padding:4px;">2</td><td>$180K ABC Corp as APAC showcase — offer 1-slide for Eric's Tuesday call</td></tr>
<tr><td style="padding:4px;">3</td><td>Digital Twin pilot results — 14.5 hrs/wk saved, propose team rollout</td></tr>
</table>
</div>""", unsafe_allow_html=True)

            st.markdown("""<div class="whitebox" style="border-color:#ff88ff; padding:12px;">
<h6 style="color:#ff88ff; margin:0;">🙋 Support Required from You</h6>
<table style="width:100%; font-size:11px; color:#e0e0e0; margin-top:6px;">
<tr style="border-bottom:1px solid #222;"><td style="padding:4px; width:5%;">1</td><td>Approve Twin onboarding for Amy + Ben</td></tr>
<tr style="border-bottom:1px solid #222;"><td style="padding:4px;">2</td><td>Temp resource approval (if backlog persists beyond Fri)</td></tr>
<tr><td style="padding:4px;">3</td><td>APAC showcase slot — July (nominate our team)</td></tr>
</table>
</div>""", unsafe_allow_html=True)

            st.markdown('<p style="font-size:10px; color:#888;">🧠 <em>Twin reasoning: Cover ratio first (James\'s #1 KPI). $180K lead (he asked twice last week). Motor flag because he reports to Eric weekly.</em></p>', unsafe_allow_html=True)
            st.markdown('<p style="font-size:10px; color:#00ff88;">🔔 MS Teams notification sent — brief ready for review</p>', unsafe_allow_html=True)

        with sk1:
            st.markdown("#### ⚡ Skill #1: Claim Handling")
            st.markdown('<p style="font-size:11px; color:#888;">Per-case status • SOP step tracking • My Approval Required actions highlighted</p>', unsafe_allow_html=True)

            st.markdown("""<div class="whitebox" style="padding:8px; overflow-x:auto;">
<table style="width:100%; font-size:10px; color:#e0e0e0; border-collapse:collapse;">
<tr style="border-bottom:2px solid #0099ff; color:#0099ff;">
<th style="padding:5px; text-align:left;">Case</th>
<th style="padding:5px;">Type / Amount</th>
<th style="padding:5px;">SOP Step</th>
<th style="padding:5px;">Work Done</th>
<th style="padding:5px;">Next Step</th>
<th style="padding:5px;">Attention</th>
<th style="padding:5px; color:#ff9900;">🙋 My Approval</th>
<th style="padding:5px;">Status</th>
</tr>
<tr style="border-bottom:1px solid #222; background:#2e0a0a;">
<td style="padding:5px; color:#ff4444; font-weight:bold;">#4415</td>
<td style="padding:5px;">Motor $55K</td>
<td style="padding:5px;">Step 4/7</td>
<td style="padding:5px;">Coverage verified, LA report reviewed</td>
<td style="padding:5px;">Escalate to James (amount + SLA)</td>
<td style="padding:5px; color:#ff4444;">🚨 Day 4/5 SLA</td>
<td style="padding:5px; color:#ff9900; font-weight:bold;">Approve escalation</td>
<td style="padding:5px; color:#ff4444;">⚠️ URGENT</td>
</tr>
<tr style="border-bottom:1px solid #222;">
<td style="padding:5px; font-weight:bold;">#4412</td>
<td style="padding:5px;">Property $42K</td>
<td style="padding:5px;">Step 6/7</td>
<td style="padding:5px;">ABC Corp — settlement calculated $42K</td>
<td style="padding:5px;">Issue settlement to broker</td>
<td style="padding:5px; color:#ff9900;">Amount >$10K</td>
<td style="padding:5px; color:#ff9900; font-weight:bold;">Sign off settlement</td>
<td style="padding:5px; color:#ff9900;">Pending approval</td>
</tr>
<tr style="border-bottom:1px solid #222;">
<td style="padding:5px;">#4418</td>
<td style="padding:5px;">Property $12K</td>
<td style="padding:5px;">Step 2/7</td>
<td style="padding:5px;">Initial triage done, docs incomplete</td>
<td style="padding:5px;">Chase broker EOD if no docs</td>
<td style="padding:5px;">—</td>
<td style="padding:5px; color:#888;">None (auto-chase)</td>
<td style="padding:5px; color:#0099ff;">In progress</td>
</tr>
<tr style="border-bottom:1px solid #222;">
<td style="padding:5px;">#4419</td>
<td style="padding:5px;">Motor $6K</td>
<td style="padding:5px;">Step 3/7</td>
<td style="padding:5px;">Assigned Carol, coverage check done</td>
<td style="padding:5px;">Carol processes settlement</td>
<td style="padding:5px;">—</td>
<td style="padding:5px; color:#888;">None (delegated)</td>
<td style="padding:5px; color:#0099ff;">In progress</td>
</tr>
<tr style="border-bottom:1px solid #222;">
<td style="padding:5px;">#4420</td>
<td style="padding:5px;">Travel $2K</td>
<td style="padding:5px;">Step 3/7</td>
<td style="padding:5px;">Assigned Amy, routine travel</td>
<td style="padding:5px;">Amy processes (auto-approve eligible)</td>
<td style="padding:5px;">—</td>
<td style="padding:5px; color:#888;">None (delegated)</td>
<td style="padding:5px; color:#0099ff;">In progress</td>
</tr>
<tr style="border-bottom:1px solid #222; background:#0a1a0a;">
<td style="padding:5px; color:#00ff88;">#4405</td>
<td style="padding:5px;">Travel $3K</td>
<td style="padding:5px;">Step 7/7</td>
<td style="padding:5px;">Auto-approved (<$10K, coverage clear)</td>
<td style="padding:5px;">—</td>
<td style="padding:5px;">—</td>
<td style="padding:5px; color:#888;">None</td>
<td style="padding:5px; color:#00ff88;">✅ Closed</td>
</tr>
<tr style="background:#0a1a0a;">
<td style="padding:5px; color:#00ff88;">#4406</td>
<td style="padding:5px;">Home $8K</td>
<td style="padding:5px;">Step 7/7</td>
<td style="padding:5px;">Auto-approved (<$10K, coverage clear)</td>
<td style="padding:5px;">—</td>
<td style="padding:5px;">—</td>
<td style="padding:5px; color:#888;">None</td>
<td style="padding:5px; color:#00ff88;">✅ Closed</td>
</tr>
</table>
</div>""", unsafe_allow_html=True)

            st.markdown("---")
            st.markdown("**🙋 Actions Awaiting My Approval:**")

            col_card1, col_btn1 = st.columns([4, 1])
            with col_card1:
                st.markdown("""<div class="whitebox" style="border-color:#ff4444; padding:8px; margin:0;">
<p style="font-size:11px; margin:0;"><strong style="color:#ff4444;">🚨 #4415</strong> Motor $55K — Day 4/5 SLA — Escalate to James</p>
<p style="font-size:9px; margin:2px 0 0 0; color:#0099ff;">📎 <a href="#" style="color:#0099ff;">Escalation_Email_Draft.md</a> • <a href="#" style="color:#0099ff;">Case_4415_Summary.pdf</a></p>
</div>""", unsafe_allow_html=True)
            with col_btn1:
                if st.button("✅ Approve", key="btn_4415"):
                    st.success("✅ Escalation sent to James. Audit logged. 🔔 MS Teams notified.")

            col_card2, col_btn2 = st.columns([4, 1])
            with col_card2:
                st.markdown("""<div class="whitebox" style="border-color:#ff9900; padding:8px; margin:0;">
<p style="font-size:11px; margin:0;"><strong style="color:#ff9900;">⚠️ #4412</strong> ABC Corp $42K — Settlement calculated — Approve to send to broker</p>
<p style="font-size:9px; margin:2px 0 0 0; color:#0099ff;">📎 <a href="#" style="color:#0099ff;">Settlement_Calc_4412.xlsx</a> • <a href="#" style="color:#0099ff;">Broker_Email_Draft.md</a></p>
</div>""", unsafe_allow_html=True)
            with col_btn2:
                if st.button("✅ Sign off", key="btn_4412"):
                    st.success("✅ Settlement approved. Broker notified. 🔔 MS Teams notified.")

        with sk2:
            st.markdown("#### 📧 Skill #2: Coverage & Inquiry Reply")
            st.markdown('<p style="font-size:11px; color:#888;">Overnight email summary • Draft replies generated • My Approval Required approval</p>', unsafe_allow_html=True)

            st.markdown("""<div class="whitebox" style="padding:8px; overflow-x:auto;">
<h6 style="color:#0099ff; margin:0 0 8px 0;">📬 Overnight Email Summary (8 emails)</h6>
<table style="width:100%; font-size:10px; color:#e0e0e0; border-collapse:collapse;">
<tr style="border-bottom:2px solid #0099ff; color:#0099ff;">
<th style="padding:4px; text-align:left;">Sender</th>
<th style="padding:4px;">Received</th>
<th style="padding:4px;">Subject</th>
<th style="padding:4px;">Content Summary</th>
<th style="padding:4px;">Question Asked</th>
<th style="padding:4px;">Draft Reply Summary</th>
<th style="padding:4px; color:#ff9900;">🙋 Action</th>
</tr>
<tr style="border-bottom:1px solid #222; background:#2e0a0a;">
<td style="padding:4px; font-weight:bold;">David Chan</td>
<td style="padding:4px;">Mon 08:12</td>
<td style="padding:4px;">ABC Corp $42K coverage</td>
<td style="padding:4px;">Asking what's covered under policy CL442</td>
<td style="padding:4px; color:#ff9900;">Items 1-4 covered?</td>
<td style="padding:4px;">Items 1-3 confirmed, Item 4 (BI) excluded Clause 7.2, offer endorsement</td>
<td style="padding:4px; color:#ff9900; font-weight:bold;">Review & Send</td>
</tr>
<tr style="border-bottom:1px solid #222; background:#1a1a0a;">
<td style="padding:4px; font-weight:bold;">James Wong</td>
<td style="padding:4px;">Mon 07:45</td>
<td style="padding:4px;">Motor backlog update?</td>
<td style="padding:4px;">Wants status on typhoon backlog</td>
<td style="padding:4px; color:#ff9900;">How many? Plan?</td>
<td style="padding:4px;">12 cases, Day 3/5 oldest, 4/day plan, #4415 flag, cover 87%</td>
<td style="padding:4px; color:#ff9900; font-weight:bold;">Review & Send</td>
</tr>
<tr style="border-bottom:1px solid #222; background:#0a1a0a;">
<td style="padding:4px;">AIA Reinsurance</td>
<td style="padding:4px;">Sun 22:10</td>
<td style="padding:4px;">Q2 treaty renewal</td>
<td style="padding:4px;">Routine renewal confirmation</td>
<td style="padding:4px; color:#888;">None</td>
<td style="padding:4px; color:#00ff88;">Auto-sent ✅</td>
<td style="padding:4px; color:#00ff88;">None</td>
</tr>
<tr style="border-bottom:1px solid #222; background:#0a1a0a;">
<td style="padding:4px;">HR</td>
<td style="padding:4px;">Sun 18:30</td>
<td style="padding:4px;">Training cert request</td>
<td style="padding:4px;">Routine cert confirmation</td>
<td style="padding:4px; color:#888;">None</td>
<td style="padding:4px; color:#00ff88;">Auto-sent ✅</td>
<td style="padding:4px; color:#00ff88;">None</td>
</tr>
<tr style="border-bottom:1px solid #222;">
<td style="padding:4px; color:#888;">Finance</td>
<td style="padding:4px;">Sun 16:00</td>
<td style="padding:4px;">Q2 reserve update</td>
<td style="padding:4px;">FYI — quarterly reserve numbers</td>
<td style="padding:4px; color:#888;">None</td>
<td style="padding:4px; color:#888;">Filed as FYI 📁</td>
<td style="padding:4px; color:#888;">None</td>
</tr>
<tr style="border-bottom:1px solid #222;">
<td style="padding:4px; color:#888;">Compliance</td>
<td style="padding:4px;">Sun 14:22</td>
<td style="padding:4px;">PII audit reminder</td>
<td style="padding:4px;">FYI — monthly reminder</td>
<td style="padding:4px; color:#888;">None</td>
<td style="padding:4px; color:#888;">Filed as FYI 📁</td>
<td style="padding:4px; color:#888;">None</td>
</tr>
<tr style="border-bottom:1px solid #222;">
<td style="padding:4px; color:#888;">Pacific Re</td>
<td style="padding:4px;">Sat 09:15</td>
<td style="padding:4px;">Case #4405 closed</td>
<td style="padding:4px;">FYI — acknowledgment of closure</td>
<td style="padding:4px; color:#888;">None</td>
<td style="padding:4px; color:#888;">Filed as FYI 📁</td>
<td style="padding:4px; color:#888;">None</td>
</tr>
<tr style="background:#1a1a0a;">
<td style="padding:4px;">Michael Lee</td>
<td style="padding:4px;">Sat 08:00</td>
<td style="padding:4px;">New submission — motor</td>
<td style="padding:4px;">New claim, routed to Skill #1</td>
<td style="padding:4px; color:#888;">None</td>
<td style="padding:4px;">Auto-acknowledged, case #4420 created</td>
<td style="padding:4px; color:#00ff88;">None</td>
</tr>
</table>
</div>""", unsafe_allow_html=True)

            st.markdown("---")
            st.markdown("**📝 Draft Replies Awaiting My Approval:**")

            st.markdown("""<div class="email-card" style="border-color:#ff4444;">
<p style="margin:0;"><strong style="color:#ff4444;">🔴 Priority:</strong> David Chan (VIP — same-day SLA)</p>
<p style="color:#ccc; font-size:11px; background:#0a0a1a; padding:8px; border-radius:4px; margin:4px 0;">
"Hi David, Coverage confirmed items 1-3 (fire, theft, water). Item 4 (BI) excluded per Clause 7.2. Happy to quote endorsement within 24hrs. Best, Sarah"</p>
<p style="font-size:9px; color:#888;">🧠 VIP broker → casual tone ("Hi David" not "Dear Mr Chan"). Coverage from policy_CL442.pdf Clause 7.2.</p>
</div>""", unsafe_allow_html=True)
            c1a, c1b = st.columns([1, 1])
            with c1a:
                if st.button("✅ Approve & Send", key="email_david"):
                    st.success("✅ Sent to David Chan. 🔔 MS Teams notified.")
            with c1b:
                if st.button("✏️ Edit (trains twin)", key="edit_david"):
                    st.info("Your edits will permanently improve my twin's tone.")

            st.markdown("""<div class="email-card" style="border-color:#ff9900;">
<p style="margin:0;"><strong style="color:#ff9900;">🟡 Normal:</strong> James Wong (Boss)</p>
<p style="color:#ccc; font-size:11px; background:#0a0a1a; padding:8px; border-radius:4px; margin:4px 0;">
"Hi James, Motor backlog: 12 cases, oldest Day 3/5. Plan: 4/day (Ben+Carol). Flag: #4415 $55K Day 4. Cover ratio 87%. Sarah"</p>
<p style="font-size:9px; color:#888;">🧠 Boss → short bullets, KPIs first, cover ratio always mentioned (learned preference).</p>
</div>""", unsafe_allow_html=True)
            c2a, c2b = st.columns([1, 1])
            with c2a:
                if st.button("✅ Approve & Send", key="email_james"):
                    st.success("✅ Sent to James. 🔔 MS Teams notified.")
            with c2b:
                if st.button("✏️ Edit (trains twin)", key="edit_james"):
                    st.info("Your edits will permanently improve my twin's style.")

            st.markdown('<p style="font-size:10px; color:#00ff88;">🔔 MS Teams notifications sent — drafts awaiting my review</p>', unsafe_allow_html=True)

        with sk3:
            st.markdown("#### 📋 Skill #3: Reporting & Insights")
            st.markdown('<p style="font-size:11px; color:#888;">Automated report generation • Schedule-driven • Key insights extracted for EXCO memo</p>', unsafe_allow_html=True)

            st.markdown("""<div class="whitebox" style="padding:8px; overflow-x:auto;">
<table style="width:100%; font-size:10px; color:#e0e0e0; border-collapse:collapse;">
<tr style="border-bottom:2px solid #0099ff; color:#0099ff;">
<th style="padding:5px; text-align:left;">Report</th>
<th style="padding:5px;">Frequency</th>
<th style="padding:5px;">Work Done</th>
<th style="padding:5px;">Next Step</th>
<th style="padding:5px; color:#ff9900;">🙋 Action Required</th>
<th style="padding:5px;">Key Insight for EXCO</th>
<th style="padding:5px;">Notification</th>
</tr>
<tr style="border-bottom:1px solid #222;">
<td style="padding:5px; font-weight:bold;">IA Return (Jun)</td>
<td style="padding:5px;">Monthly Day 3</td>
<td style="padding:5px; color:#00ff88;">Generated ✅ (all fields, DD/MM/YYYY)</td>
<td style="padding:5px;">Submit to HKIO (due Thu)</td>
<td style="padding:5px; color:#ff9900; font-weight:bold;">Approve & submit</td>
<td style="padding:5px;">47 cases closed, $1.2M settled, 0 SLA breach</td>
<td style="padding:5px; color:#00ff88;">🔔 Teams</td>
</tr>
<tr style="border-bottom:1px solid #222;">
<td style="padding:5px; font-weight:bold;">Fraud Analytics</td>
<td style="padding:5px;">Monthly</td>
<td style="padding:5px; color:#00ff88;">Scanned ✅ — 2 cases flagged</td>
<td style="padding:5px;">Investigation notes this week</td>
<td style="padding:5px; color:#888;">None (auto-flagged)</td>
<td style="padding:5px;">Fraud rate 1.4% (normal range)</td>
<td style="padding:5px; color:#00ff88;">🔔 Teams</td>
</tr>
<tr style="border-bottom:1px solid #222;">
<td style="padding:5px; font-weight:bold;">Bordereaux Q2</td>
<td style="padding:5px;">Quarterly Day 7</td>
<td style="padding:5px; color:#0099ff;">In progress (60% complete)</td>
<td style="padding:5px;">Complete by Jul 7, submit Jul 10</td>
<td style="padding:5px; color:#888;">None yet (auto-generating)</td>
<td style="padding:5px;">Premium income +8% YoY</td>
<td style="padding:5px; color:#888;">—</td>
</tr>
<tr>
<td style="padding:5px; font-weight:bold;">KPI Dashboard</td>
<td style="padding:5px;">Weekly</td>
<td style="padding:5px; color:#00ff88;">Updated ✅</td>
<td style="padding:5px;">Auto-refresh next Mon</td>
<td style="padding:5px; color:#888;">None (automated)</td>
<td style="padding:5px;">Cover ratio 87% ↑ best in 6mo</td>
<td style="padding:5px; color:#888;">—</td>
</tr>
</table>
</div>""", unsafe_allow_html=True)

            st.markdown("---")
            col_rpt, col_rptb = st.columns([4, 1])
            with col_rpt:
                st.markdown('<p style="font-size:11px; color:#ff9900; margin:0;">🙋 <strong>IA Return (Jun)</strong> — ready for HKIO submission (due Thursday)</p>', unsafe_allow_html=True)
            with col_rptb:
                if st.button("✅ Submit", key="btn_ia_submit"):
                    st.success("✅ Submitted to HKIO. Ref: IA-2026-06-001. MS Teams notified.")

            st.markdown("""<div class="whitebox" style="border-color:#00ccff; padding:10px; margin-top:10px;">
<h6 style="color:#00ccff; margin:0;">📊 Key Insights Summary (auto-extracted for EXCO memo)</h6>
<table style="width:100%; font-size:11px; color:#ccc; margin-top:6px;">
<tr style="border-bottom:1px solid #222;"><td style="padding:3px; color:#00ff88;">↑</td><td>Cover ratio 87% — above 85% target, best in 6 months</td></tr>
<tr style="border-bottom:1px solid #222;"><td style="padding:3px; color:#00ff88;">↓</td><td>Cycle time 3.2 days — target 5, division leading</td></tr>
<tr style="border-bottom:1px solid #222;"><td style="padding:3px; color:#00ff88;">✓</td><td>Fraud rate 1.4% — within normal range</td></tr>
<tr><td style="padding:3px; color:#ff9900;">⚠️</td><td>Motor backlog 12 cases — typhoon surge, clearing plan active</td></tr>
</table>
</div>""", unsafe_allow_html=True)
            st.markdown('<p style="font-size:10px; color:#00ff88;">🔔 MS Teams notification sent — IA return ready for approval</p>', unsafe_allow_html=True)

        with sk4:
            st.markdown("#### 📊 Skill #4: EXCO Update & Boss Prep")
            st.markdown('<p style="font-size:11px; color:#888;">Auto-generated leadership content • Structured by topic • Human review before presentation</p>', unsafe_allow_html=True)

            st.markdown("""<div class="whitebox" style="padding:8px; overflow-x:auto;">
<h6 style="color:#0099ff; margin:0 0 8px 0;">📊 EXCO Monthly Slide (Jun 2026)</h6>
<table style="width:100%; font-size:10px; color:#e0e0e0; border-collapse:collapse;">
<tr style="border-bottom:2px solid #0099ff; color:#0099ff;">
<th style="padding:5px; text-align:left;">Topic</th>
<th style="padding:5px;">Talking Points</th>
<th style="padding:5px;">Work Done</th>
<th style="padding:5px;">Next Step</th>
<th style="padding:5px; color:#ff9900;">🙋 Action</th>
<th style="padding:5px;">Notification</th>
</tr>
<tr style="border-bottom:1px solid #222;">
<td style="padding:5px; font-weight:bold; color:#00ff88;">1. Performance</td>
<td style="padding:5px;">Cover ratio 87% ↑ • Cycle 3.2d ↓ • TNPS 62 ↑ • Zero SLA breach</td>
<td style="padding:5px; color:#00ff88;">Content generated ✅<br/>Slide generated ✅</td>
<td style="padding:5px;">Review narrative</td>
<td style="padding:5px; color:#ff9900;">Review slide</td>
<td style="padding:5px; color:#00ff88;">🔔 Teams</td>
</tr>
<tr style="border-bottom:1px solid #222;">
<td style="padding:5px; font-weight:bold; color:#ff9900;">2. Risks & Actions</td>
<td style="padding:5px;">Motor backlog 12 (typhoon) • Plan: 4/day • Temp resource if needed</td>
<td style="padding:5px; color:#00ff88;">Content generated ✅<br/>Slide generated ✅</td>
<td style="padding:5px;">Confirm plan with James</td>
<td style="padding:5px; color:#ff9900;">Review slide</td>
<td style="padding:5px; color:#00ff88;">🔔 Teams</td>
</tr>
<tr>
<td style="padding:5px; font-weight:bold; color:#0099ff;">3. Innovation</td>
<td style="padding:5px;">Digital Twin pilot: 14.5 hrs/wk saved • $0.42/day • 204x ROI • Team rollout proposal</td>
<td style="padding:5px; color:#00ff88;">Content generated ✅<br/>Slide generated ✅</td>
<td style="padding:5px;">Add Amy/Ben onboard ask</td>
<td style="padding:5px; color:#ff9900;">Review slide</td>
<td style="padding:5px; color:#00ff88;">🔔 Teams</td>
</tr>
</table>
</div>""", unsafe_allow_html=True)

            st.markdown("""<div class="whitebox" style="padding:8px; margin-top:10px; overflow-x:auto;">
<h6 style="color:#0099ff; margin:0 0 8px 0;">💡 Boss 1:1 Brief (Weekly — auto-generates Thu 7am)</h6>
<table style="width:100%; font-size:10px; color:#e0e0e0; border-collapse:collapse;">
<tr style="border-bottom:2px solid #0099ff; color:#0099ff;">
<th style="padding:5px; text-align:left;">Topic</th>
<th style="padding:5px;">Talking Points</th>
<th style="padding:5px;">Work Done</th>
<th style="padding:5px;">Next Step</th>
<th style="padding:5px; color:#ff9900;">🙋 Action</th>
<th style="padding:5px;">Notification</th>
</tr>
<tr style="border-bottom:1px solid #222;">
<td style="padding:5px; font-weight:bold;">1. Win</td>
<td style="padding:5px;">$180K ABC Corp resolved — offer as APAC proof point for Eric</td>
<td style="padding:5px; color:#00ff88;">Brief generated ✅</td>
<td style="padding:5px;">Review before meeting</td>
<td style="padding:5px; color:#ff9900;">Review</td>
<td style="padding:5px; color:#00ff88;">🔔 Teams</td>
</tr>
<tr style="border-bottom:1px solid #222;">
<td style="padding:5px; font-weight:bold;">2. Risk</td>
<td style="padding:5px;">Motor backlog + request temp resource</td>
<td style="padding:5px; color:#00ff88;">Brief generated ✅</td>
<td style="padding:5px;">Prepare backup plan</td>
<td style="padding:5px; color:#888;">None</td>
<td style="padding:5px; color:#888;">—</td>
</tr>
<tr>
<td style="padding:5px; font-weight:bold;">3. Ask</td>
<td style="padding:5px;">Twin rollout Amy+Ben • APAC slot July • Temp resource</td>
<td style="padding:5px; color:#00ff88;">Brief generated ✅</td>
<td style="padding:5px;">Confirm asks with James</td>
<td style="padding:5px; color:#ff9900;">Review</td>
<td style="padding:5px; color:#00ff88;">🔔 Teams</td>
</tr>
</table>
</div>""", unsafe_allow_html=True)

            st.markdown("---")
            st.markdown("**🙋 Actions Awaiting My Approval:**")

            col_ex1, col_exb1 = st.columns([4, 1])
            with col_ex1:
                st.markdown("""<div class="whitebox" style="border-color:#ff9900; padding:8px; margin:0;">
<p style="font-size:11px; margin:0;">📊 <strong>EXCO slides (3 topics)</strong> — content & slides generated. Review and approve for submission.</p>
<p style="font-size:9px; margin:2px 0 0 0; color:#0099ff;">📎 <a href="#" style="color:#0099ff;">EXCO_Jun_Slide1.pptx</a> • <a href="#" style="color:#0099ff;">EXCO_Jun_Slide2.pptx</a> • <a href="#" style="color:#0099ff;">EXCO_Jun_Slide3.pptx</a></p>
</div>""", unsafe_allow_html=True)
            with col_exb1:
                if st.button("✅ Approve", key="btn_exco"):
                    st.success("✅ EXCO slides finalized. Calendar invite sent. 🔔 MS Teams notified.")

            col_ex2, col_exb2 = st.columns([4, 1])
            with col_ex2:
                st.markdown("""<div class="whitebox" style="border-color:#0099ff; padding:8px; margin:0;">
<p style="font-size:11px; margin:0;">💡 <strong>Boss 1:1 brief</strong> — talking points generated. Review before Thursday.</p>
<p style="font-size:9px; margin:2px 0 0 0; color:#0099ff;">📎 <a href="#" style="color:#0099ff;">Boss_1on1_Brief_Thu.md</a></p>
</div>""", unsafe_allow_html=True)
            with col_exb2:
                if st.button("✅ Approve", key="btn_boss_brief"):
                    st.success("✅ Boss brief confirmed. Reminder set for Thu 9:30am. 🔔 MS Teams notified.")


# ==========================================
# TAB 5: MEASURE OF SUCCESS
# ==========================================
with tab5:
    if st.session_state.phase not in ("complete", "designed", "building"):
        st.info("⏳ Complete Tab 1 first — Factory Agents are still building my twin.")
    else:
        st.markdown("### 📊 Measure of Success")

        col_m1, col_m2, col_m3, col_m4 = st.columns(4)
        with col_m1:
            st.markdown("""<div class="metric-card"><p style="font-size:24px; color:#00ff88; font-weight:bold;">14.5 hrs</p><p style="color:#888; font-size:11px;">Saved/Week</p></div>""", unsafe_allow_html=True)
        with col_m2:
            st.markdown("""<div class="metric-card"><p style="font-size:24px; color:#00ccff; font-weight:bold;">$0.42</p><p style="color:#888; font-size:11px;">Cost/Day</p></div>""", unsafe_allow_html=True)
        with col_m3:
            st.markdown("""<div class="metric-card"><p style="font-size:24px; color:#ff9900; font-weight:bold;">91%</p><p style="color:#888; font-size:11px;">Accuracy (I agree)</p></div>""", unsafe_allow_html=True)
        with col_m4:
            st.markdown("""<div class="metric-card"><p style="font-size:24px; color:#00ff88; font-weight:bold;">204x</p><p style="color:#888; font-size:11px;">ROI</p></div>""", unsafe_allow_html=True)

        st.markdown("---")
        st.markdown("#### 💰 By Skill")
        st.markdown("""<div class="whitebox">
<table style="width:100%; font-size:12px; color:#e0e0e0; border-collapse:collapse;">
<tr style="border-bottom:2px solid #0099ff;"><th style="padding:6px; text-align:left;">Skill</th><th style="padding:6px;">Frequency</th><th style="padding:6px;">Tokens</th><th style="padding:6px;">Cost/Day</th><th style="padding:6px;">Time Saved</th><th style="padding:6px;">Accuracy (I agree)</th></tr>
<tr style="border-bottom:1px solid #222;"><td style="padding:6px;">🎯 Orchestrator</td><td style="padding:6px; text-align:center;">1x/day</td><td style="padding:6px; text-align:center;">50</td><td style="padding:6px; text-align:center;">$0.002</td><td style="padding:6px; text-align:center; color:#00ff88;">0.5 hr</td><td style="padding:6px; text-align:center;">95%</td></tr>
<tr style="border-bottom:1px solid #222;"><td style="padding:6px;">⚡ #1 Claim Handling</td><td style="padding:6px; text-align:center;">8x/day</td><td style="padding:6px; text-align:center;">200</td><td style="padding:6px; text-align:center;">$0.18</td><td style="padding:6px; text-align:center; color:#00ff88; font-weight:bold;">5.5 hrs</td><td style="padding:6px; text-align:center;">89%</td></tr>
<tr style="border-bottom:1px solid #222;"><td style="padding:6px;">📧 #2 Email Reply</td><td style="padding:6px; text-align:center;">12x/day</td><td style="padding:6px; text-align:center;">100</td><td style="padding:6px; text-align:center;">$0.14</td><td style="padding:6px; text-align:center; color:#00ff88; font-weight:bold;">4.5 hrs</td><td style="padding:6px; text-align:center;">94%</td></tr>
<tr style="border-bottom:1px solid #222;"><td style="padding:6px;">📋 #3 Reporting</td><td style="padding:6px; text-align:center;">2x/month</td><td style="padding:6px; text-align:center;">500</td><td style="padding:6px; text-align:center;">$0.03</td><td style="padding:6px; text-align:center; color:#00ff88;">2.5 hrs</td><td style="padding:6px; text-align:center;">100%</td></tr>
<tr style="border-bottom:1px solid #222;"><td style="padding:6px;">📊 #4 EXCO Prep</td><td style="padding:6px; text-align:center;">1x/week</td><td style="padding:6px; text-align:center;">400</td><td style="padding:6px; text-align:center;">$0.02</td><td style="padding:6px; text-align:center; color:#00ff88;">2.0 hrs</td><td style="padding:6px; text-align:center;">88%</td></tr>
<tr style="border-top:2px solid #00ff88;"><td style="padding:6px; font-weight:bold;">TOTAL</td><td></td><td></td><td style="padding:6px; text-align:center; color:#00ccff; font-weight:bold;">$0.42/day</td><td style="padding:6px; text-align:center; color:#00ff88; font-weight:bold;">14.5 hrs/wk</td><td style="padding:6px; text-align:center; font-weight:bold;">91%</td></tr>
</table>
</div>""", unsafe_allow_html=True)

        st.markdown("#### 📈 Self-Improving Twin (Learning Curve)")
        st.markdown("""<div class="whitebox" style="padding:10px;">
<p style="font-size:12px;">
<em>Every time I correct my twin, it remembers permanently. Accuracy = % of outputs I approve without edits.</em><br/><br/>
<strong>Week 1 (Day 1-3):</strong> 84% — I corrected tone 6x, overrode priorities 2x, updated 1 threshold<br/>
<strong>Week 1 (Day 4-7):</strong> 91% — only 2 minor edits needed. Twin learned my style.<br/>
<strong>Week 2+ (projected):</strong> 95%+ — twin rarely needs correction. Never repeats a mistake.
</p>
</div>""", unsafe_allow_html=True)

        st.markdown("#### 💰 Annual ROI")
        st.markdown("""<div class="whitebox" style="border-color:#00ff88; padding:10px;">
<p style="font-size:12px;">
<strong>Time saved:</strong> 14.5 hrs/wk × 48 wks = <strong style="color:#00ff88;">696 hrs/year</strong><br/>
<strong>Value:</strong> 696 × $45/hr = <strong style="color:#00ff88;">$31,320/year</strong><br/>
<strong>Cost:</strong> $0.42/day × 365 = <strong>$153/year</strong><br/>
<strong style="color:#00ff88; font-size:14px;">Net: $31,167/year | ROI: 204x | Payback: &lt;1 day</strong><br/>
<span style="color:#888; font-size:11px;">Scale: 10 staff → $311K | Division (50) → $1.5M | Global (55K) → $170M potential</span>
</p>
</div>""", unsafe_allow_html=True)

        st.markdown("---")
        st.markdown("#### 🏗️ Architecture: 11 Agents, 4 Layers")
        st.markdown("""<div style="background:#0D1B3E; border-radius:12px; padding:30px 40px; margin:10px 0;">
<h3 style="text-align:center; color:white; font-weight:300; font-size:28px; margin-bottom:4px;">11 Factory Agents — <span style="color:#00C8E6; font-weight:600;">4 Layers</span></h3>
<p style="text-align:center; color:#A8CCF0; font-size:13px; margin-bottom:24px;">How the Digital Twin Factory thinks, designs, builds, and validates</p>

<div style="margin-bottom:12px; display:flex; align-items:stretch; border-radius:10px; overflow:hidden;">
<div style="writing-mode:vertical-rl; transform:rotate(180deg); background:#1B8A5A; padding:8px 10px; font-size:10px; font-weight:700; letter-spacing:1px; color:white; display:flex; align-items:center; justify-content:center;">UNDERSTAND</div>
<div style="display:flex; gap:10px; padding:12px 16px; flex:1; flex-wrap:wrap;">
<div style="background:rgba(255,255,255,0.07); border:1px solid rgba(255,255,255,0.15); border-radius:8px; padding:10px 14px; flex:1; min-width:180px;"><span style="font-size:11px; font-weight:700; color:#4ADE80;">#1</span><div style="font-size:13px; font-weight:600; color:white;">Understanding-You Consultant</div><div style="font-size:10px; color:#A8CCF0;">Job shadowing, video, docs → structured knowledge</div></div>
<div style="background:rgba(255,255,255,0.07); border:1px solid rgba(255,255,255,0.15); border-radius:8px; padding:10px 14px; flex:1; min-width:180px;"><span style="font-size:11px; font-weight:700; color:#4ADE80;">#2</span><div style="font-size:13px; font-weight:600; color:white;">Process Streamliner</div><div style="font-size:10px; color:#A8CCF0;">Maps workflows, identifies automation opportunities</div></div>
</div></div>

<div style="margin-bottom:12px; display:flex; align-items:stretch; border-radius:10px; overflow:hidden;">
<div style="writing-mode:vertical-rl; transform:rotate(180deg); background:#C49B2C; padding:8px 10px; font-size:10px; font-weight:700; letter-spacing:1px; color:white; display:flex; align-items:center; justify-content:center;">DESIGN</div>
<div style="display:flex; gap:10px; padding:12px 16px; flex:1; flex-wrap:wrap;">
<div style="background:rgba(255,255,255,0.07); border:1px solid rgba(255,255,255,0.15); border-radius:8px; padding:10px 14px; flex:1; min-width:140px;"><span style="font-size:11px; font-weight:700; color:#FCD34D;">#3</span><div style="font-size:12px; font-weight:600; color:white;">Architecture Designer</div><div style="font-size:10px; color:#A8CCF0;">Evaluates options, scores, picks best</div></div>
<div style="background:rgba(255,255,255,0.07); border:1px solid rgba(255,255,255,0.15); border-radius:8px; padding:10px 14px; flex:1; min-width:140px;"><span style="font-size:11px; font-weight:700; color:#FCD34D;">#4</span><div style="font-size:12px; font-weight:600; color:white;">Agentic Explainer</div><div style="font-size:10px; color:#A8CCF0;">Explains AI thinking in plain language</div></div>
<div style="background:rgba(255,255,255,0.07); border:1px solid rgba(255,255,255,0.15); border-radius:8px; padding:10px 14px; flex:1; min-width:140px;"><span style="font-size:11px; font-weight:700; color:#FCD34D;">#5</span><div style="font-size:12px; font-weight:600; color:white;">Quality Self-Assessor</div><div style="font-size:10px; color:#A8CCF0;">Reusability, security, not-lift-a-finger-ness</div></div>
<div style="background:rgba(255,255,255,0.07); border:1px solid rgba(255,255,255,0.15); border-radius:8px; padding:10px 14px; flex:1; min-width:140px;"><span style="font-size:11px; font-weight:700; color:#FCD34D;">#7</span><div style="font-size:12px; font-weight:600; color:white;">Cost-Benefit Observer</div><div style="font-size:10px; color:#A8CCF0;">Projects time saved, cost/day, ROI</div></div>
</div></div>

<div style="margin-bottom:12px; display:flex; align-items:stretch; border-radius:10px; overflow:hidden;">
<div style="writing-mode:vertical-rl; transform:rotate(180deg); background:#1A68C7; padding:8px 10px; font-size:10px; font-weight:700; letter-spacing:1px; color:white; display:flex; align-items:center; justify-content:center;">BUILD</div>
<div style="display:flex; gap:10px; padding:12px 16px; flex:1; flex-wrap:wrap;">
<div style="background:rgba(255,255,255,0.07); border:1px solid rgba(255,255,255,0.15); border-radius:8px; padding:10px 14px; flex:1; min-width:160px;"><span style="font-size:11px; font-weight:700; color:#60A5FA;">#6</span><div style="font-size:12px; font-weight:600; color:white;">Twin & Skill Builder</div><div style="font-size:10px; color:#A8CCF0;">Constructs twin — skills, triggers, integrations</div></div>
<div style="background:rgba(255,255,255,0.07); border:1px solid rgba(255,255,255,0.15); border-radius:8px; padding:10px 14px; flex:1; min-width:160px;"><span style="font-size:11px; font-weight:700; color:#60A5FA;">#8</span><div style="font-size:12px; font-weight:600; color:white;">Twin Profile Writer</div><div style="font-size:10px; color:#A8CCF0;">Writes .md profile — style, tone, decisions</div></div>
<div style="background:rgba(255,255,255,0.07); border:1px solid rgba(255,255,255,0.15); border-radius:8px; padding:10px 14px; flex:1; min-width:160px;"><span style="font-size:11px; font-weight:700; color:#60A5FA;">#9</span><div style="font-size:12px; font-weight:600; color:white;">Skill Constructor</div><div style="font-size:10px; color:#A8CCF0;">Designs reasoning chains for each skill</div></div>
</div></div>

<div style="margin-bottom:0; display:flex; align-items:stretch; border-radius:10px; overflow:hidden;">
<div style="writing-mode:vertical-rl; transform:rotate(180deg); background:#7B4FC7; padding:8px 10px; font-size:10px; font-weight:700; letter-spacing:1px; color:white; display:flex; align-items:center; justify-content:center;">VALIDATE</div>
<div style="display:flex; gap:10px; padding:12px 16px; flex:1; flex-wrap:wrap;">
<div style="background:rgba(255,255,255,0.07); border:1px solid rgba(255,255,255,0.15); border-radius:8px; padding:10px 14px; flex:1; min-width:180px;"><span style="font-size:11px; font-weight:700; color:#C084FC;">#10</span><div style="font-size:12px; font-weight:600; color:white;">Parallel Run Observer</div><div style="font-size:10px; color:#A8CCF0;">Measures accuracy — twin vs human</div></div>
<div style="background:rgba(255,255,255,0.07); border:1px solid rgba(255,255,255,0.15); border-radius:8px; padding:10px 14px; flex:1; min-width:180px;"><span style="font-size:11px; font-weight:700; color:#C084FC;">#11</span><div style="font-size:12px; font-weight:600; color:white;">Factory Orchestrator</div><div style="font-size:10px; color:#A8CCF0;">Coordinates all agents, manages flow</div></div>
</div></div>
</div>""", unsafe_allow_html=True)

        st.markdown("#### ✨ Why This Design is WOW")
        st.markdown("""<div style="background:#0D1B3E; border-radius:12px; padding:30px 40px; margin:10px 0;">
<h3 style="text-align:center; color:white; font-weight:300; font-size:28px; margin-bottom:4px;">Why This Design is <span style="color:#00C8E6; font-weight:600;">WOW</span></h3>
<p style="text-align:center; color:#A8CCF0; font-size:13px; margin-bottom:24px;">6 features that make the Digital Twin Factory truly different</p>
<div style="display:grid; grid-template-columns:1fr 1fr 1fr; gap:16px;">

<div style="background:linear-gradient(135deg, rgba(26,104,199,0.15), rgba(0,200,230,0.08)); border:1px solid rgba(0,200,230,0.3); border-radius:12px; padding:20px; border-top:3px solid #1B8A5A;">
<div style="font-size:24px; margin-bottom:8px;">📦</div>
<div style="font-size:14px; font-weight:700; color:white; margin-bottom:6px;">Unorganized Teaching</div>
<div style="font-size:11px; color:#A8CCF0; line-height:1.4;">Dump JD, SOP, org chart, voice, video — Factory sorts it all.</div>
<div style="color:#00C8E6; font-size:10px; font-weight:600; margin-top:8px;">No formatting required</div>
</div>

<div style="background:linear-gradient(135deg, rgba(26,104,199,0.15), rgba(0,200,230,0.08)); border:1px solid rgba(0,200,230,0.3); border-radius:12px; padding:20px; border-top:3px solid #00C8E6;">
<div style="font-size:24px; margin-bottom:8px;">👁️</div>
<div style="font-size:14px; font-weight:700; color:white; margin-bottom:6px;">Job Shadowing</div>
<div style="font-size:11px; color:#A8CCF0; line-height:1.4;">Record your screen while working. Factory learns by watching.</div>
<div style="color:#00C8E6; font-size:10px; font-weight:600; margin-top:8px;">Learn by observation</div>
</div>

<div style="background:linear-gradient(135deg, rgba(26,104,199,0.15), rgba(0,200,230,0.08)); border:1px solid rgba(0,200,230,0.3); border-radius:12px; padding:20px; border-top:3px solid #FCD34D;">
<div style="font-size:24px; margin-bottom:8px;">🧠</div>
<div style="font-size:14px; font-weight:700; color:white; margin-bottom:6px;">Absolute Explainability</div>
<div style="font-size:11px; color:#A8CCF0; line-height:1.4;">See how AI thinks — architecture scoring, reasoning chains, decisions.</div>
<div style="color:#00C8E6; font-size:10px; font-weight:600; margin-top:8px;">Users learn AI thinking</div>
</div>

<div style="background:linear-gradient(135deg, rgba(26,104,199,0.15), rgba(0,200,230,0.08)); border:1px solid rgba(0,200,230,0.3); border-radius:12px; padding:20px; border-top:3px solid #C084FC;">
<div style="font-size:24px; margin-bottom:8px;">✅</div>
<div style="font-size:14px; font-weight:700; color:white; margin-bottom:6px;">Quality Self-Assessment</div>
<div style="font-size:11px; color:#A8CCF0; line-height:1.4;">Reusability, security, "not-lift-a-finger-ness" scored before delivery.</div>
<div style="color:#00C8E6; font-size:10px; font-weight:600; margin-top:8px;">Built-in quality gates</div>
</div>

<div style="background:linear-gradient(135deg, rgba(26,104,199,0.15), rgba(0,200,230,0.08)); border:1px solid rgba(0,200,230,0.3); border-radius:12px; padding:20px; border-top:3px solid #4ADE80;">
<div style="font-size:24px; margin-bottom:8px;">🤝</div>
<div style="font-size:14px; font-weight:700; color:white; margin-bottom:6px;">Human-in-the-Loop</div>
<div style="font-size:11px; color:#A8CCF0; line-height:1.4;">Nothing sent without sign-off. MS Teams notifications.</div>
<div style="color:#00C8E6; font-size:10px; font-weight:600; margin-top:8px;">You approve everything</div>
</div>

<div style="background:linear-gradient(135deg, rgba(26,104,199,0.15), rgba(0,200,230,0.08)); border:1px solid rgba(0,200,230,0.3); border-radius:12px; padding:20px; border-top:3px solid #F97316;">
<div style="font-size:24px; margin-bottom:8px;">💰</div>
<div style="font-size:14px; font-weight:700; color:white; margin-bottom:6px;">Cost-Benefit Visibility</div>
<div style="font-size:11px; color:#A8CCF0; line-height:1.4;">14.5 hrs/week saved. Less than a coffee/day. 91% accuracy.</div>
<div style="color:#00C8E6; font-size:10px; font-weight:600; margin-top:8px;">Transparent economics</div>
</div>

</div>
</div>""", unsafe_allow_html=True)

        st.markdown("#### 🎬 End")
        st.markdown("""<div style="background:#0D1B3E; border-radius:12px; padding:50px 40px; margin:10px 0; text-align:center;">
<h2 style="color:white; font-weight:300; font-size:36px; margin-bottom:6px;">Digital Twin <span style="color:#00C8E6; font-weight:600;">Factory</span></h2>
<p style="color:#A8CCF0; font-size:18px; margin-bottom:30px;">Built in minutes, not months.</p>
<div style="display:flex; justify-content:center; gap:40px; margin-bottom:30px;">
<div style="text-align:center;"><div style="font-size:32px; font-weight:700; color:#00C8E6;">14.5 hrs</div><div style="font-size:12px; color:#A8CCF0;">saved per week</div></div>
<div style="text-align:center;"><div style="font-size:32px; font-weight:700; color:#00C8E6;">91%</div><div style="font-size:12px; color:#A8CCF0;">accuracy</div></div>
<div style="text-align:center;"><div style="font-size:32px; font-weight:700; color:#00C8E6;">55,000</div><div style="font-size:12px; color:#A8CCF0;">staff globally</div></div>
</div>
<div style="width:150px; height:2px; background:linear-gradient(90deg, transparent, #1A68C7, transparent); margin:0 auto 24px auto;"></div>
<p style="color:white; font-size:18px; margin-bottom:4px;">Gigi Ma</p>
<p style="color:#A8CCF0; font-size:14px; margin-bottom:20px;">Zurich Insurance Hong Kong</p>
<div style="display:inline-block; border:1px solid rgba(0,200,230,0.4); border-radius:20px; padding:6px 20px; font-size:11px; color:#00C8E6; letter-spacing:1px;">HYPERCHALLENGE 2026 — BYO TRACK</div>
</div>""", unsafe_allow_html=True)

# Footer
st.markdown("---")
st.markdown('<p style="text-align:center; color:#444; font-size:10px;">🧬 Digital Twin Factory v3.0 | 🏭 11 Factory Agents → 🤖 1 Twin + 4 Skills | Zurich Hyperchallenge 2026 | Gigi Ma</p>', unsafe_allow_html=True)
