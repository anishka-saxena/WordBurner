import streamlit as st
from roast import get_roast, get_surprise_roast, get_simple_phonetic
from gtts import gTTS
from io import BytesIO
import requests
import re

st.set_page_config(page_title="WordBurner", page_icon="🔥", layout="centered")


def get_audio_url(word):
    try:
        response = requests.get(f"https://api.dictionaryapi.dev/api/v2/entries/en/{word}")
        if response.status_code != 200:
            return None
        data = response.json()
        for p in data[0].get("phonetics", []):
            if p.get("audio"):
                return p["audio"]
        return None
    except Exception:
        return None


def make_gtts_audio(word, slow=False):
    tts = gTTS(text=word, lang="en", slow=slow)
    buf = BytesIO()
    tts.write_to_fp(buf)
    buf.seek(0)
    return buf


def extract_word_from_result(result):
    for line in result.splitlines():
        if "📌 Word:" in line:
            return line.split("📌 Word:")[-1].strip().strip("*").strip()
    return None


def parse_cards(result):
    # Section headings and their grouping
    # Card 2 groups Synonyms + Antonyms together
    headings = ["📖", "📚", "🧠", "🌍", "💬", "👨‍👩‍👧"]
    lines = result.splitlines()

    # Find line indices where each heading starts
    heading_positions = {}
    for i, line in enumerate(lines):
        for h in headings:
            if h in line and i not in heading_positions.values():
                if h not in heading_positions:
                    heading_positions[h] = i
                break

    # Build ordered list of (heading_index, heading_emoji)
    ordered = sorted((idx, emoji) for emoji, idx in heading_positions.items())

    # Extract text slices per heading
    sections = {}
    for pos, (line_idx, emoji) in enumerate(ordered):
        end = ordered[pos + 1][0] if pos + 1 < len(ordered) else len(lines)
        sections[emoji] = "\n".join(lines[line_idx:end]).strip()

    # Build 6 cards: card 2 merges 📚 and 🔄 (antonyms are inside 📚 section)
    cards = []
    for emoji in headings:
        if emoji in sections:
            cards.append(sections[emoji])

    # If we got fewer than 6 (e.g. 📚 already contains antonyms), keep as-is
    return cards if cards else [result]


# Session state init
for key, default in [
    ("result", None), ("current_word", None), ("phonetic", None),
    ("show_result", False), ("cards", []), ("card_index", 0),
    ("input_value", ""), ("mode", None),
    ("audio_url", None), ("audio_bytes", None),
    ("beginner_used", []), ("intermediate_used", []), ("advanced_used", []),
]:
    if key not in st.session_state:
        st.session_state[key] = default


def set_new_word(w, result):
    st.session_state.current_word = w
    st.session_state.phonetic = get_simple_phonetic(w)
    st.session_state.result = result
    st.session_state.cards = parse_cards(result)
    st.session_state.card_index = 0
    st.session_state.show_result = True
    audio_url = get_audio_url(w)
    st.session_state.audio_url = audio_url
    if not audio_url:
        buf = make_gtts_audio(w, slow=False)
        st.session_state.audio_bytes = buf.read()
    else:
        st.session_state.audio_bytes = None


# ── Header ────────────────────────────────────────────────
st.markdown("## WordBurner 🔥")
st.markdown("<small style='color:gray;'>Vocabulary learning with zero mercy 😂</small>", unsafe_allow_html=True)

# ── Input ─────────────────────────────────────────────────
word_input = st.text_input(
    "", placeholder="Type a word...", label_visibility="collapsed",
    value=st.session_state.get("input_value", "")
)

if st.button("Discover! 🚀", use_container_width=True):
    if not word_input.strip():
        st.warning("Enter a word first 😂")
    else:
        w = word_input.strip().lower()
        st.session_state.input_value = word_input.strip()
        st.session_state.mode = "discover"
        with st.spinner("Burning your word... 🔥"):
            result = get_roast(w)
        set_new_word(w, result)

# ── Result ────────────────────────────────────────────────
if st.session_state.show_result and st.session_state.result:
    left, right = st.columns([2, 1])

    with left:
        word = st.session_state.current_word
        phonetic = st.session_state.phonetic

        # Pronunciation
        if phonetic:
            st.markdown(f"**🔊 {word.upper()}** &nbsp; {phonetic}")
        else:
            st.markdown(f"**🔊 {word.upper()}**")
        if st.session_state.audio_url:
            st.audio(st.session_state.audio_url)
        elif st.session_state.audio_bytes:
            st.audio(st.session_state.audio_bytes, format="audio/mp3")

        # Flashcard
        cards = st.session_state.cards
        idx = st.session_state.card_index
        total = len(cards)

        if cards:
            with st.container(border=True):
                # Counter top-right
                st.markdown(
                    f"<div style='text-align:right; color:gray; font-size:0.8rem;'>{idx + 1}/{total}</div>",
                    unsafe_allow_html=True,
                )
                st.text(cards[idx])

                # Navigation buttons
                btn_left, btn_right = st.columns(2)
                with btn_left:
                    if st.button("← Back", disabled=(idx == 0), use_container_width=True):
                        st.session_state.card_index -= 1
                        st.rerun()
                with btn_right:
                    if st.button("Next →", disabled=(idx == total - 1), use_container_width=True):
                        st.session_state.card_index += 1
                        st.rerun()

    with right:
        st.markdown("**🎲 Try a new word?**")
        for level, icon in [("Beginner", "🟢"), ("Intermediate", "🟡"), ("Advanced", "🔴")]:
            if st.button(f"{icon} {level}", key=f"surprise_{level}", use_container_width=True):
                used_key = f"{level.lower()}_used"
                used_words = st.session_state[used_key]
                with st.spinner("Burning your word... 🔥"):
                    result = get_surprise_roast(level, used_words)
                extracted = extract_word_from_result(result)
                w = extracted.lower() if extracted else level.lower()
                if extracted:
                    st.session_state[used_key] = used_words + [extracted.lower()]
                set_new_word(w, result)
                st.session_state.input_value = ""
                st.session_state.mode = "surprise"
                st.rerun()
        st.markdown("<small style='color:gray;'>We pick, you learn 😂</small>", unsafe_allow_html=True)
