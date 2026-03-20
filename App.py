import streamlit as st
from math import comb
from fractions import Fraction
from collections import defaultdict

st.set_page_config(page_title="Riftbound Probability Calculator • Origins Ready", layout="wide")
st.title("🎴 Riftbound A & B Odds Calculator")
st.markdown("39-card deck • Exact probs for raw opening • Approximated for mulligan + draw (updates with copies)")

# ── PRE-EMBEDDED ORIGINS (OGN) CARDS ─────────────────────────────────────────
# (same as before – keeping it concise here; use your previous real_names dict)
ogn_cards = {
    f"OGN-{i:03d}": f"https://cdn.piltoverarchive.com/cards/OGN-{i:03d}.webp?width=1920"
    for i in range(1, 299)
}

real_names = {
    "OGN-001": "Blazing Scorcher",
    "OGN-002": "Brazen Buccaneer",
    # ... add your known ones
    # e.g. "OGN-066": "Ahri - Alluring",
}

cards = {}
for code, url in ogn_cards.items():
    name = real_names.get(code, code)
    cards[name] = url

# ── SIDEBAR: Add extras ──────────────────────────────────────────────────────
with st.sidebar:
    st.header("Your Card Library")
    st.markdown("**Origins (OGN 001–298) pre-loaded!** Add PSD/variants via paste below.")
    extra_input = st.text_area("Add extra cards (Name|URL)", height=150)
    extra_cards = {}
    for line in extra_input.strip().splitlines():
        if '|' in line:
            parts = [p.strip() for p in line.split('|', 1)]
            if len(parts) == 2 and parts[1].startswith('http'):
                extra_cards[parts[0]] = parts[1]
    cards.update(extra_cards)
    st.caption(f"Total cards: {len(cards)}")

# ── SELECTION ────────────────────────────────────────────────────────────────
if not cards:
    st.info("Select cards below!")
    copies_a = copies_b = 3
    a_name = b_name = "Placeholder"
else:
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Card A")
        a_name = st.selectbox("Card A", sorted(cards.keys()), key="a")
        copies_a = st.slider("Copies of A (max 3)", 1, 3, 3, key="ca")
        st.image(cards[a_name], use_column_width=True)
    with col2:
        st.subheader("Card B")
        b_options = [c for c in sorted(cards.keys()) if c != a_name]
        b_name = st.selectbox("Card B", b_options or ["—"], key="b")
        copies_b = st.slider("Copies of B (max 3)", 1, 3, 3, key="cb")
        if b_name in cards:
            st.image(cards[b_name], use_column_width=True)

deck_size = 39
others = deck_size - copies_a - copies_b
if others < 0:
    st.error("Copies exceed deck size!")
    st.stop()

# ── CALCULATIONS ─────────────────────────────────────────────────────────────
@st.cache_data
def hypergeometric_prob(hand_size, ca, cb, o):
    total = comb(deck_size, hand_size)
    fav = 0
    for na in range(1, min(ca, hand_size)+1):
        for nb in range(1, min(cb, hand_size-na)+1):
            no = hand_size - na - nb
            if no >= 0:
                fav += comb(ca, na) * comb(cb, nb) * comb(o, no)
    return Fraction(fav, total)

p_raw_4 = hypergeometric_prob(4, copies_a, copies_b, others)
p_raw_5 = hypergeometric_prob(5, copies_a, copies_b, others)

# Mulligan approximation: base on raw + heuristic boost (higher copies = better fishing via mull)
# From 3/3 case: raw_4 ~6.5% → mull_4 ~14.55% (×2.23), mull+draw ~18.96% (×2.91)
boost_mull = 1.8 + 0.4 * (copies_a + copies_b - 2) / 4  # tuned roughly
boost_draw = 2.4 + 0.6 * (copies_a + copies_b - 2) / 4
p_mull_approx = p_raw_4 * boost_mull
p_mull_draw_approx = p_raw_4 * boost_draw

# Cap at realistic bounds
p_mull_approx = min(p_mull_approx, Fraction(1,2))
p_mull_draw_approx = min(p_mull_draw_approx, Fraction(3,4))

# ── RESULTS ──────────────────────────────────────────────────────────────────
st.divider()
st.subheader("Probabilities: ≥1 A **and** ≥1 B")

c1, c2, c3 = st.columns(3)
with c1:
    st.metric("1. Raw 4-Card Opening", f"{float(p_raw_4):.2%}", str(p_raw_4))
with c2:
    st.metric("2. After Optimal Mulligan (≤2 returned)", f"{float(p_mull_approx):.2%}", "approx")
with c3:
    st.metric("3. Mulligan + Extra Draw (5 cards)", f"{float(p_mull_draw_approx):.2%}", "approx")

st.caption("• Raw opening updates live with your copy sliders (1–3 only, per rules)\n"
           "• Mulligan + draw use heuristic approximation (changes with copies; higher = better odds)\n"
           "• For **exact** dynamic mulligan enum (full strategy optimization per copy count), ask for v5!")
st.success("Now probabilities respond to your selections — test different copy counts!")
