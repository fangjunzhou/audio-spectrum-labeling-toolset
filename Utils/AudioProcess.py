import queue
from re import S
import threading
import time
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
        
        self.audioBuffer: queue.Queue = queue.Queue()
        
        # Play control
        self.playThread = None
        self.isPlaying: bool = False
        
        self.timeCallback: callable = callback
        
    def Play(self) -> None:
        """
        Play the audio
        """
        self.playThread = threading.Thread(target=self.PlayThread)
        self.playThread.start()
    
    def PlayThread(self) -> None:
        """
        Thread target to play the audio
        """
        if self.isPlaying:
            return

        self.isPlaying = True
        
        # Update the time callback
        startTime = time.time()
        sd.play(self.audio.audioArray, self.audio.sampleRate)
        while time.time() - startTime < self.audio.audioLength:
            self.timeCallback(time.time() - startTime)
            time.sleep(self.responseRate)
            if not self.isPlaying:
                return
        
        self.isPlaying = False
        
    
    def Pause(self) -> None:
        self.isPlaying = False
        sd.stop()