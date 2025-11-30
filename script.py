import librosa
import numpy as np
from scipy.spatial.distance import euclidean
from librosa.sequence import dtw
import os
import sys

SEUIL_BIO = 28.0   # En dessous = meme personne
SEUIL_TXT = 7 # En dessous = meme phrase


def charger_audio(chemin):
    # Nettoyage du chemin pour compatibilité terminal
    chemin = chemin.strip().strip('"').strip("'")

    if not os.path.exists(chemin):
        print(f"Erreur: fichier introuvable {chemin}")
        return None, None

    try:
        # Chargement à 4kHz (standard voix) mais *2 pour le frequence d'échantillonnage
        y, sr = librosa.load(chemin, sr=8000)
        # Suppression des silences début/fin pour optimiser la comparaison
        y, _ = librosa.effects.trim(y, top_db=20)
        return y, sr
    except Exception as e:
        print(f"Erreur lecture: {e}")
        return None, None


def calcul_mfcc(y, sr):
    # Extraction des caractéristiques fréquentielles (13 coefficients)
    # Hop_length definit la resolution temporelle
    return librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13, hop_length=512)


def score_biometrie(mfcc1, mfcc2):
    """
    Compare le timbre de voix.
    Methode: Distance euclidienne sur les moyennes temporelles.
    """
    # Moyenne sur l'axe du temps (réduction vecteur)
    vec1 = np.mean(mfcc1, axis=1)
    vec2 = np.mean(mfcc2, axis=1)

    return euclidean(vec1, vec2)


def score_mot_de_passe(mfcc1, mfcc2):
    """
    Compare le contenu prononcé.
    Methode: DTW (Dynamic Time Warping) pour aligner les sequences.
    """
    # Calcul de la matrice de cout (metric cosine souvent plus robuste pour spectres)
    D, wp = dtw(mfcc1, mfcc2, subseq=True)

    # Cout normalise par la longueur du chemin
    return D[-1, -1] / len(wp)


def main(f_ref, f_test):
    global SEUIL_BIO, SEUIL_TXT
    print("-" * 30)
    print("Traitement en cours...")

    # 1. Chargement
    y_ref, sr_ref = charger_audio(f_ref)
    y_test, sr_test = charger_audio(f_test)

    if y_ref is None or y_test is None:
        return

    # 2. Extraction MFCC
    mfcc_ref = calcul_mfcc(y_ref, sr_ref)
    mfcc_test = calcul_mfcc(y_test, sr_test)

    # 3. Calcul des distances
    dist_bio = score_biometrie(mfcc_ref, mfcc_test)
    dist_txt = score_mot_de_passe(mfcc_ref, mfcc_test)

 

    # 5. Affichage resultats
    print("-" * 30)
    print(f"Distance Timbre (Bio) : {dist_bio:.2f}  (Seuil: {SEUIL_BIO})")
    print(f"Distance Phrase (DTW) : {dist_txt:.3f}  (Seuil: {SEUIL_TXT})")
    print("-" * 30)

    auth_bio = dist_bio < SEUIL_BIO
    auth_txt = dist_txt < SEUIL_TXT

    if auth_bio and auth_txt:
        print("RESULTAT : ACCES AUTORISE")
    else:
        print("RESULTAT : ACCES REFUSE")
        if not auth_bio: print(" -> Identite non reconnue")
        if not auth_txt: print(" -> Phrase incorrecte")


if __name__ == "__main__":
    # Gestion arguments ligne de commande ou interactif
    if len(sys.argv) == 3:
        main(sys.argv[1], sys.argv[2])
    else:
        print("Usage: python app.py <fichier_test1.wav> <fichier_test2.wav>")
