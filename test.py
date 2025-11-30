import os
import itertools
import sys

try:
    from script import charger_audio, calcul_mfcc, score_biometrie, score_mot_de_passe, SEUIL_BIO, SEUIL_TXT
except ImportError:
    print("Erreur: Le fichier 'script.py' est introuvable ou contient des erreurs.")
    sys.exit(1)

DOSSIER_DATA = "data"


def parser_nom(nom_fichier):
    """
    Analyse le nom: 'Al_ph_8a.wav' -> Personne='Al', Phrase='8'
    """
    try:
        # On enlève l'extension .wav
        clean_name = nom_fichier.replace('.wav', '')
        parts = clean_name.split('_')

        # parts[0] = "Al" (Personne)
        personne = parts[0]

        # parts[2] = "8a" -> On garde tout sauf la dernière lettre (le 'a')
        phrase_brute = parts[2]
        phrase_id = phrase_brute[:-1]

        return personne, phrase_id
    except:
        return "Inconnu", "Inconnu"


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
    verif_timbre = [0,0,0,0]
    verif_phrase = [0,0,0,0] # Pour statistiques c'est [phrase ok quand phrase ok , phrase pas ok quand phrase ok, phrase pas ok quand phrase ok, phrase pas ok quand phrase pas ok]
    for entree_a, entree_b in itertools.combinations(base_donnees, 2):

        p1, ph1 = parser_nom(entree_a["nom"])
        p2, ph2 = parser_nom(entree_b["nom"])

        resultat_attendu = "REJET"  # Par défaut
        if p1 == p2 and ph1 == ph2:
            resultat_attendu = "MATCH"
        elif p1 == p2:
            resultat_attendu = "VOIX_SEULE"
        elif ph1 == ph2:
            resultat_attendu = "MOT_SEUL"

        mfcc_a = entree_a["mfcc"]
        mfcc_b = entree_b["mfcc"]
        dist_bio = score_biometrie(mfcc_a, mfcc_b)
        dist_txt = score_mot_de_passe(mfcc_a, mfcc_b)

        ok_bio = dist_bio < SEUIL_BIO
        ok_txt = dist_txt < SEUIL_TXT

        verdict = "REJET"

        if ok_bio and ok_txt:
            verdict = "MATCH"
            nb_ok += 1
        elif ok_bio:
            verdict = "VOIX_SEULE"
            nb_juste_timbre += 1
        elif ok_txt:
            verdict = "MOT_SEUL"
            nb_juste_phrase += 1
        else:
            nb_nok += 1

        if p1 == p2:  # Si c'est la meme personne
            if ok_bio:
                verif_timbre[0] += 1
            else:
                verif_timbre[1] += 1
        else:
            if ok_bio:
                verif_timbre[2] += 1
            else:
                verif_timbre[3] += 1
        
        if ph1 == ph2:  # Si c'est la meme phrase
            if ok_txt:
                verif_phrase[0] += 1
            else:
                verif_phrase[1] += 1
        else:
            if ok_txt:
                verif_phrase[2] += 1
            else:
                verif_phrase[3] += 1

        correct = (verdict == resultat_attendu)
        if correct:
            affichage_verdict = "✅ OK"
        else:
            affichage_verdict = "❌ ERREUR "+ verdict +" (attendu: " + resultat_attendu + ")"

        if not correct or resultat_attendu == "MATCH":
            print(f"{entree_a['nom'][:24]:<25} | {entree_b['nom'][:24]:<25} | {dist_bio:.2f}   | {dist_txt:.2f}   | {affichage_verdict}")

        nb_tests += 1

    print("-" * 90)
    print(f"Test terminé : {nb_tests} comparaisons réalisées. Avec \n Match : {nb_ok} \n Juste voix : {nb_juste_timbre} \n  Juste phrase : {nb_juste_phrase} \n Rien en commun {nb_nok}")
    print(f"Avec comme seuils : SEUIL_BIO={SEUIL_BIO} et SEUIL_TXT={SEUIL_TXT}")
    print("\n" + "="*60)
    print(f"RAPPORT DE STATISTIQUES ({nb_tests} comparaisons)")
    print("="*60)

    # BLOC 1 : TIMBRE (Identité)
    print(f"\n Timbre  | Seuil: {SEUIL_BIO}")
    print(f"   --------------------------------------------------")
    print(f"   Vrais Positifs         : {verif_timbre[0]:<5} ")
    print(f"   Faux Négatifs     : {verif_timbre[1]:<5} ")
    print(f"   Faux Positifs       : {verif_timbre[2]:<5} ")
    print(f"   Vrais Négatifs         : {verif_timbre[3]:<5} ")

    # BLOC 2 : PHRASE (Contenu)
    print(f"\nPHRASE       | Seuil: {SEUIL_TXT}")
    print(f"   --------------------------------------------------")
    print(f"   Vrais Positifs   : {verif_phrase[0]:<5}")
    print(f"   Faux Négatifs     : {verif_phrase[1]:<5}")
    print(f"   Faux Positifs  : {verif_phrase[2]:<5}")
    print(f"   Vrais Négatifs    : {verif_phrase[3]:<5}")
    print("\n" + "="*60)

if __name__ == "__main__":
    lancer_analyse_totale()
