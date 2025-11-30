import os
import librosa
import soundfile as sf
import numpy as np

def normalize_audio_volume(
    input_dirs: list[str],
    output_dir: str = "./Normalized_Volume",
    target_db: float = -20.0
):
    """
    Normalise tous les fichiers WAV présents dans plusieurs répertoires,
    en préservant leur structure interne, puis les stocke dans output_dir.

    Exemple d'utilisation :
    input_folders = [
        "Dataset/Phrase1",
        "Dataset/Phrase2",
        "Dataset/Phrase3"
    ]

    normalize_multiple_folders(
        input_dirs=input_folders,
        output_dir="Clean",
        target_db=-20.0
    )
    """

    for input_dir in input_dirs:
        if not os.path.isdir(input_dir):
            print(f"❗ Répertoire introuvable : {input_dir}")
            continue

        print(f"⏳ Traitement du dossier {input_dir} en cours…")

        for root, _, files in os.walk(input_dir):
            for filename in files:
                if not filename.lower().endswith(".wav"):
                    continue
                
                print(f"⏳ Traitement du fichier {filename} en cours…")

                input_path = os.path.join(root, filename)

                # Conserver toute la hiérarchie
                relative_path = os.path.relpath(root, input_dir)
                out_dir = os.path.join(output_dir, os.path.basename(input_dir), relative_path)
                os.makedirs(out_dir, exist_ok=True)

                output_path = os.path.join(out_dir, filename)

                # Charger l'audio
                audio, sr = librosa.load(input_path, sr=None)

                # RMS → dBFS
                rms = np.sqrt(np.mean(audio**2))
                current_db = 20 * np.log10(rms + 1e-12)

                # Gain
                gain_db = target_db - current_db
                gain = 10 ** (gain_db / 20)

                # Application du gain
                normalized_audio = audio * gain

                # Écriture
                sf.write(output_path, normalized_audio, sr)

                print(f"✔️ Traitement du fichier {filename} terminé.")

                print(f"Normalisé : {input_path} → {output_path}")

        print(f"✔️ Traitement du dossier {input_dir} terminé.")

    print("✅ Traitement terminé.")



def check_audio_volume(directories):
    """
    Analyse tous les fichiers WAV dans la liste de répertoires fournie.
    Calcule leur RMS et leur niveau en dBFS pour vérifier l'uniformité du volume.

    Exemple d'utilisation :
    check_audio_volume(["Clean/Phrase1", "Clean/Phrase2"])
    """

    results = []  # (chemin, rms, dbfs)

    for directory in directories:
        if not os.path.isdir(directory):
            print(f"❗ Répertoire introuvable : {directory}")
            continue

        print(f"⏳ Analyse des fichiers du répertoire {directory} en cours…")

        for root, _, files in os.walk(directory):
            for f in files:
                print(f"⏳ Analyse du fichier {f} en cours…")
                if not f.lower().endswith(".wav"):
                    continue

                path = os.path.join(root, f)

                audio, sr = librosa.load(path, sr=None)
                rms = np.sqrt(np.mean(audio**2))
                dbfs = 20 * np.log10(rms + 1e-12)

                results.append((path, rms, dbfs))
                print(f"✔️ Analyse du fichier {f} terminée.")
        
        print(f"✔️ Analyse des fichiers du répertoire {directory} terminée.")

    if not results:
        print("❗ Aucun fichier WAV trouvé.")
        return

    # Niveau moyen
    db_mean = np.mean([r[2] for r in results])

    print("\n--- Vérification du volume ---\n")
    print(f"Niveau moyen constaté : {db_mean:.2f} dBFS\n")

    for path, rms, dbfs in results:
        diff = dbfs - db_mean
        print(f"{path}")
        print(f"    RMS     : {rms:.6f}")
        print(f"    Niveau  : {dbfs:.2f} dBFS (écart {diff:+.2f} dB)")
        print()

    # Conclusion pratique
    max_deviation = max(abs(r[2] - db_mean) for r in results)

    print(f"Écart maximal observé : {max_deviation:.2f} dB")

    if max_deviation < 0.5:
        print("✅ Tous les fichiers ont un volume uniformisé (écart très faible).")
    elif max_deviation < 1.5:
        print("⚠️ Les fichiers sont globalement uniformes, mais il existe quelques écarts légers.")
    else:
        print("❌ Les volumes ne sont pas uniformes : l'écart est notable.")
