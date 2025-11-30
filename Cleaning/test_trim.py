from trim import trim_audio

trim_audio("../data/Phrase 1", "./trimmed_audio",silence_threshold=0.06, min_silence_duration=0.1)
