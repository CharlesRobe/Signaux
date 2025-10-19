from pathlib import Path
from datetime import datetime
import streamlit as st

st.set_page_config(page_title="🧪 Tests", layout="centered", initial_sidebar_state="collapsed")
st.markdown("<style>[data-testid='stSidebar'],[data-testid='stSidebarNav']{display:none;}</style>",
            unsafe_allow_html=True)

st.title("Tests")
st.page_link("app.py", label="Accueil")

AUDIO_DIR = Path("data/audio")
AUDIO_DIR.mkdir(parents=True, exist_ok=True)
AUDIO_EXT = ("wav", "mp3", "m4a", "ogg", "flac")

# Initialiser session_state pour garder les infos remplies
if "person" not in st.session_state:
    st.session_state.person = ""
if "subdir" not in st.session_state:
    st.session_state.subdir = ""
if "desc" not in st.session_state:
    st.session_state.desc = f"rec_{datetime.now():%Y%m%d_%H%M%S}"

# Regrouper tout dans un seul conteneur/rectangle
with st.expander("Nouvel enregistrement", expanded=True):
    persons = [p.name for p in AUDIO_DIR.iterdir() if p.is_dir()]
    # Choix ou création personne
    sel_person = st.selectbox("Personne", ["(nouvelle)"] + persons, index=0 if st.session_state.person == "" else None)
    if sel_person == "(nouvelle)":
        new_person = st.text_input("Nouvelle personne", value=st.session_state.person)
        st.session_state.person = new_person.strip()
    else:
        st.session_state.person = sel_person

    if not st.session_state.person:
        st.warning("Saisis une personne.")
        st.stop()

    person_dir = AUDIO_DIR / st.session_state.person
    person_dir.mkdir(exist_ok=True)

    subs = [p.name for p in person_dir.iterdir() if p.is_dir()]
    sel_sub = st.selectbox("Sous-dossier", ["(nouveau)"] + subs, index=0 if st.session_state.subdir == "" else None)
    if sel_sub == "(nouveau)":
        new_sub = st.text_input("Nouveau sous-dossier", value=st.session_state.subdir)
        st.session_state.subdir = new_sub.strip()
    else:
        st.session_state.subdir = sel_sub

    if not st.session_state.subdir:
        st.warning("Saisis un sous-dossier.")
        st.stop()

    desc = st.text_input("Nom / description", value=st.session_state.desc)
    st.session_state.desc = desc.strip() or st.session_state.desc

    # Boutons Enregistrement et upload
    try:
        from audio_recorder_streamlit import audio_recorder

        audio_bytes = audio_recorder(text="🎙 Enregistrer / Stop")
        if audio_bytes and st.button("Sauvegarder l'enregistrement"):
            outdir = person_dir / st.session_state.subdir
            outdir.mkdir(parents=True, exist_ok=True)
            safe = "".join(c for c in st.session_state.desc if c.isalnum() or c in "-_") or "rec"
            out = outdir / f"{safe}.wav"
            if out.exists():
                st.warning("Nom déjà utilisé.")
            else:
                out.write_bytes(audio_bytes)
                st.success(f"Créé : {out.relative_to(AUDIO_DIR)}")
    except Exception:
        st.info("Active le micro avec : `pip install audio-recorder-streamlit`")

    up = st.file_uploader("Uploader un fichier audio", type=list(AUDIO_EXT))
    if up and st.button("Ajouter le fichier"):
        outdir = person_dir / st.session_state.subdir
        outdir.mkdir(parents=True, exist_ok=True)
        out = outdir / up.name
        if out.exists():
            st.warning("Fichier existe déjà.")
        else:
            out.write_bytes(up.read())
            st.success(f"Ajouté : {out.relative_to(AUDIO_DIR)}")

st.divider()

# Liste des fichiers triés
st.subheader("Enregistrements")
all_files = list(AUDIO_DIR.rglob("*"))
files = [f for f in all_files if f.suffix.lower().lstrip(".") in AUDIO_EXT]
if not files:
    st.info("Aucun enregistrement.")
else:
    for f in sorted(files):
        with st.container(border=True):
            st.write(f"**{f.relative_to(AUDIO_DIR)}**")
            st.audio(str(f))
            c1, c2 = st.columns(2)
            if c1.button("Tester", key=f"t-{f}"):
                ok = "ref" in f.stem.lower()
                st.success("PASS") if ok else st.error("FAIL")
            if c2.button("Supprimer", key=f"d-{f}"):
                f.unlink(missing_ok=True)
                st.rerun()
