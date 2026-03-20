import streamlit as st
from math import comb
from fractions import Fraction

st.set_page_config(page_title="Riftbound Calculator - All Origins Included", layout="wide")
st.title("🎴 Riftbound A & B Requirement Calculator")
st.markdown("**39-card deck** • Exact P(≥ req_A of A **and** ≥ req_B of B) in 4-card opening hand")

# ── ALL ORIGINS (OGN) CARDS PRE-EMBEDDED (298 total) ─────────────────────────
# URLs follow: https://cdn.piltoverarchive.com/cards/OGN-XXX.webp?width=1920
# Real names for known cards (from checklists: beckett, totalcards, getcollectr, riftbound.gg)
# Rest use OGN-XXX as display name (searchable in dropdown)
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
    "OGN-010": "Legion Rearguard",  # or Legion Guard in some lists
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
    # Add more known Champions/important cards as you find them
    # "OGN-066": "Ahri - Alluring",  # example placeholder - replace with real if confirmed
    # "OGN-269": "Sett, The Boss",
    # ... continue for others you care about
}

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

# ── CALCULATION FUNCTION ─────────────────────────────────────────────────────
@st.cache_data
def calc_prob(hand_size, deck_a, deck_b, others, req_a, req_b):
    if req_a + req_b > hand_size:
        return Fraction(0)
    total = comb(deck_size, hand_size)
    fav = 0
    max_a = min(deck_a, hand_size)
    max_b = min(deck_b, hand_size)
    for na in range(req_a, max_a + 1):
        for nb in range(req_b, max_b - (na - req_a) + 1):  # optimized range
            no = hand_size - na - nb
            if no >= 0:
                fav += comb(deck_a, na) * comb(deck_b, nb) * comb(others, no)
    return Fraction(fav, total)

p_raw_4 = calc_prob(4, deck_a, deck_b, others, req_a, req_b)

# Mulligan probs (still fixed to original ≥1/≥1 for 3/3; can expand later)
p_mull_4 = Fraction(67801, 466089)
p_mull_draw = Fraction(3093227, 16313115)

# ── DISPLAY RESULTS ──────────────────────────────────────────────────────────
st.divider()
st.subheader(f"P(≥{req_a} {a_name} **and** ≥{req_b} {b_name})")

c1, c2, c3 = st.columns(3)
with c1:
    st.metric("Raw 4-Card Opening", f"{float(p_raw_4):.2%}", f"{p_raw_4}")
with c2:
    st.metric("After Optimal Mulligan (4 cards)", f"{float(p_mull_4):.2%}", "fixed ≥1/≥1")
with c3:
    st.metric("Mulligan + Extra Draw (5 cards)", f"{float(p_mull_draw):.2%}", "fixed ≥1/≥1")

if req_a + req_b > 4:
    st.warning("Requirement impossible in 4 cards → probability = 0% (as expected)")

st.caption("""
• All 298 Origins cards are now built-in (no paste needed for base set)
• Real names for many popular/early cards; others show as OGN-XXX (easy to find)
• Raw probability fully dynamic and matches your definition
• Mulligan values are still from the classic ≥1/≥1 3-copy case
""")
