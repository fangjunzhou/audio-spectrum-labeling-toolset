from curses import window
import queue
import threading
import time
import librosa
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
        self.fftSpectrum = np.abs(librosa.core.spectrum.stft(self.audioArray))
    
    def ReconstructAudio(
        self,
        fftSpectrum: np.ndarray,
        freqHeight: int,
        freqSpan: tuple[int, int],
    ) -> np.ndarray:
        """
        Reconstruct the audio from the FFT spectrum.
        """
        # Check 0 <= freqSpan[0] <= freqSpan[1] <= freqHeight
        if freqSpan[0] < 0 or freqSpan[1] > freqHeight or freqSpan[0] > freqSpan[1]:
            raise ValueError("Invalid frequency span")
        
        # Reconstruct the audio from the FFT spectrum
        # Create a new np array for spectrogram
        self.fftSpectrum = np.zeros((freqHeight, fftSpectrum.shape[1]))
        # Store the FFT spectrum
        self.fftSpectrum[freqSpan[0]:freqSpan[1], :] = fftSpectrum[:, :]
        
        # Reconstruct the audio from the FFT spectrum
        self.audioArray = librosa.core.spectrum.griffinlim(self.fftSpectrum)
        
        return self.audioArray

class AudioPlayer:
    """
    Audio player class
    """
    def __init__(
        self,
        audio: Audio,
        responseRate: float,
        callback: callable = None,
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
            if self.timeCallback is not None:
                self.timeCallback(time.time() - startTime)
            time.sleep(self.responseRate)
            if not self.isPlaying:
                return
        
        self.isPlaying = False
        
    def Pause(self) -> None:
        self.isPlaying = False
        sd.stop()