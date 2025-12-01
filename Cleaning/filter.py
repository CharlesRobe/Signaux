from __future__ import annotations

import os
from scipy.io import wavfile
import noisereduce as nr
import soundfile as sf
import librosa
import librosa.display
import matplotlib.pyplot as plt
import numpy as np

def filter_noise(
    input_dirs: list[str],
    output_dir: str = "./Filtered_Audio",
) -> None:
    """
    Applique une réduction de bruit aux fichiers audio WAV dans un ou plusieurs répertoires d'entrée.
    Les fichiers traités sont sauvegardés dans une structure de répertoires identique sous le répertoire de sortie spécifié.

    Args:
        input_dirs (list[str]):
            Liste des chemins des répertoires contenant les fichiers audio WAV à filtrer.
            Chaque répertoire est traité récursivement.
        output_dir (str, optional):
            Chemin du répertoire de destination où les fichiers filtrés seront enregistrés.
            Par défaut, "./Filtered_Audio".

    Raises:
        FileNotFoundError:
            Si un répertoire d'entrée n'existe pas (un message est affiché, mais le traitement continue).
        Exception:
            Toute erreur liée à la lecture/écriture des fichiers audio ou à la création des répertoires
            sera propagée (ex: permissions insuffisantes, format audio invalide).

    Notes:
        - Seuls les fichiers avec l'extension `.wav` (insensible à la casse) sont traités.
        - Utilise la bibliothèque `noisereduce` pour la réduction de bruit.
        - Utilise `soundfile` pour l'écriture des fichiers audio.
        - La structure des sous-répertoires des répertoires d'entrée est reproduite dans le répertoire de sortie.

    Example:
        >>> filter_noise(
        ...     input_dirs=["~/musique/album1", "~/musique/album2"],
        ...     output_dir="./musique_filtre"
        ... )
        ⏳ Traitement du dossier ~/musique/album1 en cours…
        ⏳ Filtrage du fichier piste1.wav en cours…
        ✔️ Filtrage du fichier piste1.wav terminé.
        ✔️ Traitement du dossier ~/musique/album1 terminé.
        ✅ Traitement terminé.
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

                print(f"⏳ Filtrage du fichier {filename} en cours…")
                input_path = os.path.join(root, filename)
                # Conserver toute la hiérarchie
                relative_path = os.path.relpath(root, input_dir)
                out_dir = os.path.join(output_dir, os.path.basename(input_dir), relative_path)
                os.makedirs(out_dir, exist_ok=True)
                output_path = os.path.join(out_dir, filename)
                # Load data
                rate, data = wavfile.read(input_path)  # Correction : utiliser input_path au lieu d'un chemin codé en dur
                # Perform noise reduction
                reduced_noise = nr.reduce_noise(y=data, sr=rate)
                # Écriture
                sf.write(output_path, reduced_noise, rate)  # Correction : utiliser reduced_noise et rate
                print(f"✔️ Filtrage du fichier {filename} terminé.")
        print(f"✔️ Traitement du dossier {input_dir} terminé.")

    print("✅ Traitement terminé.")


import os
import librosa
import librosa.display
import matplotlib.pyplot as plt
import numpy as np

def compare_spectrograms(
    dirty_dirs: list[str],
    clean_dirs: list[str],
    output_dir: str = "./Spectrogram_Comparisons",
) -> None:
    """
    Compare les spectrogrammes de deux ensembles de fichiers audio WAV (sales et propres),
    puis sauvegarde les spectrogrammes dans un répertoire de sortie.

    Args:
        dirty_dirs (list[str]):
            Liste des chemins des répertoires contenant les fichiers audio WAV sales (non filtrés).
        clean_dirs (list[str]):
            Liste des chemins des répertoires contenant les fichiers audio WAV propres (filtrés).
        output_dir (str, optional):
            Chemin du répertoire de destination où les spectrogrammes seront sauvegardés.
            Par défaut, "./Spectrogram_Comparisons".

    Raises:
        FileNotFoundError:
            Si un répertoire d'entrée n'existe pas (un message est affiché, mais le traitement continue).
        Exception:
            Toute erreur liée à la lecture des fichiers audio ou à la création des répertoires
            sera propagée (ex: permissions insuffisantes, format audio invalide).

    Notes:
        - Seuls les fichiers avec l'extension `.wav` (insensible à la casse) sont traités.
        - Les répertoires `dirty_dirs` et `clean_dirs` doivent avoir la même structure et les mêmes noms de fichiers.
        - Les spectrogrammes sont sauvegardés au format PNG.
        - Utilise `librosa` pour le calcul des spectrogrammes et `matplotlib` pour l'affichage.
    """
    # Créer le répertoire de sortie s'il n'existe pas
    os.makedirs(output_dir, exist_ok=True)

    # Parcourir les répertoires de fichiers sales et propres
    for dirty_dir, clean_dir in zip(dirty_dirs, clean_dirs):
        if not os.path.isdir(dirty_dir) or not os.path.isdir(clean_dir):
            print(f"❗ Répertoire introuvable : {dirty_dir} ou {clean_dir}")
            continue

        print(f"⏳ Traitement des dossiers {dirty_dir} et {clean_dir} en cours…")

        # Parcourir les fichiers dans les répertoires sales
        for root_dirty, _, files_dirty in os.walk(dirty_dir):
            for filename in files_dirty:
                if not filename.lower().endswith(".wav"):
                    continue

                # Construire les chemins des fichiers sales et propres
                relative_path = os.path.relpath(root_dirty, dirty_dir)
                clean_root = os.path.join(clean_dir, relative_path)
                dirty_path = os.path.join(root_dirty, filename)
                clean_path = os.path.join(clean_root, filename)

                if not os.path.exists(clean_path):
                    print(f"❗ Fichier propre non trouvé : {clean_path}")
                    continue

                print(f"⏳ Comparaison des spectrogrammes pour {filename} en cours…")

                # Charger les fichiers audio
                y_dirty, sr = librosa.load(dirty_path, sr=None)
                y_clean, _ = librosa.load(clean_path, sr=sr)

                # Calculer les spectrogrammes
                D_dirty = librosa.amplitude_to_db(np.abs(librosa.stft(y_dirty)), ref=np.max)
                D_clean = librosa.amplitude_to_db(np.abs(librosa.stft(y_clean)), ref=np.max)

                # Sauvegarder les spectrogrammes
                fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

                # Spectrogramme du fichier sale
                img1 = librosa.display.specshow(D_dirty, y_axis='log', x_axis='time', sr=sr, ax=ax1)
                ax1.set_title(f"Spectrogramme sale : {filename}")
                fig.colorbar(img1, ax=ax1, format='%+2.0f dB')

                # Spectrogramme du fichier propre
                img2 = librosa.display.specshow(D_clean, y_axis='log', x_axis='time', sr=sr, ax=ax2)
                ax2.set_title(f"Spectrogramme propre : {filename}")
                fig.colorbar(img2, ax=ax2, format='%+2.0f dB')

                # Sauvegarder la figure
                output_filename = f"comparaison_{os.path.splitext(filename)[0]}.png"
                output_path = os.path.join(output_dir, output_filename)
                plt.savefig(output_path, dpi=300, bbox_inches='tight')
                plt.close(fig)

                print(f"✔️ Spectrogrammes pour {filename} sauvegardés : {output_path}")

        print(f"✔️ Traitement des dossiers {dirty_dir} et {clean_dir} terminé.")

    print("✅ Comparaison des spectrogrammes terminée.")