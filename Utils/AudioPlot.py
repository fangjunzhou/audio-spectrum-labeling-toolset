
import librosa
import librosa.display
from turtle import pos
import numpy as np
from Utils.AudioProcess import Audio
from matplotlib import patches, pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.widgets import Cursor

from Utils.DataSetLabel import DataSetLabel


class AudioPlot:
    """
    Base class for all audio plots.
    """

    def __init__(self,
                 audio: Audio,
                 ax: plt.Axes,
                 canvas: FigureCanvasTkAgg,
                 onRelease: callable = None,
    ) -> None:
        # Constants
        self.X_TICK_NUMBER = 10
        self.Y_TICK_NUMBER = 5

        # The audio object currently being plotted
        self.audio: Audio = audio
        # The matplotlib axes object
        self.ax: plt.Axes = ax
        self.canvas: FigureCanvasTkAgg = canvas
        self.canvas.mpl_connect("button_press_event", self.OnCanvasClick)
        self.canvas.mpl_connect("button_release_event", self.OnCanvasRelease)

        # The time position of the cursor.
        self.cursorPosition: float = 0
        
        # Mouse cursor related
        self.onRelease = onRelease
        self.pressCoord: tuple(float, float) = None
        self.releaseCoord: tuple(float, float) = None

    def Plot(self) -> None:
        """
        Method to plot the audio.
        """
        pass

    def SetCursorPosition(self, position: float) -> None:
        """
        Set the cursor position.
        """
        if position < 0:
            position = 0
        if position > self.audio.audioLength:
            position = self.audio.audioLength
        self.cursorPosition = position / self.audio.audioLength
        self.Plot()
    
    def OnCanvasClick(self, event) -> None:
        """
        Method to handle the click event on the canvas.
        """
        self.pressCoord = (event.xdata, event.ydata)
    
    def OnCanvasRelease(self, event) -> None:
        """
        Method to handle the release event on the canvas.
        """
        self.releaseCoord = (event.xdata, event.ydata)
        
        self.OnRelease(self.pressCoord, self.releaseCoord)
    
    def OnRelease(self, startCoord: tuple[float, float], endCoord: tuple[float, float]) -> None:
        """
        Method to handle the release event on the canvas.
        """
        print(f"{startCoord} => {endCoord}")
        
        if self.onRelease is None:
            return
        
        self.onRelease(startCoord, endCoord)


class AudioMagnitudePlot(AudioPlot):
    """
    Audio magnitude plot.
    """

    def __init__(self, audio: Audio, ax: plt.Axes, canvas: FigureCanvasTkAgg) -> None:
        super().__init__(audio, ax, canvas)

    def Plot(self) -> None:
        """
        Method to plot the audio.
        """
        # Get the audio array
        audioArray = self.audio.audioArray
        # Average the audio array into length of 8192
        groupSize = len(audioArray) // 8192
        # Get the average of each group and combine into a single array
        compressedAudioArray = []
        for i in range(0, len(audioArray), groupSize):
            # Get the actual length of the group
            groupSize = min(groupSize, len(audioArray) - i)
            compressedAudioArray.append(sum(
                [abs(mag) for mag in audioArray[i:i + groupSize]]
            )/groupSize)

        # Clear the axes
        self.ax.cla()
        # Plot the audio array
        self.ax.plot(compressedAudioArray)
        # Set ticks of the x axis to be the corresponding time position
        sampleIndeces = np.arange(0, len(compressedAudioArray), len(
            compressedAudioArray) // self.X_TICK_NUMBER)
        self.ax.set_xticks(sampleIndeces)
        tickLabels = [
            (
                "{:.2f}".format(self.audio.audioLength *
                                i / len(compressedAudioArray))
            ) for i in sampleIndeces]
        self.ax.set_xticklabels(tickLabels)
        # Set the x-axis label
        self.ax.set_xlabel("Time (s)")

        # Plot the cursor as a vertical line
        self.ax.axvline(self.cursorPosition * len(compressedAudioArray), color='r')

        # Update the canvas
        self.canvas.draw()


class AudioSpectrumPlot(AudioPlot):
    """
    Audio spectrum plot.
    """

    def __init__(
        self,
        audio: Audio,
        ax: plt.Axes,
        canvas: FigureCanvasTkAgg,
        onRelease: callable = None
    ) -> None:
        super().__init__(audio, ax, canvas, onRelease)
        
        # Label highlighting
        self.highlightedLabels: list[DataSetLabel] = []

        # Settings for the audio spectrum plot
        self.brightnessEnhancement = 0
        self.contrastEnhancement = 1.0
        
        # Plot cursor
        self.cursor = Cursor(self.ax, useblit=True, color='white', linewidth=1)

    def Plot(self) -> None:
        # Get the audio spectrum
        audioSpectrum = self.audio.fftSpectrum

        if audioSpectrum is None:
            return
        
        # Get max value in the audio spectrum
        maxVal = np.amax(audioSpectrum)
        audioSpectrum = audioSpectrum / maxVal
        
        # Enhance the contrast of the audio spectrum
        audioSpectrum = 1 - (1-audioSpectrum)**self.contrastEnhancement
        
        # Enhance the brightness of the spectrum
        audioSpectrum = audioSpectrum + self.brightnessEnhancement

        # Clear the axes
        self.ax.cla()
        # Plot the audio spectrum
        self.ax.imshow(audioSpectrum, aspect='auto', origin='lower', vmin=0, vmax=1)
        
        # Set x axis ticks to be the corresponding time
        self.ax.set_xticks(np.arange(0, audioSpectrum.shape[1], audioSpectrum.shape[1] // self.X_TICK_NUMBER))
        self.ax.set_xticklabels(
            [
                "{:.2f}".format(self.audio.audioLength * i / audioSpectrum.shape[1]) 
                for i in np.arange(
                    0,
                    audioSpectrum.shape[1],
                    audioSpectrum.shape[1] // self.X_TICK_NUMBER
                )
             ]
        )
        
        # Get frequency array
        freqArr = librosa.fft_frequencies(sr=self.audio.sampleRate, n_fft=self.audio.fftSpectrum.shape[1])
        self.ax.set_yticks(np.arange(0, len(freqArr), len(freqArr) // self.Y_TICK_NUMBER))
        self.ax.set_yticklabels(
            [
                "{:.2f}".format(freq) for freq in freqArr[::len(freqArr) // self.Y_TICK_NUMBER]
            ]
        )

        # Plot the cursor as a vertical line
        # self.ax.axvline(self.cursorPosition * self.audio.fftSpectrum.shape[1], color='r')
        
        # Plot the highlighted labels
        for label in self.highlightedLabels:
            # Get the start and end of x
            xStart = label.startTime / self.audio.audioLength * audioSpectrum.shape[1]
            xEnd = label.endTime / self.audio.audioLength * audioSpectrum.shape[1]
            # Get the first frequency index in freqArr >= label.startFreq
            yStart = np.argmax(freqArr >= label.startFreq)
            yEnd = np.argmax(freqArr >= label.endFreq)
            # Plot the rectangle
            self.ax.add_patch(
                patches.Rectangle(
                    (xStart, yStart),
                    xEnd - xStart,
                    yEnd - yStart,
                    fill=False,
                    edgecolor='r',
                    linewidth=2
                )
            )

        # Update the canvas
        self.canvas.draw()

    def SetBrightnessEnhancement(self, value: float) -> None:
        self.brightnessEnhancement = value

        self.Plot()
    
    def SetContrastEnhancement(self, value: float) -> None:
        self.contrastEnhancement = value

        self.Plot()
    
    def UpdateHighlightedLabels(self, labels: list[DataSetLabel]) -> None:
        self.highlightedLabels = labels

        self.Plot()
