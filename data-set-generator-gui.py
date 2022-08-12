from curses.panel import bottom_panel
import os
import platform
import librosa
import threading
from time import sleep, time
from timeit import timeit
from matplotlib import pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk

import tkinter as tk
from tkinter import *
from tkinter import ttk
from tkinter import filedialog

import numpy as np

from Utils.AudioPlot import AudioMagnitudePlot, AudioSpectrumPlot
from Utils.AudioProcess import Audio, AudioPlayer
from Utils.DataSetLabelInspector import DataSetLabelGroup, DataSetLabelsInspector
from Utils.FFTInspector import FFTDetailInspector

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
        
        # =====MENU BARS=====
        self.menuBar = tk.Menu(self.master)
        fileMenu = tk.Menu(self.menuBar, tearoff=0)
        playMenu = tk.Menu(self.menuBar, tearoff=0)
        spectrogramMenu = tk.Menu(self.menuBar, tearoff=0)
        
        # File menu
        if platform.system() == "Darwin":
            fileMenu.add_command(label="Open (Cmd + O)", command=self.SelectFile)
            self.master.bind("<Command-o>", self.SelectFile)
        elif platform.system() == "Windows":
            fileMenu.add_command(label="Open (Ctrl + O)", command=self.SelectFile)
            self.master.bind("<Control-o>", self.SelectFile)
        
        # Play menu
        if platform.system() == "Darwin":
            playMenu.add_command(label="Play (Cmd + P)", command=self.Play)
            self.master.bind("<Command-p>", self.Play)
        elif platform.system() == "Windows":
            playMenu.add_command(label="Play (Ctrl + P)", command=self.Play)
            self.master.bind("<Control-p>", self.Play)
        
        if platform.system() == "Darwin":
            playMenu.add_command(label="Pause (Cmd + Shift + P)", command=self.Pause)
            self.master.bind("<Command-P>", self.Pause)
        elif platform.system() == "Windows":
            playMenu.add_command(label="Pause (Ctrl + Shift + P)", command=self.Pause)
            self.master.bind("<Control-P>", self.Pause)
        
        # Spectrogram menu
        if platform.system() == "Darwin":
            spectrogramMenu.add_command(label="Label Spectrogram (Cmd + L)", command=self.fftInspector.AddToCurrentLabelGroup)
            self.master.bind("<Command-l>", self.fftInspector.AddToCurrentLabelGroup)
        elif platform.system() == "Windows":
            spectrogramMenu.add_command(label="Label Spectrogram (Ctrl + L)", command=self.fftInspector.AddToCurrentLabelGroup)
            self.master.bind("<Control-l>", self.fftInspector.AddToCurrentLabelGroup)
        
        self.menuBar.add_cascade(label="File", menu=fileMenu)
        self.menuBar.add_cascade(label="Play", menu=playMenu)
        self.menuBar.add_cascade(label="Spectrogram", menu=spectrogramMenu)

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
        # Frame for spectrogram controls
        spectrogramControlFrame = tk.Frame(self.leftFrame)
        spectrogramControlFrame.pack(side=tk.TOP, fill=tk.X, expand=False)
        
        # Label for Spectrogram
        spectrogramLabel = ttk.Label(
            spectrogramControlFrame, text="Spectrogram Settings")
        spectrogramLabel.grid(row=0, column=0)

        # Slider for Spectrogram brightness enhancement
        brightnessSliderLabel = ttk.Label(
            spectrogramControlFrame, text="Brightness")
        brightnessSliderLabel.grid(row=1, column=0)
        brightnessSlider = ttk.Scale(
            spectrogramControlFrame,
            from_=0, to=1,
            orient=tk.HORIZONTAL,
            command=self.BrightnessSlider)
        brightnessSlider.set(0)
        brightnessSlider.grid(row=1, column=1)
        
        # Slider for Spectrogram contrast enhancement
        self.fftContrastCurveCanvas = FigureCanvasTkAgg(self.fftContrastCurveFig, spectrogramControlFrame)
        contrastSliderLabel = ttk.Label(
            spectrogramControlFrame, text="Contrast")
        contrastSliderLabel.grid(row=2, column=0)
        contrastSlider = ttk.Scale(
            spectrogramControlFrame,
            from_=1, to=32,
            orient=tk.HORIZONTAL,
            command=self.ContrastSlider)
        contrastSlider.set(1)
        contrastSlider.grid(row=2, column=1)
        self.ContrastSlider(1)
        self.fftContrastCurveCanvas.get_tk_widget().grid(row=3, column=0, columnspan=2)
        
        # Data set label groups
        self.dataSetLabelInspector = DataSetLabelsInspector(
            self.audioSpectrumPlot,
            master=self.leftFrame
        )
        self.dataSetLabelInspector.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
    
    def DrawRightFrame(self):
        """
        Method to draw the right frame.
        """
        
        self.fftInspector = FFTDetailInspector(
            self.dataSetLabelInspector,
            master=self.rightFrame
        )
        self.fftInspector.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        
    def DrawBottomFrame(self):
        """
        Method to draw the bottom frame
        """
        playControl = {
            "Play": self.Play,
            "Pause": self.Pause
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


    def SelectFile(self, event=None):
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
        # Check selected file name is not empty
        if selectedFileName == "":
            print("No file selected")
            return
        
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

    def Play(self, event=None):
        """
        Play the audio file
        """
        if self.mainAudioPlayer is None:
            return
        
        # Play the audio file
        self.mainAudioPlayer.Play()

    def Pause(self, event=None):
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
        
        # Update FFT Detail Inspector
        self.fftInspector.fftDetailViewAx.clear()
        self.fftInspector.fftDetailViewAx.imshow(
            slicedSpectrum,
            aspect='auto',
            origin='lower')
        self.fftInspector.fftDetailCanvas.draw()
        
        freqArr = librosa.fft_frequencies(sr=self.mainAudio.sampleRate, n_fft=self.mainAudio.fftSpectrum.shape[1])
        self.fftInspector.SetFFTDetail(
            xSpan[0] / self.mainAudio.fftSpectrum.shape[1] * self.mainAudio.audioLength,
            xSpan[1] / self.mainAudio.fftSpectrum.shape[1] * self.mainAudio.audioLength,
            freqArr[int(ySpan[0])],
            freqArr[(ySpan[1])]
        )
        
        self.fftInspector.fftDetailAudio.ReconstructAudio(
            self.mainAudio.sampleRate,
            slicedSpectrum,
            self.mainAudio.fftSpectrum.shape[0],
            ySpan
        )
        
        self.fftInspector.fftDetailAudioPlayer.Play()
            
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
dataSetGenerator.master.configure(menu=dataSetGenerator.menuBar)

# start the program
dataSetGenerator.mainloop()
