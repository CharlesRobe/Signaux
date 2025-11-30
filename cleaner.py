# Ce script va effectuer tout le nettoyage nécessaire.

dirty_audio_dirs = [
    "./data/Phrase 1",
    "./data/Phrase 2",
    "./data/Phrase 3",
    "./data/Phrase 4",
    "./data/Phrase 5",
    "./data/Phrase 6",
    "./data/Phrase 7",
    "./data/Phrase 8",
    "./data/Phrase 9",
    "./data/Phrase 10",
    "./data/Phrase 11",
    "./data/Phrase 12",
]

# 1. Filtrage des fichiers audio (fichiers résultants dans Filtered_Audio)

from Cleaning.filter import filter_noise, compare_spectrograms

filter_noise(dirty_audio_dirs, "./Cleaning/Filtered_Audio")

# 2. Vérification : Aller voir le répertoire (LONG !)

filtered_audio_dirs = [
    "./Cleaning/Filtered_Audio/Phrase 1",
    "./Cleaning/Filtered_Audio/Phrase 2",
    "./Cleaning/Filtered_Audio/Phrase 3",
    "./Cleaning/Filtered_Audio/Phrase 4",
    "./Cleaning/Filtered_Audio/Phrase 5",
    "./Cleaning/Filtered_Audio/Phrase 6",
    "./Cleaning/Filtered_Audio/Phrase 7",
    "./Cleaning/Filtered_Audio/Phrase 8",
    "./Cleaning/Filtered_Audio/Phrase 9",
    "./Cleaning/Filtered_Audio/Phrase 10",
    "./Cleaning/Filtered_Audio/Phrase 11",
    "./Cleaning/Filtered_Audio/Phrase 12",
]

gen_spectros = input("Voulez-vous générer les spectrogrammes pour comparer les fichiers audio avant et après filtrage ? Attention, ça prend longtemps ! [Y/n]")
if gen_spectros == '' or gen_spectros.lower() == 'y':
    compare_spectrograms(dirty_audio_dirs, filtered_audio_dirs, "./Cleaning/Spectrograms")

# 3. Mise au même volume (pour que le seuil fonctionne correctement)

from Cleaning.volume import check_audio_volume, normalize_audio_volume

check_audio_volume(filtered_audio_dirs)
normalize_audio_volume(filtered_audio_dirs, "./Cleaning/Normalized_Audio")
check_audio_volume(["Normalized_Audio"])

# 3. Découpe

from Cleaning.trim import trim_audio

normalized_volume_dirs = [
    "./Cleaning/Normalized_Audio/Phrase 1",
    "./Cleaning/Normalized_Audio/Phrase 2",
    "./Cleaning/Normalized_Audio/Phrase 3",
    "./Cleaning/Normalized_Audio/Phrase 4",
    "./Cleaning/Normalized_Audio/Phrase 5",
    "./Cleaning/Normalized_Audio/Phrase 6",
    "./Cleaning/Normalized_Audio/Phrase 7",
    "./Cleaning/Normalized_Audio/Phrase 8",
    "./Cleaning/Normalized_Audio/Phrase 9",
    "./Cleaning/Normalized_Audio/Phrase 10",
    "./Cleaning/Normalized_Audio/Phrase 11",
    "./Cleaning/Normalized_Audio/Phrase 12",
]

trim_audio(normalized_volume_dirs, "./Cleaned_Audio",silence_threshold=0.06, min_silence_duration=0.1)
