from pathlib import Path
import streamlit as st

# --- Config + masquage sidebar ---
st.set_page_config(page_title="Auth Demo", layout="centered", initial_sidebar_state="collapsed")
st.markdown("<style>[data-testid='stSidebar'],[data-testid='stSidebarNav']{display:none;}</style>", unsafe_allow_html=True)

st.title("🔐 Auth Demo")

# Lien clair vers la page de tests (PAS de switch_page)
st.page_link("pages/test_son.py", label="🧪 Page de tests")

# --- Etat global minimal ---
FLAG = Path("registered.flag")
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

# --- Flux simple d'inscription/connexion ---
if not FLAG.exists():
    st.subheader("Inscription")
    if st.button("S'enregistrer"):
        FLAG.touch()
        st.session_state.logged_in = False
        st.rerun()

elif not st.session_state.logged_in:
    st.subheader("Connexion")
    col1, col2 = st.columns(2)
    if col1.button("Se connecter"):
        st.session_state.logged_in = True
        st.rerun()
    if col2.button("Supprimer le compte"):
        FLAG.unlink(missing_ok=True)
        st.session_state.logged_in = False
        st.rerun()

else:
    st.subheader("Compte")
    st.success("✅ Vous êtes connecté")
    if st.button("Se déconnecter"):
        st.session_state.logged_in = False
        st.rerun()
