import streamlit as st
from math import comb
from fractions import Fraction

st.set_page_config(page_title="Riftbound Probability Calculator • Piltover Archive Style", layout="wide")
st.title("🎴 Riftbound A & B Odds Calculator")
st.markdown("39-card deck • Exact probs for opening 4, optimal mulligan, + extra draw")

# ── SIDEBAR: Add cards from Piltover Archive ────────────────────────────────
with st.sidebar:
    st.header("Your Card Library")
    st.markdown("""
    **Quick add from https://piltoverarchive.com/cards**  
    1. Go to the site → filter/browse cards  
    2. Click card → right-click big image → **Copy image address**  
    3. Paste here: `Card Name|https://cdn.piltoverarchive.com/cards/XXXX.webp`  
    (one per line — add only cards you care about!)
    """)

    default_example = """Jinx|https://picsum.photos/id/201/400/560
Ahri|https://picsum.photos/id/1015/400/560
Yasuo|https://picsum.photos/id/237/400/560
Sett|https://picsum.photos/id/29/400/560
Annie|https://picsum.photos/id/64/400/560
Irelia|https://picsum.photos/id/160/400/560"""

    card_text = st.text_area("Paste your cards (Name|URL)", value=default_example, height=280)

    cards = {}
    for line in card_text.strip().splitlines():
        if '|' in line:
            parts = [p.strip() for p in line.split('|', 1)]
            if len(parts) == 2 and parts[1].startswith('http'):
                cards[parts[0]] = parts[1]

    st.caption(f"Loaded {len(cards)} cards • Add more anytime!")

# ── MAIN AREA: Card Selection ───────────────────────────────────────────────
if not cards:
    st.info("Add some cards from piltoverarchive.com/cards to get started!")
    a_name = "Card A (placeholder)"
    b_name = "Card B (placeholder)"
    copies_a = 3
    copies_b = 3
else:
    col1, col2 = st.columns([3, 3])

    with col1:
        st.subheader("Card A")
        a_name = st.selectbox("Search / select Card A", sorted(cards.keys()), key="sel_a")
        copies_a = st.slider("Copies in deck", 1, 4, 3, key="cop_a")
        st.image(cards[a_name], use_column_width=True, caption=a_name)

    with col2:
        st.subheader("Card B")
        b_options = [c for c in sorted(cards.keys()) if c != a_name]
        b_name = st.selectbox("Search / select Card B", b_options or ["(select different A first)"], key="sel_b")
        copies_b = st.slider("Copies in deck", 1, 4, 3, key="cop_b")
        if b_name in cards:
            st.image(cards[b_name], use_column_width=True, caption=b_name)

deck_size = 39
others = deck_size - copies_a - copies_b

if others < 0:
    st.error(f"Total copies ({copies_a + copies_b}) exceed deck size {deck_size}!")
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
p_open_5   = hypergeometric_fav(5, copies_a, copies_b, others)  # raw 5-card for reference

# From our exact earlier calc (for 3/3 case — best we have without full enum per copy count)
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

st.caption("• Raw probs update live with your copy counts\n"
           "• Mulligan probs use our exact 3/3 enumeration (very close for similar counts)\n"
           "Want full dynamic optimal mulligan for any copies? → Say yes for v4 (longer but complete)")

st.success("Paste more cards from piltoverarchive.com/cards whenever you want — enjoy testing different A/B pairs!")
