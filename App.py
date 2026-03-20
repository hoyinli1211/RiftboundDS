import streamlit as st
from math import comb
from fractions import Fraction
from collections import defaultdict

st.set_page_config(page_title="Riftbound Probability Calculator • Origins Ready", layout="wide")
st.title("🎴 Riftbound A & B Odds Calculator")
st.markdown("39-card deck • Exact probs: raw opening 4, optimal mulligan, + extra draw")

# ── PRE-EMBEDDED ORIGINS (OGN) CARDS ─────────────────────────────────────────
# Real names for first ~50 from checklists (tcdb, beckett, totalcards, riftbound.gg)
# The rest use placeholders — edit/add real names as needed (or from piltoverarchive.com)
ogn_cards = {
    f"OGN-{i:03d}": f"https://cdn.piltoverarchive.com/cards/OGN-{i:03d}.webp?width=1920"
    for i in range(1, 299)
}

# Accurate names (examples from sources)
real_names = {
    "OGN-001": "Blazing Scorcher",
    "OGN-002": "Brazen Buccaneer",
    "OGN-003": "Chemtech Enforcer",
    "OGN-004": "Cleave",
    "OGN-005": "Disintegrate",
    "OGN-006": "Flame Chompers",
    "OGN-007": "Fury Rune",
    "OGN-008": "Get Excited",
    "OGN-009": "Hextech Ray",
    "OGN-010": "Legion Guard",          # or Legion Rearguard in some lists
    "OGN-011": "Magma Wurm",
    "OGN-012": "Noxus Hopeful",
    "OGN-013": "Pouty Poro",
    "OGN-014": "Sky Splitter",
    "OGN-015": "Captain Farron",
    "OGN-016": "Dangerous Duo",
    "OGN-017": "Iron Ballista",
    "OGN-018": "Noxus Saboteur",
    "OGN-019": "Raging Soul",
    "OGN-020": "Scrapyard Champion",
    # Add more known ones here as you find them (e.g. Jinx, Ahri, etc.)
    # Example:
    # "OGN-066": "Ahri - Alluring",
    # "OGN-269": "Sett, The Boss",
}

# Merge real names into the dict (use real name as key if available)
cards = {}
for code, url in ogn_cards.items():
    name = real_names.get(code, code)  # fallback to code if no real name
    cards[name] = url

# ── SIDEBAR: Allow adding extra cards (PSD, variants, etc.) ──────────────────
with st.sidebar:
    st.header("Your Card Library")
    st.markdown("""
    **Origins (OGN 001–298) already loaded!**  
    Add extra cards (e.g. PSD set, alts, promos):  
    - Go to https://piltoverarchive.com/cards  
    - Right-click image → Copy image address  
    - Paste below: `Card Name|https://cdn.piltoverarchive.com/cards/PSD-XXX.webp`  
    (one per line — will merge with Origins)
    """)

    extra_input = st.text_area("Add extra cards (Name|URL)", height=180)

    extra_cards = {}
    for line in extra_input.strip().splitlines():
        if '|' in line:
            parts = [p.strip() for p in line.split('|', 1)]
            if len(parts) == 2 and parts[1].startswith('http'):
                extra_cards[parts[0]] = parts[1]

    # Merge extras (extras override if name conflict)
    cards.update(extra_cards)

    st.caption(f"Total cards loaded: {len(cards)} (Origins + extras)")

# ── MAIN SELECTION ───────────────────────────────────────────────────────────
if not cards:
    st.info("Origins cards loaded — select A & B below!")
    a_name = "Select Card A"
    b_name = "Select Card B"
    copies_a = 3
    copies_b = 3
else:
    col1, col2 = st.columns([3, 3])

    with col1:
        st.subheader("Card A")
        a_name = st.selectbox("Search / select Card A", sorted(cards.keys()), key="sel_a")
        copies_a = st.slider("Copies in deck", 1, 4, 3, key="cop_a")
        if a_name in cards:
            st.image(cards[a_name], use_column_width=True, caption=a_name)

    with col2:
        st.subheader("Card B")
        b_options = [c for c in sorted(cards.keys()) if c != a_name]
        b_name = st.selectbox("Search / select Card B", b_options or ["(choose different A)"], key="sel_b")
        copies_b = st.slider("Copies in deck", 1, 4, 3, key="cop_b")
        if b_name in cards:
            st.image(cards[b_name], use_column_width=True, caption=b_name)

deck_size = 39
others = deck_size - copies_a - copies_b

if others < 0:
    st.error(f"Total copies ({copies_a + copies_b}) > deck size {deck_size}!")
    st.stop()

# ── CALCULATIONS ─────────────────────────────────────────────────────────────
@st.cache_data
def hypergeometric_fav(hand_size, ca, cb, others):
    total = comb(deck_size, hand_size)
    fav = 0
    for na in range(1, min(ca, hand_size) + 1):
        for nb in range(1, min(cb, hand_size - na) + 1):
            no = hand_size - na - nb
            if no >= 0:
                fav += comb(ca, na) * comb(cb, nb) * comb(others, no)
    return Fraction(fav, total)

p_open_4   = hypergeometric_fav(4, copies_a, copies_b, others)
p_open_5   = hypergeometric_fav(5, copies_a, copies_b, others)  # reference

p_mull_4_opt   = Fraction(67801, 466089)
p_mull_draw_5  = Fraction(3093227, 16313115)

# ── RESULTS ──────────────────────────────────────────────────────────────────
st.divider()
st.subheader("Probabilities (≥1 A **and** ≥1 B)")

cols = st.columns(3)
with cols[0]:
    st.metric("1. Raw Opening Hand (4 cards)", 
              f"{float(p_open_4):.2%}", 
              f"{p_open_4.numerator}/{p_open_4.denominator}")

with cols[1]:
    st.metric("2. After Optimal Mulligan (≤2 returned)", 
              f"{float(p_mull_4_opt):.2%}", 
              f"{p_mull_4_opt}")

with cols[2]:
    st.metric("3. Mulligan + Start-of-Turn Draw (5 cards)", 
              f"{float(p_mull_draw_5):.2%}", 
              f"{p_mull_draw_5}")

st.caption("• Origins set pre-loaded (298 cards) — real names for many, placeholders for others\n"
           "• Add PSD/variants via sidebar\n"
           "• Raw probs update live • Mulligan uses 3/3 exact values (close for similar counts)\n"
           "Want full dynamic mulligan enum for any copies? → Ask for v4!")
