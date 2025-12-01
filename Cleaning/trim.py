from __future__ import annotations

import os
import numpy as np
from scipy.io import wavfile


def trim_audio(
    input_dirs: list[str],
    output_dir: str = "./Trimmed_Audio",
    silence_threshold: float = 0.01,
    min_silence_duration: float = 0.1,
    verbose: bool = False
):
    """
    Parcourt une liste de répertoires, détecte et coupe les silences au début
    et à la fin des fichiers WAV, puis sauvegarde les fichiers rognés dans
    un répertoire final avec la même structure hiérarchique.

    Parameters
    ----------
    input_dirs : list[str]
        Liste des répertoires contenant les fichiers WAV à traiter.
    output_dir : str
        Répertoire racine où seront enregistrés les fichiers rognés.
    silence_threshold : float
        Seuil d'amplitude relative sous lequel on considère du silence.
    min_silence_duration : float
        Durée minimale (en secondes) de silence pour être prise en compte.
    verbose : bool
        Affiche le détail fichier par fichier si True.
    """

    total_processed = 0

    for input_dir in input_dirs:
        if not os.path.isdir(input_dir):
            print(f"⚠ Répertoire introuvable : {input_dir}")
            continue

        print(f"➡️ Traitement de : {input_dir}")

        for root, _, files in os.walk(input_dir):
            for filename in files:
                if not filename.lower().endswith(".wav"):
                    continue

                # Chemin source
                input_path = os.path.join(root, filename)

                # Reproduction de l'arborescence dans le dossier final
                relative_path = os.path.relpath(root, input_dir)
                out_dir = os.path.join(output_dir, os.path.basename(input_dir), relative_path)
                os.makedirs(out_dir, exist_ok=True)

                output_path = os.path.join(out_dir, filename)

                if verbose:
                    print(f"   → {filename}")

                try:
                    # Lecture WAV
                    sample_rate, audio = wavfile.read(input_path)

                    # Normalisation
                    if audio.dtype.kind == "i":
                        max_val = np.iinfo(audio.dtype).max
                    else:
                        max_val = 1.0
                    audio_float = audio.astype(np.float32) / max_val

                    amplitude = np.abs(audio_float)
                    min_silence_samples = int(min_silence_duration * sample_rate)

                    mask = amplitude > silence_threshold

                    # Fichier entièrement silencieux
                    if not np.any(mask):
                        if verbose:
                            print(f"   ⚠ Silence total ignoré : {filename}")
                        continue

                    # Périmètre utile
                    start = np.argmax(mask)
                    end = len(mask) - np.argmax(mask[::-1])

                    if end <= start:
                        if verbose:
                            print(f"   ⚠ Trop silencieux : {filename}")
                        continue

                    trimmed = audio[start:end]

                    # Sauvegarde
                    wavfile.write(output_path, sample_rate, trimmed.astype(audio.dtype))
                    total_processed += 1

                except Exception as e:
                    print(f"❗ Erreur sur `{filename}` : {e}")

        print(f"✔️ Terminé pour {input_dir}\n")

    print(f"✅ Fin du trim : {total_processed} fichier(s) généré(s).")
