import scipy
import soundfile as sf
import numpy as np


class Audio:
    """
    Audio object.
    """

    def __init__(
        self,
        audioFilePath: str = None,
    ) -> None:
        # Basic audio info
        # Audio length in seconds
        self.audioLength: float = 0

        # Original audio array
        self.audioArray: np.ndarray = None
        self.sampleRate: int = None

        # FFT array
        self.fftFreqSample: np.ndarray = None
        self.fftTimeSpan: np.ndarray = 0
        self.fftSpectrum: np.ndarray = None

        # Load the audio if audio file path is provided
        if audioFilePath is not None:
            self.LoadAudio(audioFilePath)

    def LoadAudio(self, audioFilePath: str):
        """
        Method to load a audio file.
        """
        # Load audio file
        self.audioArray, self.sampleRate = sf.read(audioFilePath)
        # get the length of the audio file
        self.audioLength = len(self.audioArray) / self.sampleRate

        # Generate FFT Spectrum
        self.fftFreqSample, self.fftTimeSpan, self.fftSpectrum = scipy.signal.spectrogram(
            self.audioArray, self.sampleRate)
