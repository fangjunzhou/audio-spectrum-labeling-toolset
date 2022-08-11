from curses.panel import bottom_panel
import os
import threading
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
            self.mainAudio, self.fftAx, self.fftCanvas)
        
        # FFT contrast control
        self.fftContrastCurveFig, self.fftContrastCurveAx = plt.subplots()
        self.fftContrastCurveFig.set_size_inches(2, 2)
        self.fftContrastCurveFig.tight_layout()
        
        # FFT detail view
        self.fftDetailViewFig, self.fftDetailViewAx = plt.subplots()
        self.fftDetailViewFig.set_size_inches(4, 3)
        self.fftDetailViewFig.tight_layout()

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
        spectrogramLabel = tk.Label(
            leftFrameScrollable, text="Spectrogram Settings")
        spectrogramLabel.grid(row=0, column=0)

        # Slider for Spectrogram brightness enhancement
        brightnessSliderLabel = tk.Label(
            leftFrameScrollable, text="Brightness")
        brightnessSliderLabel.grid(row=1, column=0)
        brightnessSlider = tk.Scale(
            leftFrameScrollable,
            from_=0, to=1, resolution=.001,
            orient=tk.HORIZONTAL,
            command=self.BrightnessSlider)
        brightnessSlider.set(0)
        brightnessSlider.grid(row=1, column=1)
        
        # Slider for Spectrogram contrast enhancement
        contrastSliderLabel = tk.Label(
            leftFrameScrollable, text="Contrast")
        contrastSliderLabel.grid(row=2, column=0)
        contrastSlider = tk.Scale(
            leftFrameScrollable,
            from_=1, to=32, resolution=.01,
            orient=tk.HORIZONTAL,
            command=self.ContrastSlider)
        contrastSlider.set(1)
        contrastSlider.grid(row=2, column=1)
        self.fftContrastCurveCanvas = FigureCanvasTkAgg(self.fftContrastCurveFig, leftFrameScrollable)
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
            playControl[key] = tk.Button(
                playControlFrame, text=key, command=playControl[key])
            playControl[key].pack(side=tk.LEFT)

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
        playThread = threading.Thread(target=self.mainAudioPlayer.Play)
        playThread.start()

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
