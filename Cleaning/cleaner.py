# Ce script va effectuer tout le nettoyage nécessaire.

import filter

dirty_audio_dirs = [
    "../data/Phrase 1",
    "../data/Phrase 2",
    "../data/Phrase 3",
    "../data/Phrase 4",
    "../data/Phrase 5",
    "../data/Phrase 6",
    "../data/Phrase 7",
    "../data/Phrase 8",
    "../data/Phrase 9",
    "../data/Phrase 10",
    "../data/Phrase 11",
    "../data/Phrase 12",
]

# 1. Filtrage des fichiers audio (fichiers résultants dans Filtered_Audio)

filter.filter_noise(dirty_audio_dirs)

# 2. Vérification : Aller voir le répertoire (LONG !)

filtered_audio_dirs = [
    "./Filtered_Audio/Phrase 1",
    "./Filtered_Audio/Phrase 2",
    "./Filtered_Audio/Phrase 3",
    "./Filtered_Audio/Phrase 4",
    "./Filtered_Audio/Phrase 5",
    "./Filtered_Audio/Phrase 6",
    "./Filtered_Audio/Phrase 7",
    "./Filtered_Audio/Phrase 8",
    "./Filtered_Audio/Phrase 9",
    "./Filtered_Audio/Phrase 10",
    "./Filtered_Audio/Phrase 11",
    "./Filtered_Audio/Phrase 12",
]

filter.compare_spectrograms(dirty_audio_dirs, filtered_audio_dirs)

# 3. Mise au même volume (pour que le seuil fonctionne correctement)

import volume

volume.check_audio_volume(filtered_audio_dirs)
volume.normalize_audio_volume(filtered_audio_dirs)
volume.check_audio_volume(["Normalized_Audio"])

# 3. Découpe

import trim

normalized_volume_dirs = [
    "./Normalized_Audio/Phrase 1",
    "./Normalized_Audio/Phrase 2",
    "./Normalized_Audio/Phrase 3",
    "./Normalized_Audio/Phrase 4",
    "./Normalized_Audio/Phrase 5",
    "./Normalized_Audio/Phrase 6",
    "./Normalized_Audio/Phrase 7",
    "./Normalized_Audio/Phrase 8",
    "./Normalized_Audio/Phrase 9",
    "./Normalized_Audio/Phrase 10",
    "./Normalized_Audio/Phrase 11",
    "./Normalized_Audio/Phrase 12",
]

trim.trim_audio(normalized_volume_dirs, "./trimmed_audio",silence_threshold=0.06, min_silence_duration=0.1)
