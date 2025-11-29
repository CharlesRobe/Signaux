import os
import itertools
import sys

try:
    from script import charger_audio, calcul_mfcc, score_biometrie, score_mot_de_passe, SEUIL_BIO, SEUIL_TXT
except ImportError:
    print("Erreur: Le fichier 'script.py' est introuvable ou contient des erreurs.")
    sys.exit(1)

DOSSIER_DATA = "data"


def pre_calculer_signatures(fichiers):
    """
    Optimisation: On calcule les MFCC une seule fois par fichier pour gagner du temps.

    """
    db = []
    print(SEUIL_BIO, SEUIL_TXT)
    print("Pré-traitement des fichiers (Extraction MFCC)...")

    for chemin in fichiers:
        y, sr = charger_audio(chemin)

        if y is not None:
            mfcc = calcul_mfcc(y, sr)

            db.append({
                "nom": os.path.basename(chemin),
                "mfcc": mfcc
            })
    return db


def lancer_analyse_totale():
    print(f"Lancement de l'analyse totale sur le dossier '{DOSSIER_DATA}'\n")

    # 1. Scan du  pour récuper les chemins des fichiers audio dans une liste
    fichiers = []
    for root, dirs, files in os.walk(DOSSIER_DATA):
        for file in files:
            if file.lower().endswith(('.wav')):
                fichiers.append(os.path.join(root, file))

    if not fichiers:
        print(f"Aucun fichier trouvé dans {DOSSIER_DATA}")
        return

    # 2. Pré-calcul des signatures MFCC pour ne pas devoir le faire a chaque comparaison
    base_donnees = pre_calculer_signatures(fichiers)
    print(f"{len(base_donnees)} signatures valides générées.\n")

    print(f"{'FICHIER A':<25} | {'FICHIER B':<25} | {'BIO':<6} | {'TXT':<6} | {'VERDICT'}")
    print("-" * 90)

    # 3. Lancement des comparaisons par paires

    nb_tests = 0
    nb_ok = 0
    nb_juste_timbre = 0
    nb_juste_phrase = 0
    nb_nok = 0

    for entree_a, entree_b in itertools.combinations(base_donnees, 2):
        mfcc_a = entree_a["mfcc"]
        mfcc_b = entree_b["mfcc"]


        dist_bio = score_biometrie(mfcc_a, mfcc_b)
        dist_txt = score_mot_de_passe(mfcc_a, mfcc_b)

        ok_bio = dist_bio < SEUIL_BIO
        ok_txt = dist_txt < SEUIL_TXT

        verdict = "❌"
        if ok_bio and ok_txt:
            verdict = "✅ MATCH"
            nb_ok += 1
        elif ok_bio:
            verdict = "⚠️ MEME PERS / MAUVAIS MOT"
            nb_juste_timbre += 1
        elif ok_txt:
            verdict = "⚠️ BON MOT / MAUVAISE PERS"
            nb_juste_phrase += 1
        else:
            nb_nok += 1

        print(f"{entree_a['nom'][:24]:<25} | {entree_b['nom'][:24]:<25} | {dist_bio:.2f}   | {dist_txt:.2f}   | {verdict}")

        nb_tests += 1

    print("-" * 90)
    print(f"Test terminé : {nb_tests} comparaisons réalisées. Avec \n Match : {nb_ok} \n Juste voix : {nb_juste_timbre} \n  Juste phrase : {nb_juste_phrase} \n Rien en commun {nb_nok}")
    print(f"Avec comme seuils : SEUIL_BIO={SEUIL_BIO} et SEUIL_TXT={SEUIL_TXT}")
if __name__ == "__main__":
    lancer_analyse_totale()
