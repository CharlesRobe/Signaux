from filter import filter_noise, compare_spectrograms

dirty_audio_files = [
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

filtered_audio_files = [
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

filter_noise(dirty_audio_files)
#compare_spectrograms(dirty_audio_files, filtered_audio_files) # Attention c'est long