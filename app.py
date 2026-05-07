import streamlit as st
import pandas as pd

st.set_page_config(page_title="AFL Rotation Elite", layout="wide")

# --- INITIAL SQUAD SETUP ---
if 'players' not in st.session_state:
    st.session_state.players = [
        {"Name": "Joel", "Line": "Back", "Group": 1, "Unit": "A", "Active": True},
        {"Name": "Eli", "Line": "Back", "Group": 2, "Unit": "A", "Active": True},
        {"Name": "Jagger", "Line": "Back", "Group": 3, "Unit": "A", "Active": True},
        {"Name": "Max", "Line": "Back", "Group": 4, "Unit": "A", "Active": True},
        {"Name": "Josh", "Line": "Back", "Group": 5, "Unit": "A", "Active": True},
        {"Name": "Carmelo", "Line": "Mid", "Group": 1, "Unit": "B", "Active": True},
        {"Name": "Buddy", "Line": "Mid", "Group": 2, "Unit": "B", "Active": True},
        {"Name": "Jaxon F", "Line": "Mid", "Group": 3, "Unit": "B", "Active": True},
        {"Name": "Harry", "Line": "Mid", "Group": 4, "Unit": "B", "Active": True},
        {"Name": "Tyler", "Line": "Mid", "Group": 5, "Unit": "B", "Active": True},
        {"Name": "Michael", "Line": "Forward", "Group": 1, "Unit": "C", "Active": True},
        {"Name": "Ernest", "Line": "Forward", "Group": 2, "Unit": "C", "Active": True},
        {"Name": "Leyton", "Line": "Forward", "Group": 3, "Unit": "C", "Active": True},
        {"Name": "Jaxon J", "Line": "Forward", "Group": 4, "Unit": "C", "Active": True},
        {"Name": "Xavier", "Line": "Forward", "Group": 5, "Unit": "C", "Active": True},
    ]

# --- LINE ROTATION SETTINGS ---
if 'line_plan' not in st.session_state:
    st.session_state.line_plan = {
        1: {"A": "Back", "B": "Mid", "C": "Forward"},
        2: {"A": "Mid", "B": "Forward", "C": "Back"},
        3: {"A": "Forward", "B": "Back", "C": "Mid"},
        4: {"A": "Back", "B": "Mid", "C": "Forward"}
    }

# --- SIDEBAR: TACTICAL & SQUAD ---
with st.sidebar:
    st.header("⚙️ Tactical Strategy")
    with st.expander("🔄 Set Line Rotations"):
        for q in [1, 2, 3, 4]:
            st.write(f"**Quarter {q} Plan**")
            st.session_state.line_plan[q]["A"] = st.selectbox(f"Unit A Pos", ["Back", "Mid", "Forward"], index=["Back", "Mid", "Forward"].index(st.session_state.line_plan[q]["A"]), key=f"q{q}a")
            st.session_state.line_plan[q]["B"] = st.selectbox(f"Unit B Pos", ["Back", "Mid", "Forward"], index=["Back", "Mid", "Forward"].index(st.session_state.line_plan[q]["B"]), key=f"q{q}b")
            st.session_state.line_plan[q]["C"] = st.selectbox(f"Unit C Pos", ["Back", "Mid", "Forward"], index=["Back", "Mid", "Forward"].index(st.session_state.line_plan[q]["C"]), key=f"q{q}c")

    st.header("📋 Player Names")
    for i, p in enumerate(st.session_state.players):
        p['Name'] = st.text_input(f"Unit {p['Unit']} - G{p['Group']}", value=p['Name'], key=f"name_{i}")

# --- MAIN INTERFACE ---
st.title("🏉 AFL Rotation Elite")

# --- UI CONTROLS ---
t_col1, t_col2 = st.columns([2, 1])

with t_col1:
    q_selected = st.radio("Current Quarter", [1, 2, 3, 4], horizontal=True)
    phase_toggle = st.radio("Rotation Segment", ["Start (0-7.5m)", "Mid (7.5-15m)"], horizontal=True)
    phase = ((q_selected - 1) * 2) + (1 if phase_toggle == "Start (0-7.5m)" else 2)

with t_col2:
    st.metric("Rotation Phase", f"P{phase}")
    current_plan = st.session_state.line_plan[q_selected]
    st.info(f"Plan: A={current_plan['A']} | B={current_plan['B']} | C={current_plan['C']}")

st.divider()

# Update player lines based on the tactical plan for the selected quarter
for p in st.session_state.players:
    p['Line'] = st.session_state.line_plan[q_selected][p['Unit']]

# --- ROTATION ENGINE ---
mapping = {1:1, 2:2, 3:3, 4:4, 5:5, 6:1, 7:2, 8:3}
next_mapping = {1:2, 2:3, 3:4, 4:5, 5:1, 6:2, 7:3, 8:4}

current_off_group = mapping[phase]
next_off_group = next_mapping[phase]

df = pd.DataFrame(st.session_state.players)

# --- FIELD VIEW ---
col_field, col_bench = st.columns([3, 1.2])

with col_field:
    f1, f2, f3 = st.columns(3)
    lines = [("Back", "🔵 BACKS", f1), ("Mid", "🟢 MIDFIELD", f2), ("Forward", "🟠 FORWARDS", f3)]
    
    for line_key, label, col in lines:
        with col:
            st.subheader(label)
            players_on = df[(df['Line'] == line_key) & (df['Group'] != current_off_group)]
            for _, p in players_on.iterrows():
                st.info(f"**{p['Name']}** `G{p['Group']}`")

with col_bench:
    st.subheader("🪑 CURRENT BENCH")
    bench = df[df['Group'] == current_off_group]
    for _, p in bench.iterrows():
        st.error(f"**OFF: {p['Name']}**")
    
    st.divider()
    st.subheader("🚨 UPCOMING SUBS")
    st.write("Warn these players they are OFF next:")
    upcoming = df[df['Group'] == next_off_group]
    for _, p in upcoming.iterrows():
        st.write(f"👉 **{p['Name']}** ({p['Line']})")
