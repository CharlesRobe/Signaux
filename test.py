import os
import itertools
import sys
import numpy as np
import script


try:
    from script import charger_audio, calcul_mfcc, score_biometrie, score_mot_de_passe, SEUIL_BIO, SEUIL_TXT
except ImportError:
    print("Erreur: Le fichier 'script.py' est introuvable ou contient des erreurs.")
    sys.exit(1)

FICHIER_SORTIE = "resultats.txt"

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

    for chemin in fichiers:
        y, sr = charger_audio(chemin)

        if y is not None:
            mfcc = calcul_mfcc(y, sr)

            db.append({
                "nom": os.path.basename(chemin),
                "mfcc": mfcc
            })
    return db


def lancer_analyse_totale(DOSSIER_DATA):

    afficher_logs = "-all" in sys.argv

    with open(FICHIER_SORTIE, 'w', encoding='utf-8') as fichier_logs:
        msg = f"Lancement de l'analyse totale sur le dossier '{DOSSIER_DATA}'\n\n"
        print(msg, end='')
        fichier_logs.write(msg)

        # Scan du  pour récuper les chemins des fichiers audio dans une liste
        fichiers = []
        for root, dirs, files in os.walk(DOSSIER_DATA):
            for file in files:
                if file.lower().endswith(('.wav')):
                    fichiers.append(os.path.join(root, file))

        if not fichiers:
            print(f"Aucun fichier trouvé dans {DOSSIER_DATA}")
            return

        # Pré-calcul des signatures MFCC pour ne pas devoir le faire a chaque comparaison
        base_donnees = pre_calculer_signatures(fichiers)
        print(f"{len(base_donnees)} fichiers trouvées\n")
        if afficher_logs:
            print(f"{'FICHIER A':<25} | {'FICHIER B':<25} | {'BIO':<6} | {'TXT':<6} | {'VERDICT'}")
            print("-" * 90)

        # Lancement des comparaisons par paires

        nb_tests = 0
        nb_ok = 0
        nb_juste_timbre = 0
        nb_juste_phrase = 0
        nb_nok = 0
        verif_timbre = [0, 0, 0, 0]
        verif_phrase = [0, 0, 0, 0] # Pour statistiques c'est [phrase ok quand phrase ok , phrase pas ok quand phrase ok, phrase pas ok quand phrase ok, phrase pas ok quand phrase pas ok]
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

            ligne = f"{entree_a['nom'][:24]:<25} | {entree_b['nom'][:24]:<25} | {dist_bio:.2f}   | {dist_txt:.2f}   | {affichage_verdict}\n"
            if afficher_logs:
                print(ligne, end='')
            fichier_logs.write(ligne)
            nb_tests += 1
        rapport = f"{'='*60}"
        rapport += f"Test terminé : {nb_tests} comparaisons réalisées. Avec\n"
        rapport += f" Match : {nb_ok}\n Juste voix : {nb_juste_timbre}\n Juste phrase : {nb_juste_phrase}\n Rien en commun {nb_nok}\n"
        rapport += f"Avec comme seuils : SEUIL_BIO={SEUIL_BIO} et SEUIL_TXT={SEUIL_TXT}\n"
        rapport += f"\n{'='*60}\n"
        rapport += f"RAPPORT DE STATISTIQUES ({nb_tests} comparaisons)\n"
        rapport += f"{'='*60}\n"
        rapport += f"\n Timbre  | Seuil: {SEUIL_BIO}\n"
        rapport += f"   --------------------------------------------------\n"
        rapport += f"   Vrais Positifs         : {verif_timbre[0]:<5}\n"
        rapport += f"   Faux Négatifs     : {verif_timbre[1]:<5}\n"
        rapport += f"   Faux Positifs       : {verif_timbre[2]:<5}\n"
        rapport += f"   Vrais Négatifs         : {verif_timbre[3]:<5}\n"
        rapport += f"\nPHRASE       | Seuil: {SEUIL_TXT}\n"
        rapport += f"   --------------------------------------------------\n"
        rapport += f"   Vrais Positifs   : {verif_phrase[0]:<5}\n"
        rapport += f"   Faux Négatifs     : {verif_phrase[1]:<5}\n"
        rapport += f"   Faux Positifs  : {verif_phrase[2]:<5}\n"
        rapport += f"   Vrais Négatifs    : {verif_phrase[3]:<5}\n"
        rapport += f"\n{'='*60}\n"

        print(rapport)
        fichier_logs.write(rapport)


def optimiser_seuils(DOSSIER_DATA, fichier_resultats="optimisation_seuils.txt"):
    """
    Teste une large plage de seuils et trouve les meilleurs F1-scores.
    Enregistre tous les résultats dans un fichier.
    """

    resultats_bio = []  # Liste de (seuil_bio, seuil_txt, f1, precision, recall)
    resultats_txt = []  # Liste de (seuil_bio, seuil_txt, f1, precision, recall)

    valeur_bio = list(range(20, 140, 1))
    valeur_txt = list(range(100, 6000, 50))
    if len(valeur_bio) > len(valeur_txt):
        valeur_txt = valeur_txt + [valeur_txt[-1]] * (len(valeur_bio) - len(valeur_txt))
    else:
        valeur_bio = valeur_bio + [valeur_bio[-1]] * (len(valeur_txt) - len(valeur_bio))

    total_tests = len(valeur_bio)
    compteur = 0

    # Charger et pré-calculer
    fichiers = []
    for root, dirs, files in os.walk(DOSSIER_DATA):
        for file in files:
            if file.lower().endswith('.wav'):
                fichiers.append(os.path.join(root, file))

    if not fichiers:
        print(f"Aucun fichier trouvé dans {DOSSIER_DATA}")
        return []

    base_donnees = pre_calculer_signatures(fichiers)
    distances = []  # Liste de (dist_bio, dist_txt, p1, p2, ph1, ph2)

    for entree_a, entree_b in itertools.combinations(base_donnees, 2):
        p1, ph1 = parser_nom(entree_a["nom"])
        p2, ph2 = parser_nom(entree_b["nom"])

        mfcc_a = entree_a["mfcc"]
        mfcc_b = entree_b["mfcc"]

        dist_bio = score_biometrie(mfcc_a, mfcc_b)
        dist_txt = score_mot_de_passe(mfcc_a, mfcc_b)
        distances.append((dist_bio, dist_txt, p1, p2, ph1, ph2))

    print(f"Lancement de l'optimisation : {total_tests} combinaisons à tester")
    print(f"Résultats sauvegardés dans '{fichier_resultats}'")
    print("=" * 70)

    with open(fichier_resultats, 'w', encoding='utf-8') as f:
        for seuil_bio, seuil_txt in zip(valeur_bio, valeur_txt):
            compteur += 1

            # Modifier les seuils dans script.py
            script.SEUIL_BIO = seuil_bio
            script.SEUIL_TXT = seuil_txt

            # Lancer les comparaisons
            nb_ok = 0
            nb_juste_timbre = 0
            nb_juste_phrase = 0
            verif_timbre = [0, 0, 0, 0]
            verif_phrase = [0, 0, 0, 0]

            for dist_bio, dist_txt, p1, p2, ph1, ph2 in distances:
                ok_bio = dist_bio < seuil_bio
                ok_txt = dist_txt < seuil_txt

                if ok_bio and ok_txt:
                    nb_ok += 1
                elif ok_bio:
                    nb_juste_timbre += 1
                elif ok_txt:
                    nb_juste_phrase += 1

                # Stats timbre
                if p1 == p2:
                    if ok_bio:
                        verif_timbre[0] += 1
                    else:
                        verif_timbre[1] += 1
                else:
                    if ok_bio:
                        verif_timbre[2] += 1
                    else:
                        verif_timbre[3] += 1

                # Stats phrase
                if ph1 == ph2:
                    if ok_txt:
                        verif_phrase[0] += 1
                    else:
                        verif_phrase[1] += 1
                else:
                    if ok_txt:
                        verif_phrase[2] += 1
                    else:
                        verif_phrase[3] += 1

            taux_vp_bio = verif_timbre[0] / (verif_timbre[0] + verif_timbre[1])
            taux_vn_bio = verif_timbre[3] / (verif_timbre[2] + verif_timbre[3])

            taux_vp_txt = verif_phrase[0] / (verif_phrase[0] + verif_phrase[1])
            taux_vn_txt = verif_phrase[3] / (verif_phrase[2] + verif_phrase[3])

            # Enregistrer
            resultats_bio.append((seuil_bio, taux_vp_bio, taux_vn_bio, verif_timbre.copy()))
            resultats_txt.append((seuil_txt, taux_vp_txt, taux_vn_txt, verif_phrase.copy()))

            # Écrire dans le fichier
            ligne = f"BIO={seuil_bio} | TXT={seuil_txt} | "
            ligne += f"timbre=[VP:{verif_timbre[0]} FN:{verif_timbre[1]} FP:{verif_timbre[2]} VN:{verif_timbre[3]}] | "
            ligne += f"phrase=[VP:{verif_phrase[0]} FN:{verif_phrase[1]} FP:{verif_phrase[2]} VN:{verif_phrase[3]}]\n"
            f.write(ligne)

            # Affichage progression
            print(f"Progression: {compteur}/{total_tests} ({100*compteur/total_tests:.1f}%)")

    # ========== TABLEAU COMPLET TIMBRE ==========
        f.write("\n\n" + "="*100 + "\n")
        f.write("TOUS LES RÉSULTATS TIMBRE (BIOMÉTRIE)\n")
        f.write("="*100 + "\n")
        f.write(f"{'SEUIL':<10} | {'VP%':<10} | {'VN%':<10} | {'VP':<8} | {'FN':<8} | {'FP':<8} | {'VN':<8}\n")
        f.write("-"*100 + "\n")
        
        for seuil, taux_vp, taux_vn, stats in resultats_bio:
            ligne = f"{seuil:<10} | {taux_vp*100:<10.2f} | {taux_vn*100:<10.2f} | "
            ligne += f"{stats[0]:<8} | {stats[1]:<8} | {stats[2]:<8} | {stats[3]:<8}\n"
            f.write(ligne)
        
        # ========== TABLEAU COMPLET PHRASE ==========
        f.write("\n\n" + "="*100 + "\n")
        f.write("TOUS LES RÉSULTATS PHRASE (TEXTE)\n")
        f.write("="*100 + "\n")
        f.write(f"{'SEUIL':<10} | {'VP%':<10} | {'VN%':<10} | {'VP':<8} | {'FN':<8} | {'FP':<8} | {'VN':<8}\n")
        f.write("-"*100 + "\n")
        
        for seuil, taux_vp, taux_vn, stats in resultats_txt:
            ligne = f"{seuil:<10} | {taux_vp*100:<10.2f} | {taux_vn*100:<10.2f} | "
            ligne += f"{stats[0]:<8} | {stats[1]:<8} | {stats[2]:<8} | {stats[3]:<8}\n"
            f.write(ligne)
    
    # Affichage console simplifié
    print("\n" + "=" * 70)
    print("OPTIMISATION TERMINÉE")
    print("=" * 70)
    print(f"TIMBRE : {len(resultats_bio)} seuils testés (de {valeur_bio[0]} à {valeur_bio[-1]})")
    print(f"PHRASE : {len(resultats_txt)} seuils testés (de {valeur_txt[0]} à {valeur_txt[-1]})")
    print(f"\nConsulter '{fichier_resultats}' pour voir tous les VP% et VN%")
    

if __name__ == "__main__":
    if len(sys.argv) > 1 and not sys.argv[1].startswith('-'):
        DOSSIER_DATA = sys.argv[1]
    else:
        DOSSIER_DATA = "data"

    if "--optimize" in sys.argv:
        optimiser_seuils(DOSSIER_DATA)
    else:
        lancer_analyse_totale(DOSSIER_DATA)