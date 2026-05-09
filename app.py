import streamlit as st
import time
import pandas as pd
from datetime import datetime

# --- CONFIG & SESSION STATE ---
st.set_page_config(layout="centered", page_title="AFL Game Day Manager")

if 'game_active' not in st.session_state:
    st.session_state.game_active = False
    st.session_state.start_time = 0
    st.session_state.time_remaining = 900  # 15 mins in seconds
    st.session_state.score = {"RMF": {"G": 0, "B": 0}, "OPPO": {"G": 0, "B": 0}}
    st.session_state.log = []
    # Mock Data for Initial Setup
    st.session_state.players = {
        "Back": ["A. Hardwich", "Q. Tran", "P. Nair", "T. Chan"],
        "Mid": ["K. Williams", "B. Carter", "F. Rahman", "D. Russo"],
        "Fwd": ["P. Garner", "L. Wilson", "N. Nguyen", "P. Kyriacou"],
        "Bench": ["H. Moore", "N. Gianno", "L. Moore"]
    }

# --- STYLING ---
st.markdown("""
    <style>
    .player-card { border: 2px solid #3498db; border-radius: 8px; padding: 10px; text-align: center; background: white; margin: 5px; }
    .bench-card { border: 2px dashed #95a5a6; border-radius: 8px; padding: 10px; background: #ecf0f1; margin: 5px; }
    .swap-arrow { font-size: 20px; color: #e67e22; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# --- FUNCTIONS ---
def update_score(team, type, val):
    st.session_state.score[team][type] += val
    st.session_state.log.append(f"{type} added for {team}")

def undo_score():
    if st.session_state.log:
        last_action = st.session_state.log.pop()
        # Logic to decrement score based on log string...
        st.toast(f"Undone: {last_action}")

# --- HEADER & CLOCK ---
col1, col2, col3 = st.columns([1,2,1])
with col2:
    st.title("⏱️ 15:00") # Logic for countdown timer would go here
    st.subheader(f"RMF: {st.session_state.score['RMF']['G']}.{st.session_state.score['RMF']['B']} ({st.session_state.score['RMF']['G']*6 + st.session_state.score['RMF']['B']})")

# --- SCORE CONTROLS ---
with st.expander("Score Correction / Entry"):
    c1, c2 = st.columns(2)
    with c1:
        st.button("+6 RMF", on_click=update_score, args=("RMF", "G", 1))
        st.button("+1 RMF", on_click=update_score, args=("RMF", "B", 1))
    with c2:
        st.button("+6 OPPO", on_click=update_score, args=("OPPO", "G", 1))
        st.button("+1 OPPO", on_click=update_score, args=("OPPO", "B", 1))
    st.button("Undo Last Action", on_click=undo_score)

# --- THE FIELD (12-MAN GRID) ---
st.divider()
st.markdown("### 🏟️ THE FIELD")

for zone in ["Fwd", "Mid", "Back"]:
    st.caption(f"--- {zone.upper()} ---")
    cols = st.columns(4)
    for i, player in enumerate(st.session_state.players[zone]):
        with cols[i]:
            st.markdown(f"<div class='player-card'>{player}</div>", unsafe_allow_html=True)

# --- THE ROTATION "STAGE" ---
st.divider()
st.markdown("### 🔄 PLANNED ROTATION (Due @ 7:30)")

# This pair shows the Bench kid and who they are slated to replace
r1, r2, r3 = st.columns(3)
with r1:
    st.markdown(f"<div class='bench-card'><b>{st.session_state.players['Bench'][0]}</b><div class='swap-arrow'>↓</div>{st.session_state.players['Back'][0]}</div>", unsafe_allow_html=True)
with r2:
    st.markdown(f"<div class='bench-card'><b>{st.session_state.players['Bench'][1]}</b><div class='swap-arrow'>↓</div>{st.session_state.players['Mid'][0]}</div>", unsafe_allow_html=True)
with r3:
    st.markdown(f"<div class='bench-card'><b>{st.session_state.players['Bench'][2]}</b><div class='swap-arrow'>↓</div>{st.session_state.players['Fwd'][0]}</div>", unsafe_allow_html=True)

if st.button("COMMIT ALL ROTATIONS", use_container_width=True, type="primary"):
    # Swap Logic here
    st.success("Rotations Executed & Logged!")

# --- EXPORT ---
if st.button("End Game & Export Stats"):
    st.write("Generating CSV...")
