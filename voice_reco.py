import numpy as np
from scipy.io import wavfile
from scipy.fft import fft
import os

def soundSig(filename):
    """
    Compute and normalize the power spectrum of a WAV audio file.

    This function reads a WAV file, computes its Fast Fourier Transform (FFT),
    calculates the power spectrum, sums the power in 100-sample bins, and
    returns the normalized power distribution.

    Parameters:
        filename (str): Path to the WAV file to be processed.

    Returns:
        numpy.ndarray: A 1D array of length 50, containing the normalized power distribution of the audio signal's power spectrum.
    """
    # Read the WAV file
    sample_rate, in_data = wavfile.read(filename)

    # Ensure the input is mono (take the first channel if stereo)
    if len(in_data.shape) > 1:
        in_data = in_data[:, 0]

    # Compute the FFT
    f = fft(in_data, n=100000)

    # Compute the power spectrum
    q = f * np.conj(f)
    q = np.abs(q[:5000])

    # Sum the power spectrum in 100-sample bins
    p = np.zeros(50)
    for i in range(50):
        t = (i - 1) * 100 + 1
        p[i] = np.sum(q[t:t+100])

    # Normalize
    p = p / np.sum(p)

    return p

def comparison_tests(reference_file, targets):
    """
    Compare the similarity of a reference audio file's power spectrum with a list of target audio files.
    Prints only the file names (not full paths) in the output.
    """

    ref_file_signature = soundSig(reference_file)
    best_similarity = np.sum(ref_file_signature * ref_file_signature) # setting the best similarity value

    ref_name = os.path.basename(reference_file)

    for file in targets:
        target_signature = soundSig(file)
        similarity = np.sum(ref_file_signature * target_signature)

        target_name = os.path.basename(file)
        print(f"Similarity between {ref_name} and {target_name}: {(similarity/best_similarity)*100}%")

# File paths definitions
ju_patate = "/home/he202415/GitHub/Signaux/data/audio/Julien/Mot/ju_patate.wav"
ju_pomme = "/home/he202415/GitHub/Signaux/data/audio/Julien/Mot/ju_pomme.wav"
ju_bouteille = "/home/he202415/GitHub/Signaux/data/audio/Julien/Mot/ju_bouteille.wav"

cha_patate = "/home/he202415/GitHub/Signaux/data/audio/Charles/Mot/cha_patate.wav"
cha_pomme = "/home/he202415/GitHub/Signaux/data/audio/Charles/Mot/cha_pomme.wav"
cha_bouteille = "/home/he202415/GitHub/Signaux/data/audio/Charles/Mot/cha_bouteille.wav"

targets = [ju_patate, ju_pomme, ju_bouteille]

comparison_tests(ju_bouteille, targets)
