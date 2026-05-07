import streamlit as st
import pandas as pd

st.set_page_config(page_title="AFL Rotation Pro", layout="wide")

# --- DATA INITIALIZATION ---
if 'players' not in st.session_state:
    st.session_state.players = [
        {"Name": "Joel", "Unit": "A", "Group": 1, "Active": True},
        {"Name": "Eli", "Unit": "A", "Group": 2, "Active": True},
        {"Name": "Jagger", "Unit": "A", "Group": 3, "Active": True},
        {"Name": "Max", "Unit": "A", "Group": 4, "Active": True},
        {"Name": "Josh", "Unit": "A", "Group": 5, "Active": True},
        {"Name": "Carmelo", "Unit": "B", "Group": 1, "Active": True},
        {"Name": "Buddy", "Unit": "B", "Group": 2, "Active": True},
        {"Name": "Jaxon F", "Unit": "B", "Group": 3, "Active": True},
        {"Name": "Harry", "Unit": "B", "Group": 4, "Active": True},
        {"Name": "Tyler", "Unit": "B", "Group": 5, "Active": True},
        {"Name": "Michael", "Unit": "C", "Group": 1, "Active": True},
        {"Name": "Ernest", "Unit": "C", "Group": 2, "Active": True},
        {"Name": "Leyton", "Unit": "C", "Group": 3, "Active": True},
        {"Name": "Jaxon J", "Unit": "C", "Group": 4, "Active": True},
        {"Name": "Xavier", "Unit": "C", "Group": 5, "Active": True},
    ]

if 'line_plan' not in st.session_state:
    st.session_state.line_plan = {
        1: {"A": "Back", "B": "Mid", "C": "Forward"},
        2: {"A": "Forward", "B": "Back", "C": "Mid"},
        3: {"A": "Mid", "B": "Forward", "C": "Back"},
        4: {"A": "Back", "B": "Mid", "C": "Forward"}
    }

# --- APP MODE SELECTOR ---
app_mode = st.pills("App Mode", ["📋 Setup & Whiteboard", "🏟 LIVE GAME VIEW"], default="📋 Setup & Whiteboard")

if app_mode == "📋 Setup & Whiteboard":
    st.header("Whiteboard Planning")
    st.info("Set your squad and tactical plan here before the siren.")
    
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Tactical Line Swaps")
        for q in [1, 2, 3, 4]:
            with st.expander(f"Quarter {q} Assignments"):
                st.session_state.line_plan[q]["A"] = st.selectbox(f"Unit A Q{q}", ["Back", "Mid", "Forward"], index=0, key=f"qa{q}")
                st.session_state.line_plan[q]["B"] = st.selectbox(f"Unit B Q{q}", ["Back", "Mid", "Forward"], index=1, key=f"qb{q}")
                st.session_state.line_plan[q]["C"] = st.selectbox(f"Unit C Q{q}", ["Back", "Mid", "Forward"], index=2, key=f"qc{q}")
    
    with col2:
        st.subheader("Squad List")
        for i, p in enumerate(st.session_state.players):
            with st.expander(f"Slot {i+1}: Unit {p['Unit']} - G{p['Group']}"):
                p['Name'] = st.text_input("Name", value=p['Name'], key=f"un_{i}")
                p['Active'] = st.checkbox("Available", value=p['Active'], key=f"act_{i}")

else:
    # --- LIVE GAME VIEW ---
    st.header("Game Mode")
    
    # Simple Controls
    c1, c2 = st.columns([2, 1])
    q_selected = c1.pills("Quarter", [1, 2, 3, 4], default=1)
    phase_toggle = c1.pills("Timing", ["Start", "Mid"], default="Start")
    
    # Rotation Logic (Fixed Array to prevent drift)
    # Mapping Phase 1-8 to Group Off
    rot_sequence = [1, 2, 3, 4, 5, 1, 2, 3] 
    phase_idx = ((q_selected - 1) * 2) + (0 if phase_toggle == "Start" else 1)
    off_group = rot_sequence[phase_idx]
    
    # Upcoming Swap logic
    next_phase_idx = (phase_idx + 1) % 8
    next_off_group = rot_sequence[next_phase_idx]

    # Map current lines
    for p in st.session_state.players:
        p['CurrentLine'] = st.session_state.line_plan[q_selected][p['Unit']]

    df = pd.DataFrame(st.session_state.players)
    df_active = df[df['Active'] == True]

    # --- THE OVAL LAYOUT ---
    st.markdown("""
    <style>
    .oval-zone {
        border: 2px solid #555;
        border-radius: 50px;
        padding: 15px;
        margin-bottom: 10px;
        background-color: #f9f9f9;
        text-align: center;
    }
    .player-card {
        display: inline-block;
        background: #1F4E78;
        color: white;
        padding: 5px 10px;
        margin: 3px;
        border-radius: 5px;
        font-weight: bold;
    }
    </style>
    """, unsafe_allow_html=True)

    # 1. FORWARDS (Top of Oval)
    st.markdown("<div class='oval-zone'><strong>🟠 FORWARDS</strong><br>", unsafe_allow_html=True)
    fwds = df_active[(df_active['CurrentLine'] == 'Forward') & (df_active['Group'] != off_group)]
    for _, p in fwds.iterrows():
        st.markdown(f"<span class='player-card'>{p['Name']} (G{p['Group']})</span>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    # 2. MIDFIELD (Middle)
    st.markdown("<div class='oval-zone'><strong>🟢 MIDFIELD</strong><br>", unsafe_allow_html=True)
    mids = df_active[(df_active['CurrentLine'] == 'Mid') & (df_active['Group'] != off_group)]
    for _, p in mids.iterrows():
        st.markdown(f"<span class='player-card' style='background-color:#2E7D32'>{p['Name']} (G{p['Group']})</span>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    # 3. BACKS (Bottom of Oval)
    st.markdown("<div class='oval-zone'><strong>🔵 BACKS</strong><br>", unsafe_allow_html=True)
    backs = df_active[(df_active['CurrentLine'] == 'Back') & (df_active['Group'] != off_group)]
    for _, p in backs.iterrows():
        st.markdown(f"<span class='player-card' style='background-color:#1565C0'>{p['Name']} (G{p['Group']})</span>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    st.divider()
    
    # 4. BENCH & SWAPS
    b1, b2 = st.columns(2)
    with b1:
        st.subheader("🪑 CURRENT BENCH")
        bench = df_active[df_active['Group'] == off_group]
        for _, p in bench.iterrows():
            st.error(f"**OFF: {p['Name']}** ({p['CurrentLine']} Sub)")
    
    with b2:
        st.subheader("🚨 UPCOMING SWAP")
        off_p = df_active[df_active['Group'] == next_off_group]
        on_p = df_active[df_active['Group'] == off_group]
        for _, p_off in off_p.iterrows():
            p_on = on_p[on_p['Unit'] == p_off['Unit']]
            on_name = p_on['Name'].iloc[0] if not p_on.empty else "No Sub"
            st.warning(f"{p_off['Name']} (Field) ↔ {on_name} (Bench)")
