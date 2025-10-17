from pathlib import Path
from datetime import datetime
import streamlit as st

# --- Config + masquage sidebar ---
st.set_page_config(page_title="🧪 Tests", layout="centered", initial_sidebar_state="collapsed")
st.markdown("<style>[data-testid='stSidebar'],[data-testid='stSidebarNav']{display:none;}</style>", unsafe_allow_html=True)

st.title("🧪 Tests audio")

# Lien retour (fiable)
st.page_link("app.py", label="🏠 Accueil")

TESTS_DIR = Path("data/tests"); TESTS_DIR.mkdir(parents=True, exist_ok=True)
AUDIO_EXT = ("wav", "mp3", "m4a", "ogg", "flac")

# Enregistrement micro (optionnel)
st.subheader("Enregistrer depuis le micro")
try:
    from audio_recorder_streamlit import audio_recorder
    audio_bytes = audio_recorder(text="🎙️ Enregistrer / Stop")
    name_rec = st.text_input("Nom du fichier", value=f"rec_{datetime.now():%Y%m%d_%H%M%S}")
    if audio_bytes and st.button("💾 Sauver l'enregistrement"):
        safe = "".join(c for c in name_rec if c.isalnum() or c in "-_") or "rec"
        out = TESTS_DIR / f"{safe}.wav"
        if out.exists():
            st.warning("Nom déjà utilisé.")
        else:
            out.write_bytes(audio_bytes)
            st.success(f"Créé : {out.name}")
except Exception:
    st.info("Active le micro avec : `pip install audio-recorder-streamlit`")

st.divider()

# Upload simple
st.subheader("Uploader un fichier")
up = st.file_uploader("Fichier audio", type=list(AUDIO_EXT))
if up and st.button("➕ Ajouter"):
    out = TESTS_DIR / up.name
    if out.exists(): st.warning("Existe déjà.")
    else: out.write_bytes(up.read()); st.success(f"Ajouté : {out.name}")

st.divider()

# Liste + Test (placeholder) + Suppression
st.subheader("Enregistrements")
files = [f for f in sorted(TESTS_DIR.glob("*")) if f.suffix.lower().lstrip(".") in AUDIO_EXT]
if not files:
    st.info("Aucun enregistrement pour l’instant.")
else:
    for f in files:
        with st.container(border=True):
            st.write(f"**{f.name}**"); st.audio(str(f))
            c1, c2 = st.columns(2)
            if c1.button("✅ Tester", key=f"t-{f.name}"):
                ok = "ref" in f.stem.lower()  # règle factice lisible
                st.success("PASS") if ok else st.error("FAIL")
            if c2.button("🗑️ Supprimer", key=f"d-{f.name}"):
                f.unlink(missing_ok=True); st.rerun()
