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
        stop=0
        st.markdown("### Personne")
        col1, col2 = st.columns([2, 3])
        with col1:
            person_selected = st.selectbox("Dossier existant", options=[""] + persons, key="person_select")
        with col2:
            person_new = st.text_input("Nouveau nom", key="person_new")
        person = person_new.strip() if person_new.strip() else person_selected

        if not person:
            st.warning("Merci de renseigner une personne.")
            stop=1

        person_dir = AUDIO_DIR / person

        try :
            subs = [d.name for d in person_dir.iterdir() if d.is_dir()]
        except :
            pass
        if not stop:
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
                stop=1
        if not stop:
            desc = st.text_input("Nom fichier",  key="desc").strip()
            if not desc:
                st.warning("Merci de renseigner un nom")
                stop=1

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
                st.info("Installez `audio-recorder-streamlit` pour activer l'enregistrement via micro.")

if tests:
    with st.container():
        desactiver= True
        st.markdown("### Sélection du premier fichier audio")

        persons_1 = [d.name for d in AUDIO_DIR.iterdir() if d.is_dir()]
        person1 = st.selectbox("Dossier personne 1", [""] + persons_1, key="person1")

        subs_1 = []
        if person1:
            subs_1 = [d.name for d in (AUDIO_DIR / person1).iterdir() if d.is_dir()]
        sub1 = st.selectbox("Sous-dossier 1", [""] + subs_1, key="sub1")

        files_1 = []
        if person1 and sub1:
            files_1 = [f.name for f in (AUDIO_DIR / person1 / sub1).glob("*.wav")]
        file1 = st.selectbox("Fichier audio 1", [""] + files_1, key="file1")

        if file1:
            file1_path = AUDIO_DIR / person1 / sub1 / file1
            with open(file1_path, "rb") as f:
                st.audio(f.read(), format="audio/wav")


        st.markdown("### Sélection du second fichier audio")

        persons_2 = [d.name for d in AUDIO_DIR.iterdir() if d.is_dir()]
        person2 = st.selectbox("Dossier personne 2", [""] + persons_2, key="person2")

        subs_2 = []
        if person2:
            subs_2 = [d.name for d in (AUDIO_DIR / person2).iterdir() if d.is_dir()]
        sub2 = st.selectbox("Sous-dossier 2", [""] + subs_2, key="sub2")

        files_2 = []
        if person2 and sub2:
            files_2 = [f.name for f in (AUDIO_DIR / person2 / sub2).glob("*.wav")]
        file2 = st.selectbox("Fichier audio 2", [""] + files_2, key="file2")

        if file2:
            file2_path = AUDIO_DIR / person2 / sub2 / file2
            with open(file2_path, "rb") as f:
                st.audio(f.read(), format="audio/wav")
                desactiver = False

        if st.button("Lancer test audio", key="btn_test_audio", disabled=desactiver):
            placeholder = st.empty()
            with st.spinner("Exécution du test..."):
                ok = test_audio()  # <- doit renvoyer True/False
            if ok:
                placeholder.success("✅ Test réussi")
            else:
                placeholder.error("❌ Test échoué")