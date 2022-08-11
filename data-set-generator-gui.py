from curses.panel import bottom_panel
import os
from termios import VMIN
import threading
from time import sleep
from matplotlib import pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk

import tkinter as tk
from tkinter import *
from tkinter import ttk
from tkinter import filedialog

import numpy as np

from Utils.AudioPlot import AudioMagnitudePlot, AudioSpectrumPlot
from Utils.AudioProcess import Audio, AudioPlayer


class App(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.pack(fill=BOTH, expand=True)
        self.master.protocol("WM_DELETE_WINDOW", self.OnClose)

        # =====INITIALIZE=====

        # Main audio object
        self.mainAudio: Audio = Audio()
        self.mainAudioPlayer: AudioPlayer = None

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
        self.fftFig.tight_layout()
        self.fftCanvas = FigureCanvasTkAgg(self.fftFig, self)
        # Audio plot
        self.audioMagnitudePlot = AudioMagnitudePlot(
            self.mainAudio, self.magAx, self.magCanvas)
        self.audioSpectrumPlot = AudioSpectrumPlot(
            self.mainAudio, self.fftAx, self.fftCanvas, self.SpectrumSelected)
        
        # FFT contrast control
        self.fftContrastCurveFig, self.fftContrastCurveAx = plt.subplots()
        self.fftContrastCurveFig.set_size_inches(3, 2)
        self.fftContrastCurveFig.tight_layout()
        
        # FFT detail view
        self.fftDetailViewFig, self.fftDetailViewAx = plt.subplots()
        self.fftDetailViewFig.set_size_inches(4, 3)
        self.fftDetailViewFig.tight_layout()
        # FFT detail audio
        self.fftDetailAudio: Audio = Audio()
        self.fftDetailAudioPlayer: AudioPlayer = AudioPlayer(self.fftDetailAudio, 1)

        # =====FRAMES=====

        # Top frame for file selection
        self.topFrame = tk.Frame(self)
        self.topFrame.pack(side=TOP, fill=X)

        # Bottom frame for play control
        self.bottomFrame = tk.Frame(self)
        self.bottomFrame.pack(side=BOTTOM, fill=X)

        # Left frame for tools
        self.leftFrame = tk.Frame(self)
        self.leftFrame.pack(side=LEFT, fill=Y)
        
        # Right frame for FFT Inspector
        self.rightFrame = tk.Frame(self)
        self.rightFrame.pack(side=RIGHT, fill=Y)

        self.DrawTopFrame()

        self.DrawMainFrame()

        self.DrawLeftFrame()
        
        self.DrawRightFrame()

        self.DrawBottomFrame()

    def DrawTopFrame(self):
        """
        Method to drop the top frame
        """
        # Create a label and button for file selection
        self.openFileName = tk.StringVar()
        self.openFileName.set("Select a file")

        fileNameLabel = ttk.Label(self.topFrame, textvariable=self.openFileName)
        fileNameLabel.pack(side=tk.LEFT, expand=True)
        selectFileButton = ttk.Button(
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
        
        # Create canvas for spectrum frame
        leftCanvas = Canvas(self.leftFrame)
        leftCanvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Add a scrollbar to the canvas
        leftCanvasScrollbar = ttk.Scrollbar(self.leftFrame, orient=tk.VERTICAL, command=leftCanvas.yview)
        leftCanvasScrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Configure the canvas
        leftCanvas.configure(yscrollcommand=leftCanvasScrollbar.set)
        leftCanvas.bind(
            '<Configure>',
            lambda e: leftCanvas.configure(
                scrollregion=leftCanvas.bbox('all')
            )
        )
        
        # Create scrollable frame for canvas
        leftFrameScrollable = tk.Frame(leftCanvas)
        # Add the frame to the canvas
        leftCanvas.create_window((0, 0), window=leftFrameScrollable, anchor=tk.NW)
        
        # Label for Spectrogram
        spectrogramLabel = ttk.Label(
            leftFrameScrollable, text="Spectrogram Settings")
        spectrogramLabel.grid(row=0, column=0)

        # Slider for Spectrogram brightness enhancement
        brightnessSliderLabel = ttk.Label(
            leftFrameScrollable, text="Brightness")
        brightnessSliderLabel.grid(row=1, column=0)
        brightnessSlider = ttk.Scale(
            leftFrameScrollable,
            from_=0, to=1,
            orient=tk.HORIZONTAL,
            command=self.BrightnessSlider)
        brightnessSlider.set(0)
        brightnessSlider.grid(row=1, column=1)
        
        # Slider for Spectrogram contrast enhancement
        self.fftContrastCurveCanvas = FigureCanvasTkAgg(self.fftContrastCurveFig, leftFrameScrollable)
        contrastSliderLabel = ttk.Label(
            leftFrameScrollable, text="Contrast")
        contrastSliderLabel.grid(row=2, column=0)
        contrastSlider = ttk.Scale(
            leftFrameScrollable,
            from_=1, to=32,
            orient=tk.HORIZONTAL,
            command=self.ContrastSlider)
        contrastSlider.set(1)
        contrastSlider.grid(row=2, column=1)
        self.ContrastSlider(1)
        self.fftContrastCurveCanvas.get_tk_widget().grid(row=3, column=0, columnspan=2)
    
    def DrawRightFrame(self):
        """
        Method to draw the right frame.
        """
        # Pack the fft detail canvas
        self.fftDetailCanvas = FigureCanvasTkAgg(self.fftDetailViewFig, self.rightFrame)
        self.fftDetailCanvas.draw()
        self.fftDetailCanvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=False)
        
        # Create canvas for spectrum frame
        rightCanvas = Canvas(self.rightFrame)
        rightCanvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Add a scrollbar to the canvas
        rightCanvasScrollbar = ttk.Scrollbar(self.rightFrame, orient=tk.VERTICAL, command=rightCanvas.yview)
        rightCanvasScrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Configure the canvas
        rightCanvas.configure(yscrollcommand=rightCanvasScrollbar.set)
        rightCanvas.bind(
            '<Configure>',
            lambda e: rightCanvas.configure(
                scrollregion=rightCanvas.bbox('all')
            )
        )
        
        # Create scrollable frame for canvas
        rightFrameScrollable = tk.Frame(rightCanvas)
        # Add the frame to the canvas
        rightCanvas.create_window((0, 0), window=rightFrameScrollable, anchor=tk.NW)
        
    def DrawBottomFrame(self):
        """
        Method to draw the bottom frame
        """
        playControl = {
            "Play From Start": self.Play,
            "Stop": self.Pause
        }
        playControlFrame = tk.Frame(self.bottomFrame)
        playControlFrame.pack(side=tk.TOP)
        for key in playControl:
            playControl[key] = ttk.Button(
                playControlFrame, text=key, command=playControl[key])
            playControl[key].pack(side=tk.LEFT)

        # Status bar
        statusBar = ttk.Label(self.bottomFrame, textvariable=self.status)
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
        loadFileThread = threading.Thread(target=self.SelectFileHelper, args=(selectedFileName,))
        loadFileThread.start()

    def SelectFileHelper(self, selectedFileName):
        """
        Helper method to select a file
        """
        # Set the status to loading
        self.status.set("Status: Loading")

        # Load audio file
        self.mainAudio.LoadAudio(selectedFileName)
        print("Loaded audio file")
        print("Audio length (s): " + str(self.mainAudio.audioLength))
        print("Audio length (frame): " + str(len(self.mainAudio.audioArray)))
        print("Audio sample rate: " + str(self.mainAudio.sampleRate))
        
        # Set up audio player
        self.mainAudioPlayer = AudioPlayer(
            self.mainAudio,
            0.2,
            self.UpdateAudioCursor
        )
        
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
    
    def ContrastSlider(self, value):
        """
        Method to handle the contrast slider
        """
        # Plot f(x) = 1 - (1-x)^(contrast)
        self.fftContrastCurveAx.clear()
        self.fftContrastCurveAx.plot(
            np.linspace(0, 1, 1000),
            1 - np.power(1 - np.linspace(0, 1, 1000), float(value))
        )
        self.fftContrastCurveAx.set_title("Contrast Curve")
        self.fftContrastCurveCanvas.draw()
        
        self.audioSpectrumPlot.SetContrastEnhancement(float(value))

    def Play(self):
        """
        Play the audio file
        """
        if self.mainAudioPlayer is None:
            return
        
        # Play the audio file
        self.mainAudioPlayer.Play()

    def Pause(self):
        """
        Pause the audio file
        """
        if self.mainAudioPlayer is None:
            return
        
        # Pause the audio file
        self.mainAudioPlayer.Pause()
    
    def UpdateAudioCursor(self, value):
        """
        Method to update the audio cursor
        """
        self.audioMagnitudePlot.SetCursorPosition(value)
        self.audioSpectrumPlot.SetCursorPosition(value)
    
    def SpectrumSelected(self, startCoord: tuple[float, float], endCoord: tuple[float, float]):
        """
        Method to handle the spectrum selected
        """
        # Check if the start and end coordinates are valid
        if startCoord is None or endCoord is None:
            print("Invalid coordinates")
            return
        if startCoord[0] is None or startCoord[1] is None or endCoord[0] is None or endCoord[1] is None:
            print("Invalid coordinates")
            return
        
        if self.mainAudio is None or self.mainAudio.audioArray is None:
            return
        
        # Construct x coord span
        xSpan = (int(startCoord[0]), int(endCoord[0]))
        # Sort the x coord span
        xSpan = sorted(xSpan)
        # Construct y coord span
        ySpan = (int(startCoord[1]), int(endCoord[1]))
        ySpan = sorted(ySpan)
        
        # Slice the spectrum array
        slicedSpectrum = self.mainAudio.fftSpectrum[ySpan[0]:ySpan[1], xSpan[0]:xSpan[1]]
        
        print("FFT Spectrum Sliced:")
        
        self.fftDetailViewAx.clear()
        self.fftDetailViewAx.imshow(
            slicedSpectrum,
            aspect='auto',
            origin='lower')
        self.fftDetailViewAx.set_title("FFT Spectrum")
        self.fftDetailCanvas.draw()
        
        self.fftDetailAudio.ReconstructAudio(
            slicedSpectrum,
            self.mainAudio.fftSpectrum.shape[0],
            ySpan
        )
        
        self.fftDetailAudioPlayer.Play()
        
        
    def OnClose(self):
        """
        Method to exit the program
        """
        print("Exiting")
        # Pause the audio player
        self.Pause()
        
        # Close the window
        self.quit()
        self.destroy()
        exit()


# create the application
dataSetGenerator = App()

# here are method calls to the window manager class
dataSetGenerator.master.title("Audio Data Set Generator")
dataSetGenerator.master.minsize(width=1200, height=600)
dataSetGenerator.master.geometry("1200x600")

# start the program
dataSetGenerator.mainloop()
