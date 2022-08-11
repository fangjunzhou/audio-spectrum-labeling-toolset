
import math
import re
from turtle import pos
import numpy as np
from Utils.AudioProcess import Audio
from matplotlib import pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.widgets import Cursor


class AudioPlot:
    """
    Base class for all audio plots.
    """

    def __init__(self, audio: Audio, ax: plt.Axes, canvas: FigureCanvasTkAgg) -> None:
        # Constants
        self.X_TICK_NUMBER = 16
        self.Y_TICK_NUMBER = 8

        # The audio object currently being plotted
        self.audio: Audio = audio
        # The matplotlib axes object
        self.ax: plt.Axes = ax
        self.canvas: FigureCanvasTkAgg = canvas
        self.canvas.mpl_connect("button_press_event", self.OnCanvasClick)
        self.canvas.mpl_connect("button_release_event", self.OnCanvasRelease)

        # The time position of the cursor.
        self.cursorPosition: float = 0

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
        print(
            f"You clicked on the canvas at position ({event.xdata}, {event.ydata})"
        )
    
    def OnCanvasRelease(self, event) -> None:
        """
        Method to handle the release event on the canvas.
        """
        print(
            f"You released on the canvas at position ({event.xdata}, {event.ydata})"
        )


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

    def __init__(self, audio: Audio, ax: plt.Axes, canvas: FigureCanvasTkAgg) -> None:
        super().__init__(audio, ax, canvas)

        # Settings for the audio spectrum plot
        self.brightnessEnhancement = 0
        self.contrastEnhancement = 1.0
        
        # Plot cursor
        self.cursor = Cursor(self.ax, useblit=True, color='red', linewidth=1)

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

        # Set ticks of the x axis to be the corresponding time position
        sampleIndeces = np.arange(0, len(self.audio.fftTimeSpan), len(
            self.audio.fftTimeSpan) // self.X_TICK_NUMBER)
        self.ax.set_xticks(sampleIndeces)
        tickLabels = [
            (
                "{:.2f}".format(self.audio.audioLength *
                                i / len(self.audio.fftTimeSpan))
            ) for i in sampleIndeces]
        self.ax.set_xticklabels(tickLabels)
        # Set the x-axis label
        self.ax.set_xlabel("Time (s)")

        # Set the ticks of the y axis to be the corresponding frequency position
        sampleIndeces = np.arange(0, len(self.audio.fftFreqSample), len(
            self.audio.fftFreqSample) // self.Y_TICK_NUMBER)
        self.ax.set_yticks(sampleIndeces)
        tickLabels = [
            self.audio.fftFreqSample[i] for i in sampleIndeces]
        self.ax.set_yticklabels(tickLabels)
        self.ax.set_ylabel("Frequency (Hz)")

        # Plot the cursor as a vertical line
        self.ax.axvline(self.cursorPosition * len(self.audio.fftTimeSpan), color='r')

        # Update the canvas
        self.canvas.draw()

    def SetBrightnessEnhancement(self, value: float) -> None:
        self.brightnessEnhancement = value

        self.Plot()
    
    def SetContrastEnhancement(self, value: float) -> None:
        self.contrastEnhancement = value

        self.Plot()
