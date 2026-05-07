import streamlit as st
import pandas as pd
import random

st.set_page_config(page_title="AFL Rotation Pro", layout="wide")

# --- DATA INITIALIZATION ---
if 'players' not in st.session_state:
    st.session_state.players = [{"Name": "", "Unit": "", "Grp": i%5+1, "Active": True} for i in range(15)]
    # Default names for testing - user can overwrite
    default_names = ["Joel", "Eli", "Jagger", "Max", "Josh", "Carmelo", "Buddy", "Jaxon F", "Harry", "Tyler", "Michael", "Ernest", "Leyton", "Jaxon J", "Xavier"]
    for i in range(15):
        st.session_state.players[i]["Name"] = default_names[i]
        st.session_state.players[i]["Unit"] = "A" if i < 5 else ("B" if i < 10 else "C")

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
    for i, p in enumerate(st.session_state.players):
        col1, col2 = st.columns([3, 1])
        p['Name'] = col1.text_input(f"Player {i+1}", value=p['Name'], key=f"n_{i}")
        p['Active'] = col2.checkbox("Playing", value=p['Active'], key=f"act_{i}")

# --- PAGE 2: WHITEBOARD PLAN ---
elif page == "🖍 Whiteboard Plan":
    st.header("Step 2: Set the Board")
    
    # Starting Group Logic
    st.session_state.start_grp = st.pills("Which Group starts on the bench?", [1, 2, 3, 4, 5], default=1)
    
    # Quarter Plan
    st.subheader("Tactical Line Moves")
    for q in [1, 2, 3, 4]:
        with st.expander(f"Quarter {q} Plan"):
            c1, c2, c3 = st.columns(3)
            st.session_state.line_plan[q]["A"] = c1.selectbox(f"Unit A (Defenders)", ["Back", "Mid", "Forward"], index=0, key=f"ca{q}")
            st.session_state.line_plan[q]["B"] = c2.selectbox(f"Unit B (Midfielders)", ["Back", "Mid", "Forward"], index=1, key=f"cb{q}")
            st.session_state.line_plan[q]["C"] = c3.selectbox(f"Unit C (Forwards)", ["Back", "Mid", "Forward"], index=2, key=f"cc{q}")

    st.divider()
    st.subheader("Assign Positions & Groups")
    
    # Auto-Fill Option
    if st.button("Shuffle Remaining Players"):
        used_names = [p['Name'] for p in st.session_state.players if p['Name'] != ""]
        # Logic to ensure 5 per unit
        units = ["A"]*5 + ["B"]*5 + ["C"]*5
        random.shuffle(units)
        for i, p in enumerate(st.session_state.players):
            if p['Name'] == "": p['Name'] = f"Player {i+1}"
            p['Unit'] = units[i]
        st.rerun()

    # Layout by Unit for "Top Level" visibility
    u_cols = st.columns(3)
    unit_labels = {"A": "Unit A (Defensive Block)", "B": "Unit B (Midfield Block)", "C": "Unit C (Forward Block)"}
    
    for i, unit_id in enumerate(["A", "B", "C"]):
        with u_cols[i]:
            st.markdown(f"### {unit_labels[unit_id]}")
            unit_players = [p for p in st.session_state.players if p['Unit'] == unit_id]
            for p_idx, p in enumerate(st.session_state.players):
                if p['Unit'] == unit_id:
                    st.text_input(f"Name", value=p['Name'], key=f"pname_{p_idx}", label_visibility="collapsed")
                    col_u, col_g = st.columns([1, 1])
                    p['Unit'] = col_u.selectbox("Unit", ["A", "B", "C"], index=i, key=f"punit_{p_idx}", label_visibility="collapsed")
                    p['Grp'] = col_g.selectbox("Grp", [1, 2, 3, 4, 5], index=p['Grp']-1, key=f"pgrp_{p_idx}", label_visibility="collapsed")
                    st.markdown("---")

# --- PAGE 3: LIVE OVAL ---
elif page == "🏟 LIVE OVAL":
    if "prev_q" not in st.session_state: st.session_state.prev_q = 1
    q_selected = st.pills("Quarter", [1, 2, 3, 4], default=1)
    
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
    st.markdown("""<style>.zone{border:2px solid #333; border-radius:15px; padding:10px; margin-bottom:10px; background:#f0f2f6; text-align:center;} .player{display:block; padding:8px; margin:4px; background:white; border-radius:5px; border-left:8px solid #1F4E78; font-weight:bold; font-size:1.1em;}</style>""", unsafe_allow_html=True)
    
    for zone, color, label in [("Forward", "🟠", "FORWARDS"), ("Mid", "🟢", "MIDFIELD"), ("Back", "🔵", "BACKS")]:
        st.markdown(f"<div class='zone'>{color} <strong>{label}</strong></div>", unsafe_allow_html=True)
        z_players = df_active[(df_active['Zone'] == zone) & (df_active['Grp'] != off_grp)]
        for _, p in z_players.iterrows():
            st.markdown(f"<div class='player'>{p['Name']} [G{p['Grp']}]</div>", unsafe_allow_html=True)

    st.divider()
    c_off, c_next = st.columns(2)
    with c_off:
        st.error("**OFF FIELD**")
        for _, p in df_active[df_active['Grp'] == off_grp].iterrows():
            st.write(f"❌ {p['Name']} ({p['Zone']} Sub)")
    with c_next:
        st.warning("**UPCOMING SWAP**")
        upcoming_off = df_active[df_active['Grp'] == next_off_grp]
        for _, off_p in upcoming_off.iterrows():
            on_p = df_active[(df_active['Unit'] == off_p['Unit']) & (df_active['Grp'] == off_grp)]
            on_name = on_p['Name'].values[0] if not on_p.empty else "No Sub"
            st.write(f"**{off_p['Name']}** ↔ **{on_name}**")
