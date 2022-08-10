import asyncio
from curses.panel import bottom_panel
import os
from turtle import st

from matplotlib import pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk

import tkinter as tk
from tkinter import *
from tkinter import ttk
from tkinter import filedialog
from Utils.AudioPlot import AudioMagnitudePlot, AudioSpectrumPlot

from Utils.AudioProcess import Audio


class App(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.pack(fill=BOTH, expand=True)

        # =====INITIALIZE=====

        # Main audio object
        self.mainAudio: Audio = Audio()

        # Status text
        self.status = tk.StringVar()
        self.status.set("Status: Ready")
        # Loading status
        self.loadingStatus = False
        # Matplotlib figure
        self.magFig, self.magAx = plt.subplots()
        self.magFig.set_figheight(2)
        self.magFig.tight_layout()
        self.magCanvas = FigureCanvasTkAgg(self.magFig, self)
        self.fftFig, self.fftAx = plt.subplots()
        self.fftCanvas = FigureCanvasTkAgg(self.fftFig, self)
        self.fftFig.tight_layout()
        # Audio plot
        self.audioMagnitudePlot = AudioMagnitudePlot(
            self.mainAudio, self.magAx, self.magCanvas)
        self.audioSpectrumPlot = AudioSpectrumPlot(
            self.mainAudio, self.fftAx, self.fftCanvas)

        # =====FRAMES=====

        # Top frame for file selection
        self.topFrame = tk.Frame(self)
        self.topFrame.pack(side=TOP, fill=X)

        # Bottom frame for play control
        self.bottomFrame = tk.Frame(self)
        self.bottomFrame.pack(side=BOTTOM, fill=X)

        # Left frame for tools
        self.leftFrame = tk.Frame(self)
        self.leftFrame.pack(side=LEFT)

        self.DrawTopFrame()

        self.DrawMainFrame()

        self.DrawLeftFrame()

        self.DrawBottomFrame()

    def DrawTopFrame(self):
        """
        Method to drop the top frame
        """
        # Create a label and button for file selection
        self.openFileName = tk.StringVar()
        self.openFileName.set("Select a file")

        fileNameLabel = tk.Label(self.topFrame, textvariable=self.openFileName)
        fileNameLabel.pack(side=tk.LEFT, expand=True)
        selectFileButton = tk.Button(
            self.topFrame, text="Select a file", command=self.SelectFile)
        selectFileButton.pack(side=tk.LEFT)

    def DrawMainFrame(self):
        """
        Method to draw the main frame
        """
        self.magCanvas.draw()
        self.magCanvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=False)
        self.fftCanvas.draw()
        self.fftCanvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)

    def DrawLeftFrame(self):
        """
        Method to draw the left frame
        """
        # Label for Spectrogram
        spectrogramLabel = tk.Label(
            self.leftFrame, text="Spectrogram Settings")
        spectrogramLabel.grid(row=0, column=0)

        # Slider for Spectrogram brightness enhancement
        brightnessSliderLabel = tk.Label(
            self.leftFrame, text="Brightness")
        brightnessSliderLabel.grid(row=1, column=0)
        brightnessSlider = tk.Scale(
            self.leftFrame,
            from_=1, to=.01, resolution=.01,
            orient=tk.HORIZONTAL,
            command=self.BrightnessSlider)
        brightnessSlider.set(1)
        brightnessSlider.grid(row=1, column=1)

    def DrawBottomFrame(self):
        """
        Method to draw the bottom frame
        """
        playControl = {
            "play": self.Play,
            "pause": self.Pause
        }
        playControlFrame = tk.Frame(self.bottomFrame)
        playControlFrame.pack(side=tk.TOP)
        for key in playControl:
            playControl[key] = tk.Button(
                playControlFrame, text=key, command=playControl[key])
            playControl[key].pack(side=tk.LEFT)

        toolbarFrame = tk.Frame(self.bottomFrame)
        toolbarFrame.pack(side=TOP)
        toolbar = NavigationToolbar2Tk(self.fftCanvas, toolbarFrame)
        toolbar.update()

        # Status bar
        statusBar = tk.Label(self.bottomFrame, textvariable=self.status)
        statusBar.pack(side=BOTTOM, anchor=W)

    def SelectFile(self):
        # Get current working directory
        currDir = os.getcwd()
        # Open a file dialog and set the file name in the label
        selectedFileName = filedialog.askopenfilename(initialdir=currDir, title="Select a file",
                                                      filetypes=(
                                                          ("wav files", "*.wav"),
                                                          ("all files", "*.*")
                                                      ))
        self.openFileName.set(selectedFileName)

        # Run the helper method to load the file
        asyncio.run(self.SelectFileHelper(selectedFileName))

    async def SelectFileHelper(self, selectedFileName):
        """
        Helper method to select a file
        """
        # Set the status to loading
        self.status.set("Status: Loading")

        # Load audio file
        self.mainAudio.LoadAudio(selectedFileName)
        # Plot audio file
        self.audioMagnitudePlot.Plot()
        self.audioSpectrumPlot.Plot()

        # Set the status to ready
        self.status.set("Status: Ready")

    def BrightnessSlider(self, value):
        """
        Method to handle the brightness slider
        """
        self.audioSpectrumPlot.SetBrightnessEnhancement(float(value))

    def Play(self):
        """
        Play the audio file
        """
        # TODO: Play the audio file
        pass

    def Pause(self):
        """
        Pause the audio file
        """
        # TODO: Pause the audio file
        pass


# create the application
dataSetGenerator = App()

# here are method calls to the window manager class
dataSetGenerator.master.title("Audio Data Set Generator")
dataSetGenerator.master.minsize(width=800, height=400)
dataSetGenerator.master.geometry("1000x500")

# start the program
dataSetGenerator.mainloop()
