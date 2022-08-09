
import math
import numpy as np
from Utils.AudioProcess import Audio
from matplotlib import pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


class AudioPlot:
    """
    Base class for all audio plots.
    """

    def __init__(self, audio: Audio, ax: plt.Axes, canvas: FigureCanvasTkAgg) -> None:
        # The audio object currently being plotted
        self.audio: Audio = audio
        # The matplotlib axes object
        self.ax: plt.Axes = ax
        self.canvas: FigureCanvasTkAgg = canvas

        # The time position of the cursor.
        self.cursorPosition: float = 0

    def Plot(self) -> None:
        """
        Method to plot the audio.
        """
        pass


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
        # Plot the cursor as a vertical line
        self.ax.axvline(self.cursorPosition, color='r')

        # Update the canvas
        self.canvas.draw()
