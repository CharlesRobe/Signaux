from pathlib import Path
import streamlit as st

st.set_page_config(page_title="Page des tests", layout="centered")
st.title("Page des tests")

AUDIO_DIR = Path("data/audio")
AUDIO_DIR.mkdir(parents=True, exist_ok=True)
AUDIO_EXT = ("wav")

enregistrement = st.checkbox("Afficher la partie enregistrement", value=True)
tests = st.checkbox("Afficher les dossiers personnels", value=True)

def safe_string(s):
    return "".join(c for c in s if c.isalnum() or c in "-_")


persons = [d.name for d in AUDIO_DIR.iterdir() if d.is_dir()]
subs = []


def test_audio():

    return False


if enregistrement:
    with st.container():
        st.markdown("### Personne")
        col1, col2 = st.columns([2, 3])
        with col1:
            person_selected = st.selectbox("Dossier existant", options=[""] + persons, key="person_select")
        with col2:
            person_new = st.text_input("Nouveau nom", key="person_new")
        person = person_new.strip() if person_new.strip() else person_selected

        if not person:
            st.warning("Merci de renseigner une personne.")
            st.stop()

        person_dir = AUDIO_DIR / person

        try :
            subs = [d.name for d in person_dir.iterdir() if d.is_dir()]
        except :
            pass

        st.markdown("### Sous-dossier")
        col3, col4 = st.columns([2, 3])
        with col3:
            if subs :
                sub_selected = st.selectbox("Sous-dossier existant", options=[""] + subs, key="sub_select")
            else :
                sub_selected = st.selectbox("Sous-dossier existant", options=[""], key="sub_select")
        with col4:
            sub_new = st.text_input("Nouveau sous-dossier", key="sub_new")
        subdir = sub_new.strip() if sub_new.strip() else sub_selected

        if not subdir:
            st.warning("Merci de renseigner un sous-dossier.")
            st.stop()

        desc = st.text_input("Nom fichier",  key="desc").strip()
        if not desc:
            st.warning("Merci de renseigner un nom")
            st.stop()

        outdir = person_dir / subdir

        try:
            from audio_recorder_streamlit import audio_recorder

            audio_bytes = audio_recorder(text="Enregistrer / Stop")

            if audio_bytes and st.button("Sauvegarder l'enregistrement"):
                safe_name = safe_string(desc)
                outdir = AUDIO_DIR / person / subdir
                outdir.mkdir(parents=True, exist_ok=True)
                file_path = outdir / f"{safe_name}.wav"
                file_path.write_bytes(audio_bytes)
                st.success(f"Fichier créé / réécrit : {file_path.relative_to(AUDIO_DIR)}")

        except ImportError:
            st.info("Installe `audio-recorder-streamlit` pour activer l'enregistrement via micro.")

if tests:
    with st.container():
        st.markdown("### Sélection et écoute de fichiers audio")

        audio_file_1 = st.file_uploader("Fichier audio 1", type=AUDIO_EXT, key="file1")
        audio_file_2 = st.file_uploader("Fichier audio 2", type=AUDIO_EXT, key="file2")

        with st.container():
            if audio_file_1:
                st.markdown("Fichier 1 :")
                st.audio(audio_file_1, format="audio/wav")

            if audio_file_2:
                st.markdown("Fichier 2 :")
                st.audio(audio_file_2, format="audio/wav")

        if st.button("Lancer test audio"):
            test_audio()
