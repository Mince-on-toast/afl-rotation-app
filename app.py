import streamlit as st
import pandas as pd

st.set_page_config(page_title="AFL Rotation Pro", layout="wide")

# --- INITIAL SQUAD DATA ---
if 'players' not in st.session_state:
    st.session_state.players = [
        {"Name": "Joel", "Unit": "A", "Grp": 1, "Active": True},
        {"Name": "Eli", "Unit": "A", "Grp": 2, "Active": True},
        {"Name": "Jagger", "Unit": "A", "Grp": 3, "Active": True},
        {"Name": "Max", "Unit": "A", "Grp": 4, "Active": True},
        {"Name": "Josh", "Unit": "A", "Grp": 5, "Active": True},
        {"Name": "Carmelo", "Unit": "B", "Grp": 1, "Active": True},
        {"Name": "Buddy", "Unit": "B", "Grp": 2, "Active": True},
        {"Name": "Jaxon F", "Unit": "B", "Grp": 3, "Active": True},
        {"Name": "Harry", "Unit": "B", "Grp": 4, "Active": True},
        {"Name": "Tyler", "Unit": "B", "Grp": 5, "Active": True},
        {"Name": "Michael", "Unit": "C", "Grp": 1, "Active": True},
        {"Name": "Ernest", "Unit": "C", "Grp": 2, "Active": True},
        {"Name": "Leyton", "Unit": "C", "Grp": 3, "Active": True},
        {"Name": "Jaxon J", "Unit": "C", "Grp": 4, "Active": True},
        {"Name": "Xavier", "Unit": "C", "Grp": 5, "Active": True},
    ]

if 'line_plan' not in st.session_state:
    st.session_state.line_plan = {
        1: {"A": "Back", "B": "Mid", "C": "Forward"},
        2: {"A": "Forward", "B": "Back", "C": "Mid"},
        3: {"A": "Mid", "B": "Forward", "C": "Back"},
        4: {"A": "Back", "B": "Mid", "C": "Forward"}
    }

# --- NAVIGATION ---
page = st.sidebar.radio("Navigation", ["📋 Setup Squad", "🖍 Whiteboard Plan", "🏟 LIVE OVAL"])

# --- PAGE 1: SETUP SQUAD ---
if page == "📋 Setup Squad":
    st.header("Step 1: Attendance")
    for p in st.session_state.players:
        col1, col2 = st.columns([3, 1])
        p['Name'] = col1.text_input(f"Player", value=p['Name'], key=f"n_{p['Name']}")
        p['Active'] = col2.checkbox("Playing", value=p['Active'], key=f"act_{p['Name']}")

# --- PAGE 2: WHITEBOARD PLAN ---
elif page == "🖍 Whiteboard Plan":
    st.header("Step 2: Set the Board")
    st.session_state.start_grp = st.pills("Which Group starts on the bench?", [1, 2, 3, 4, 5], default=1)
    
    st.subheader("Quarterly Line Moves")
    for q in [1, 2, 3, 4]:
        with st.expander(f"Quarter {q} Plan"):
            c1, c2, c3 = st.columns(3)
            st.session_state.line_plan[q]["A"] = c1.selectbox(f"Unit A", ["Back", "Mid", "Forward"], index=0, key=f"ca{q}")
            st.session_state.line_plan[q]["B"] = c2.selectbox(f"Unit B", ["Back", "Mid", "Forward"], index=1, key=f"cb{q}")
            st.session_state.line_plan[q]["C"] = c3.selectbox(f"Unit C", ["Back", "Mid", "Forward"], index=2, key=f"cc{q}")

    st.subheader("Assign Starting Positions")
    for p in st.session_state.players:
        if p['Active']:
            with st.expander(f"Position {p['Name']}"):
                # Coach thinks in positions, we map to Units A/B/C internally
                pos = st.selectbox("Start Position", ["Back", "Mid", "Forward"], index=["A", "B", "C"].index(p['Unit']), key=f"p_{p['Name']}")
                p['Unit'] = {"Back": "A", "Mid": "B", "Forward": "C"}[pos]
                p['Grp'] = st.selectbox("Rotation Group", [1, 2, 3, 4, 5], index=p['Grp']-1, key=f"g_{p['Name']}")

# --- PAGE 3: LIVE OVAL ---
elif page == "🏟 LIVE OVAL":
    # AUTO-RESET LOGIC
    if "prev_q" not in st.session_state: st.session_state.prev_q = 1
    
    q_selected = st.pills("Quarter", [1, 2, 3, 4], default=1)
    
    # If Quarter changes, force Timing to 'Starting Rotation'
    if q_selected != st.session_state.prev_q:
        st.session_state.timing_choice = "Starting Rotation"
        st.session_state.prev_q = q_selected
        st.rerun()

    timing = st.pills("Rotation Timing", ["Starting Rotation", "Mid-Quarter Rotation"], key="timing_choice")
    
    # Rotation Logic
    raw_phase = ((q_selected - 1) * 2) + (1 if timing == "Starting Rotation" else 2)
    start_offset = st.session_state.get('start_grp', 1) - 1
    group_seq = [1, 2, 3, 4, 5, 1, 2, 3]
    off_grp = group_seq[(raw_phase - 1 + start_offset) % 5]
    next_off_grp = group_seq[(raw_phase + start_offset) % 5]

    for p in st.session_state.players:
        p['Zone'] = st.session_state.line_plan[q_selected][p['Unit']]
    
    df_active = pd.DataFrame(st.session_state.players)[lambda x: x['Active'] == True]

    # STYLED OVAL
    st.markdown("""<style>.zone{border:2px solid #333; border-radius:15px; padding:10px; margin-bottom:10px; background:#f0f2f6; text-align:center;} .player{display:block; padding:5px; margin:2px; background:white; border-radius:5px; border-left:5px solid #1F4E78; font-weight:bold;}</style>""", unsafe_allow_html=True)
    
    # Zone Layout
    for zone, color, label in [("Forward", "🟠", "FORWARDS"), ("Mid", "🟢", "MIDFIELD"), ("Back", "🔵", "BACKS")]:
        st.markdown(f"<div class='zone'>{color} <strong>{label}</strong></div>", unsafe_allow_html=True)
        z_players = df_active[(df_active['Zone'] == zone) & (df_active['Grp'] != off_grp)]
        for _, p in z_players.iterrows():
            st.markdown(f"<div class='player'>{p['Name']} [G{p['Grp']}]</div>", unsafe_allow_html=True)

    st.divider()
    # BENCH & SWAPS
    col_off, col_next = st.columns(2)
    with col_off:
        st.error("**OFF FIELD**")
        for _, p in df_active[df_active['Grp'] == off_grp].iterrows():
            st.write(f"❌ {p['Name']} ({p['Zone']})")
    with col_next:
        st.warning("**UPCOMING SWAP**")
        upcoming_off = df_active[df_active['Grp'] == next_off_grp]
        for _, off_p in upcoming_off.iterrows():
            on_p = df_active[(df_active['Unit'] == off_p['Unit']) & (df_active['Grp'] == off_grp)]
            on_name = on_p['Name'].values[0] if not on_p.empty else "No Sub"
            st.write(f"{off_p['Name']} ↔ {on_name}")
