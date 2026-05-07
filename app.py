import streamlit as st
import pandas as pd

st.set_page_config(page_title="AFL Rotation Elite", layout="wide")

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

# --- SIDEBAR: WHITEBOARD & SQUAD SETUP ---
with st.sidebar:
    st.header("📋 Whiteboard Setup")
    
    # MANUAL START SELECTOR
    st.subheader("🏁 Starting Bench")
    starting_group = st.pills("Which group starts OFF?", [1, 2, 3, 4, 5], default=1)
    
    with st.expander("🔄 Tactical Line Plan"):
        for q in [1, 2, 3, 4]:
            st.write(f"**Quarter {q} Plan**")
            c1, c2, c3 = st.columns(3)
            st.session_state.line_plan[q]["A"] = c1.selectbox(f"A", ["Back", "Mid", "Forward"], index=["Back", "Mid", "Forward"].index(st.session_state.line_plan[q]["A"]), key=f"pla_{q}")
            st.session_state.line_plan[q]["B"] = c2.selectbox(f"B", ["Back", "Mid", "Forward"], index=["Back", "Mid", "Forward"].index(st.session_state.line_plan[q]["B"]), key=f"plb_{q}")
            st.session_state.line_plan[q]["C"] = c3.selectbox(f"C", ["Back", "Mid", "Forward"], index=["Back", "Mid", "Forward"].index(st.session_state.line_plan[q]["C"]), key=f"plc_{q}")

    st.header("👥 Squad & Units")
    for i, p in enumerate(st.session_state.players):
        with st.expander(f"{p['Name']} (Unit {p['Unit']} - G{p['Group']})"):
            p['Name'] = st.text_input("Name", value=p['Name'], key=f"un_{i}")
            p['Unit'] = st.selectbox("Unit", ["A", "B", "C"], index=["A", "B", "C"].index(p['Unit']), key=f"u_sel_{i}")
            p['Group'] = st.selectbox("Group #", [1, 2, 3, 4, 5], index=p['Group']-1, key=f"g_sel_{i}")
            p['Active'] = st.checkbox("Active", value=p['Active'], key=f"a_sel_{i}")

# --- MAIN DASHBOARD ---
st.title("🏉 AFL Rotation Elite")

# Auto-reset logic for Quarter Changes
if "prev_q" not in st.session_state:
    st.session_state.prev_q = 1

q_selected = st.pills("Current Quarter", [1, 2, 3, 4], default=1)

if q_selected != st.session_state.prev_q:
    st.session_state.prev_q = q_selected
    st.rerun()

phase_toggle = st.pills("Rotation Phase", ["Quarter Start", "Mid-Quarter Rotation"], default="Quarter Start")

# --- ENGINE ---
phase_num = ((q_selected - 1) * 2) + (1 if phase_toggle == "Quarter Start" else 2)
group_sequence = [1, 2, 3, 4, 5, 1, 2, 3]
start_offset = starting_group - 1
current_off_idx = group_sequence[(phase_num - 1 + start_offset) % 5]
next_off_idx = group_sequence[(phase_num + start_offset) % 5]

# Update Current Lines
for p in st.session_state.players:
    p['CurrentLine'] = st.session_state.line_plan[q_selected][p['Unit']]

df = pd.DataFrame(st.session_state.players)
df_active = df[df['Active'] == True]

st.divider()

# --- FIELD VIEW ---
col_field, col_bench = st.columns([2.5, 1.5])

with col_field:
    f1, f2, f3 = st.columns(3)
    lines = [("Back", "🔵 BACKS", f1), ("Mid", "🟢 MIDS", f2), ("Forward", "🟠 FWDS", f3)]
    
    for line_key, label, col in lines:
        with col:
            st.subheader(label)
            players_on = df_active[(df_active['CurrentLine'] == line_key) & (df_active['Group'] != current_off_idx)]
            for _, p in players_on.iterrows():
                st.info(f"**{p['Name']}** `G{p['Group']}`")

with col_bench:
    st.subheader("🪑 THE BENCH")
    bench_list = df_active[df_active['Group'] == current_off_idx]
    for _, p in bench_list.iterrows():
        st.error(f"**OFF: {p['Name']}** ({p['CurrentLine']} Sub)")

    st.divider()
    st.subheader("🚨 UPCOMING SWAP")
    upcoming_off = df_active[df_active['Group'] == next_off_idx]
    upcoming_on = df_active[df_active['Group'] == current_off_idx]
    
    for _, off_p in upcoming_off.iterrows():
        on_p = upcoming_on[upcoming_on['Unit'] == off_p['Unit']]
        on_name = on_p['Name'].iloc[0] if not on_p.empty else "No Sub"
        st.warning(f"**{off_p['Name']}** (Off) ↔ **{on_name}** (On)")
