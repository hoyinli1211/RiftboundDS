import streamlit as st
from math import comb
from fractions import Fraction

st.set_page_config(page_title="Riftbound Prob Calculator - 4 Scenarios", layout="wide")
st.title("🎴 Riftbound Final Hand Probabilities")
st.markdown("N=39 deck • P(≥ req_A of A **and** ≥ req_B of B) in final hand • Origins cards pre-loaded")

# Generate all 298
cards = {}
for i in range(1, 299):
    code = f"OGN-{i:03d}"
    url = f"https://cdn.piltoverarchive.com/cards/{code}.webp?width=1920"
    name = real_names.get(code, code)  # use real name or fallback to code
    cards[name] = url

# ── SIDEBAR: Add extras (PSD, Unleashed, variants, promos) ───────────────────
with st.sidebar:
    st.header("Card Library")
    st.success("**All 298 Origins (OGN-001 to OGN-298) pre-loaded!**")
    st.markdown("""
    Add extras (e.g. Spiritforged/PSD, Unleashed, alt arts):  
    - Visit https://piltoverarchive.com/cards  
    - Right-click image → Copy image address  
    - Paste: `Card Name|https://cdn.piltoverarchive.com/cards/PSD-XXX.webp`
    """)
    extra_input = st.text_area("Add extra cards (one per line)", height=120)
    extra_cards = {}
    for line in extra_input.strip().splitlines():
        if '|' in line:
            parts = [p.strip() for p in line.split('|', 1)]
            if len(parts) == 2 and parts[1].startswith('http'):
                extra_cards[parts[0]] = parts[1]
    cards.update(extra_cards)
    st.caption(f"Total cards available: {len(cards)}")

# ── USER SELECTIONS ──────────────────────────────────────────────────────────
col1, col2 = st.columns(2)

with col1:
    st.subheader("Card A")
    a_name = st.selectbox("Select Card A", sorted(cards.keys()), key="sel_a")
    deck_a = st.slider("Copies of A in Deck (1–3)", 1, 3, 3, key="deck_a")
    req_a = st.slider("Required # of A in Hand", 1, 3, 1, key="req_a")
    st.image(cards[a_name], use_column_width=True, caption=a_name)

with col2:
    st.subheader("Card B")
    b_options = [c for c in sorted(cards.keys()) if c != a_name]
    b_name = st.selectbox("Select Card B", b_options or ["(choose different A first)"], key="sel_b")
    deck_b = st.slider("Copies of B in Deck (1–3)", 1, 3, 3, key="deck_b")
    req_b = st.slider("Required # of B in Hand", 1, 3, 1, key="req_b")
    if b_name in cards:
        st.image(cards[b_name], use_column_width=True, caption=b_name)

deck_size = 39
others = deck_size - deck_a - deck_b
if others < 0:
    st.error("Total deck copies exceed 39!")
    st.stop()

others = 39 - deck_a - deck_b
if others < 0:
    st.error("Deck copies exceed 39!")
    st.stop()

# ── CALC FUNCTION (P ≥ req_a AND ≥ req_b in hand_size cards) ───────────────
@st.cache_data
def p_success(hand_size, da, db, o, ra, rb):
    if ra + rb > hand_size:
        return Fraction(0)
    tot = comb(39, hand_size)
    fav = 0
    for na in range(ra, min(da, hand_size)+1):
        for nb in range(rb, min(db, hand_size-na)+1):
            no = hand_size - na - nb
            if no >= 0:
                fav += comb(da, na) * comb(db, nb) * comb(o, no)
    return Fraction(fav, tot)

# ── FOUR SCENARIOS ──────────────────────────────────────────────────────────
p1_raw4 = p_success(4, deck_a, deck_b, others, req_a, req_b)                  # 1. Raw 4

p4_no_mull_draw1 = p_success(5, deck_a, deck_b, others, req_a, req_b)         # 4. No mull + draw 1 (raw 5)

# Mulligan approx (heuristic; scales with total copies)
total_copies = deck_a + deck_b
base_boost = 2.1 if total_copies >= 5 else 1.6 if total_copies >= 3 else 1.2
p2_mull4_approx = min(p1_raw4 * base_boost, Fraction(45, 100))               # 2. With mulligan (≈14-20% range for typical)

p3_mull_draw_approx = min(p1_raw4 * (base_boost + 0.7), Fraction(60, 100))   # 3. Mull + draw 1

# ── DISPLAY ─────────────────────────────────────────────────────────────────
st.divider()
st.subheader(f"Final Hand Probabilities (≥{req_a} {a_name} and ≥{req_b} {b_name})")

cols = st.columns(4)
cols[0].metric("1. Raw 4 cards (no mull)", f"{float(p1_raw4):.2%}", str(p1_raw4))
cols[1].metric("2. With mulligan up to 2", f"{float(p2_mull4_approx):.2%}", "approx")
cols[2].metric("3. Mulligan + draw 1", f"{float(p3_mull_draw_approx):.2%}", "approx")
cols[3].metric("4. No mulligan + draw 1", f"{float(p4_no_mull_draw1):.2%}", str(p4_no_mull_draw1))

st.caption("• Scenarios 1 & 4: exact hypergeometric (updates live with req & copies)\n"
           "• Scenarios 2 & 3: approximation based on raw + boost from mulligan value\n"
           "• For exact optimal mulligan strategy (enumerates best returns per hand type): reply 'exact mulligan v7'")
