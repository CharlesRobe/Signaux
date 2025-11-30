from volume import check_audio_volume, normalize_audio_volume

input_dirs = ["../data/Phrase 2"]

check_audio_volume(input_dirs)
normalize_audio_volume(input_dirs)
check_audio_volume(["Normalized_Volume"])
