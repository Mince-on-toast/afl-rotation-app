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

# --- SIDEBAR: WHITEBOARD SETUP ---
with st.sidebar:
    st.header("📋 Whiteboard Setup")
    st.caption("Set your squad before the siren.")
    
    with st.expander("🔄 Tactical Line Plan"):
        for q in [1, 2, 3, 4]:
            st.write(f"**Quarter {q} Positions**")
            c1, c2, c3 = st.columns(3)
            st.session_state.line_plan[q]["A"] = c1.selectbox(f"Unit A", ["Back", "Mid", "Forward"], index=["Back", "Mid", "Forward"].index(st.session_state.line_plan[q]["A"]), key=f"plan_a_{q}")
            st.session_state.line_plan[q]["B"] = c2.selectbox(f"Unit B", ["Back", "Mid", "Forward"], index=["Back", "Mid", "Forward"].index(st.session_state.line_plan[q]["B"]), key=f"plan_b_{q}")
            st.session_state.line_plan[q]["C"] = c3.selectbox(f"Unit C", ["Back", "Mid", "Forward"], index=["Back", "Mid", "Forward"].index(st.session_state.line_plan[q]["C"]), key=f"plan_c_{q}")

    st.header("🏃 Squad Attendance")
    for i, p in enumerate(st.session_state.players):
        col1, col2 = st.columns([3, 1])
        p['Name'] = col1.text_input(f"Name {i}", value=p['Name'], key=f"n_{i}", label_visibility="collapsed")
        p['Active'] = col2.checkbox("In", value=p['Active'], key=f"act_{i}")

# --- MAIN DASHBOARD ---
st.title("🏉 AFL Rotation Pro")

# --- GAME CONTROLS ---
q_selected = st.radio("Current Quarter", [1, 2, 3, 4], horizontal=True)
phase_toggle = st.radio("Rotation Segment", ["Start (0-7.5m)", "Mid (7.5-15m)"], horizontal=True)

# Calculate Bench Logic
phase = ((q_selected - 1) * 2) + (1 if phase_toggle == "Start (0-7.5m)" else 2)
mapping = {1:1, 2:2, 3:3, 4:4, 5:5, 6:1, 7:2, 8:3}
next_mapping = {1:2, 2:3, 3:4, 4:5, 5:1, 6:2, 7:3, 8:4}
current_off = mapping[phase]
next_off = next_mapping[phase]

# Update Current Line Positions based on Plan
for p in st.session_state.players:
    p['CurrentLine'] = st.session_state.line_plan[q_selected][p['Unit']]

df = pd.DataFrame(st.session_state.players)
df_active = df[df['Active'] == True]

# Bench Tracker Calculation
bench_counts = {p['Name']: 0 for p in st.session_state.players}
for p in range(1, phase + 1):
    off_grp = mapping[p]
    for _, row in df_active[df_active['Group'] == off_grp].iterrows():
        bench_counts[row['Name']] += 1

st.divider()

# --- FIELD VIEW ---
col_field, col_bench = st.columns([3, 1.3])

with col_field:
    f1, f2, f3 = st.columns(3)
    lines = [("Back", "🔵 BACKS", f1), ("Mid", "🟢 MIDFIELD", f2), ("Forward", "🟠 FORWARDS", f3)]
    
    for line_key, label, col in lines:
        with col:
            st.subheader(label)
            players_on = df_active[(df_active['CurrentLine'] == line_key) & (df_active['Group'] != current_off)]
            for _, p in players_on.iterrows():
                st.info(f"**{p['Name']}** (Rest: {bench_counts[p['Name']]})")

with col_bench:
    st.subheader("🪑 CURRENT BENCH")
    bench_list = df_active[df_active['Group'] == current_off]
    for _, p in bench_list.iterrows():
        st.error(f"**OFF: {p['Name']}**")
    
    st.divider()
    st.subheader("🚨 UPCOMING SUBS")
    upcoming = df_active[df_active['Group'] == next_off]
    for _, p in upcoming.iterrows():
        st.warning(f"👉 **{p['Name']}** (to {p['CurrentLine']})")

    st.divider()
    st.write("📊 **Total Bench Stints**")
    for name, count in bench_counts.items():
        if count > 0:
            st.caption(f"{name}: {count} rests")
