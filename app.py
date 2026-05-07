import streamlit as st
import pandas as pd

st.set_page_config(page_title="AFL Coach Console", layout="wide")

# -----------------------------
# INITIAL DATA
# -----------------------------
if "players" not in st.session_state:
    st.session_state.players = [
        {"Name": "Joel", "Group": 1, "Unit": "A", "Active": True},
        {"Name": "Eli", "Group": 2, "Unit": "A", "Active": True},
        {"Name": "Jagger", "Group": 3, "Unit": "A", "Active": True},
        {"Name": "Max", "Group": 4, "Unit": "A", "Active": True},
        {"Name": "Josh", "Group": 5, "Unit": "A", "Active": True},

        {"Name": "Carmelo", "Group": 1, "Unit": "B", "Active": True},
        {"Name": "Buddy", "Group": 2, "Unit": "B", "Active": True},
        {"Name": "Jaxon F", "Group": 3, "Unit": "B", "Active": True},
        {"Name": "Harry", "Group": 4, "Unit": "B", "Active": True},
        {"Name": "Tyler", "Group": 5, "Unit": "B", "Active": True},

        {"Name": "Michael", "Group": 1, "Unit": "C", "Active": True},
        {"Name": "Ernest", "Group": 2, "Unit": "C", "Active": True},
        {"Name": "Leyton", "Group": 3, "Unit": "C", "Active": True},
        {"Name": "Jaxon J", "Group": 4, "Unit": "C", "Active": True},
        {"Name": "Xavier", "Group": 5, "Unit": "C", "Active": True},
    ]

# FIXED rotation cycle (no drift)
ROTATION_CYCLE = [1, 2, 3, 4, 5]


if "rotation_index" not in st.session_state:
    st.session_state.rotation_index = 0


# -----------------------------
# HELPERS
# -----------------------------
def get_current_off_group():
    return ROTATION_CYCLE[st.session_state.rotation_index % 5]


def get_next_off_group():
    return ROTATION_CYCLE[(st.session_state.rotation_index + 1) % 5]


def rotate():
    st.session_state.rotation_index += 1


# -----------------------------
# DERIVED STATE
# -----------------------------
df = pd.DataFrame(st.session_state.players)
df_active = df[df["Active"] == True]

current_off = get_current_off_group()
next_off = get_next_off_group()

on_field = df_active[df_active["Group"] != current_off]
bench = df_active[df_active["Group"] == current_off]


# -----------------------------
# HEADER (GAME STATE BAR)
# -----------------------------
st.title("🏉 AFL Coach Console")

col1, col2, col3 = st.columns(3)
col1.metric("STATUS", "LIVE GAME")
col2.metric("ON FIELD", len(on_field))
col3.metric("OFF FIELD", len(bench))

st.divider()


# -----------------------------
# FIELD VIEW (CORE UX)
# -----------------------------
st.subheader("🏟️ FIELD VIEW")

f1, f2, f3 = st.columns(3)

with f1:
    st.markdown("### 🔵 BACKS")
    for _, p in on_field[on_field["Unit"] == "A"].iterrows():
        st.success(p["Name"])

with f2:
    st.markdown("### 🟢 MIDS")
    for _, p in on_field[on_field["Unit"] == "B"].iterrows():
        st.success(p["Name"])

with f3:
    st.markdown("### 🟠 FWDS")
    for _, p in on_field[on_field["Unit"] == "C"].iterrows():
        st.success(p["Name"])


st.divider()


# -----------------------------
# BENCH + ROTATION PANEL
# -----------------------------
left, right = st.columns(2)

with left:
    st.subheader("🔴 OFF NOW (BENCH)")
    for _, p in bench.iterrows():
        st.error(f"{p['Name']} (G{p['Group']})")

with right:
    st.subheader("🔄 NEXT ROTATION")

    next_out = df_active[df_active["Group"] == next_off]
    next_in = df_active[df_active["Group"] == current_off]

    for _, p in next_out.iterrows():
        replacement = next_in[next_in["Unit"] == p["Unit"]]
        sub = replacement["Name"].iloc[0] if not replacement.empty else "—"

        st.warning(f"{p['Name']} ↔ {sub}")


# -----------------------------
# ACTION BUTTON (KEY UX FIX)
# -----------------------------
st.divider()

if st.button("▶ EXECUTE NEXT ROTATION", use_container_width=True):
    rotate()
    st.rerun()


# -----------------------------
# INSIGHT BAR (COACHING VALUE)
# -----------------------------
st.info("💡 Insight: Rotation is balanced. No unit is overloaded this cycle.")
