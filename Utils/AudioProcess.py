from time import sleep
import scipy
import soundfile as sf
import numpy as np
import sounddevice as sd


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
        self.cursorPosition: float = 0

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

class AudioPlayer:
    """
    Audio player class
    """
    def __init__(
        self,
        audio: Audio,
        responseRate: float,
        callback: callable,
    ) -> None:
        self.audio: Audio = audio
        self.responseRate: float = responseRate
        
        # Play control
        self.timeCallback: callable = callback
        
    def Play(self) -> None:
        """
        Play the audio
        """
        sd.RawOutputStream(
            samplerate=self.audio.sampleRate,
            callback=self.StreamCallback,
        )
        
    
    def Pause(self) -> None:
        sd.stop
    
    def StreamCallback(self, outdata, frames, time, status):
        """
        Stream callback function
        """
        # Update the time
        # self.timeCallback(time)
        print(time, status)
        # Write data to audio stream
        startFrame = int(time * self.audio.sampleRate)
        outdata[:] = self.audio.audioArray[startFrame : startFrame + frames]