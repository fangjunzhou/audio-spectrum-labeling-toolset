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
        nFft: int = 512,
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
        self.nFft: int = nFft

        # Load the audio if audio file path is provided
        if audioFilePath is not None:
            self.LoadAudio(audioFilePath)

    def LoadAudio(self, audioFilePath: str, channel: int = 0) -> None:
        """
        Method to load a audio file.
        """
        # Load audio file
        self.audioArray, self.sampleRate = sf.read(
            audioFilePath, always_2d=False)
        # Get the target channel
        self.audioArray = self.audioArray[:, channel]
        # get the length of the audio file
        self.audioLength = len(self.audioArray) / self.sampleRate

        # Generate FFT Spectrum
        self.fftSpectrum = np.abs(librosa.core.spectrum.stft(
            self.audioArray, n_fft=self.nFft))

    def LoadAudioArray(self, audioArray: np.ndarray, sampleRate: int):
        """
        Load audio array.
        """
        self.audioArray = audioArray
        self.sampleRate = sampleRate
        self.audioLength = len(self.audioArray) / self.sampleRate

        # Generate FFT Spectrum
        self.fftSpectrum = np.abs(librosa.core.spectrum.stft(
            self.audioArray, n_fft=self.nFft))

    def ReconstructAudio(
        self,
        sampleRate: int,
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

        self.sampleRate = sampleRate

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

    def SetAudioPosition(self, position: float) -> None:
        # Set the audio position
        position = position * self.audio.audioLength
        self.audio.cursorPosition = position

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
        if self.isPlaying or self.audio.audioArray is None:
            return

        # Check if the audio array is empty
        if self.audio.audioArray.size == 0:
            return

        self.isPlaying = True

        # Get the sub array of the audio array
        playAudioArray = self.audio.audioArray[int(
            self.audio.cursorPosition * self.audio.sampleRate):]

        # Update the time callback
        timeStamp = time.time()
        sd.play(playAudioArray, self.audio.sampleRate)
        while self.audio.cursorPosition < self.audio.audioLength:
            # Update the time callback
            if self.timeCallback is not None:
                self.timeCallback(self.audio.cursorPosition)
            # Get delta time
            deltaTime = time.time() - timeStamp
            timeStamp = time.time()
            # Increase the cursor position
            self.audio.cursorPosition += deltaTime
            time.sleep(self.responseRate)
            if not self.isPlaying:
                return

        # Reset the cursor position
        self.audio.cursorPosition = 0
        if self.timeCallback is not None:
            self.timeCallback(self.audio.cursorPosition)
        self.isPlaying = False

    def Pause(self) -> None:
        self.isPlaying = False
        sd.stop()
