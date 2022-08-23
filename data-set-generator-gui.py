import copy
from curses.panel import bottom_panel
import os
import platform
from tkinter import messagebox
import librosa
import threading
from time import sleep, time
from timeit import timeit
from matplotlib import pyplot as plt
from matplotlib.backend_bases import key_press_handler
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk

import tkinter as tk
from tkinter import *
from tkinter import ttk
from tkinter import filedialog

import numpy as np
from Config import FIG_DPI, MAX_AUDIO_LENGTH, MIN_AUDIO_LENGTH

from Utils.AudioPlot import AudioMagnitudePlot, AudioSpectrumPlot
from Utils.AudioProcess import Audio, AudioPlayer
from Utils.DataSetLabel import DataSetLabel
from Utils.DataSetLabelInspector import DataSetLabelsInspector
from Utils.FFTInspector import FFTDetailInspector


class App(ttk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.pack(fill=BOTH, expand=True)
        self.master.protocol("WM_DELETE_WINDOW", self.OnClose)

        # =====INITIALIZE=====

        # Root audio object.
        self.rootAudio: Audio = Audio()
        # Audio offset for the play window.
        self.currOffset = 0
        # Main audio and player.
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
        self.magFig.set_dpi(FIG_DPI)
        self.magFig.tight_layout()
        self.magCanvas = FigureCanvasTkAgg(self.magFig, self)
        self.fftFig, self.fftAx = plt.subplots()
        self.fftFig.set_dpi(FIG_DPI)
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
        self.fftContrastCurveFig.set_dpi(FIG_DPI)
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

        self.MenuBar()

    def DrawTopFrame(self):
        """
        Method to drop the top frame
        """
        # Create a label and button for file selection
        self.openFileName = tk.StringVar()
        self.openFileName.set("Select a file")

        fileNameLabel = ttk.Label(
            self.topFrame, textvariable=self.openFileName)
        fileNameLabel.pack(side=tk.LEFT, expand=True)
        selectFileButton = ttk.Button(
            self.topFrame, text="Select a file", command=self.SelectFile)
        selectFileButton.pack(side=tk.LEFT)

    def DrawMainFrame(self):
        """
        Method to draw the main frame
        """
        # Audio offset
        self.offsetFrame = tk.Frame(self)
        self.offsetFrame.pack(side=tk.TOP, fill=tk.X)

        # Offset value
        self.offsetValue = tk.StringVar()
        self.offsetValue.set("0")
        self.offSetEntry = ttk.Entry(
            self.offsetFrame, textvariable=self.offsetValue, width=10,
        )
        self.offSetEntry.pack(side=tk.LEFT, fill=X, expand=True)
        # Go to offset button
        self.goToOffsetButton = ttk.Button(
            self.offsetFrame, text="Go to offset", command=self.LoadAudioOffset
        )
        self.goToOffsetButton.pack(side=tk.LEFT)

        # Audio progress bar
        self.audioProgressBar = ttk.Scale(
            self, from_=0, to=1, orient=tk.HORIZONTAL,
            command=self.SetAudioPosition
        )
        self.audioProgressBar.pack(side=tk.BOTTOM, fill=tk.X)

        toolBarFrame = tk.Frame(self)
        toolBarFrame.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)

        self.fftToolbar = NavigationToolbar2Tk(self.fftCanvas, toolBarFrame)
        self.fftToolbar.update()

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
        self.fftContrastCurveCanvas = FigureCanvasTkAgg(
            self.fftContrastCurveFig, spectrogramControlFrame)
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
            onUpdateLabelHighlight=self.UpdateLabelHighlight,
            master=self.leftFrame
        )
        self.dataSetLabelInspector.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

    def DrawRightFrame(self):
        """
        Method to draw the right frame.
        """

        self.fftInspector = FFTDetailInspector(
            onAddToCurrLabelGroup=self.AddToCurrLabelGroup,
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

    def MenuBar(self):
        """
        Method to create the menu bar
        """
        self.menuBar = tk.Menu(self.master)
        fileMenu = tk.Menu(self.menuBar, tearoff=0)
        playMenu = tk.Menu(self.menuBar, tearoff=0)
        spectrogramMenu = tk.Menu(self.menuBar, tearoff=0)

        # File menu
        if platform.system() == "Darwin":
            fileMenu.add_command(label="Open (Cmd + O)",
                                 command=self.SelectFile)
            self.master.bind("<Command-o>", self.SelectFile)
        elif platform.system() == "Windows":
            fileMenu.add_command(label="Open (Ctrl + O)",
                                 command=self.SelectFile)
            self.master.bind("<Control-o>", self.SelectFile)

        if platform.system() == "Darwin":
            fileMenu.add_checkbutton(
                label="Save Label File (Cmd + S)", command=self.dataSetLabelInspector.SaveLabels)
            self.master.bind(
                "<Command-s>", self.dataSetLabelInspector.SaveLabels)
        elif platform.system() == "Windows":
            fileMenu.add_checkbutton(
                label="Save Label File (Ctrl + S)", command=self.dataSetLabelInspector.SaveLabels)
            self.master.bind(
                "<Control-s>", self.dataSetLabelInspector.SaveLabels)

        # Play menu
        if platform.system() == "Darwin":
            playMenu.add_command(label="Play (Cmd + P)", command=self.Play)
            self.master.bind("<Command-p>", self.Play)
        elif platform.system() == "Windows":
            playMenu.add_command(label="Play (Ctrl + P)", command=self.Play)
            self.master.bind("<Control-p>", self.Play)

        if platform.system() == "Darwin":
            playMenu.add_command(
                label="Pause (Cmd + Shift + P)", command=self.Pause)
            self.master.bind("<Command-P>", self.Pause)
        elif platform.system() == "Windows":
            playMenu.add_command(
                label="Pause (Ctrl + Shift + P)", command=self.Pause)
            self.master.bind("<Control-P>", self.Pause)

        # Spectrogram menu
        if platform.system() == "Darwin":
            spectrogramMenu.add_command(
                label="Label Spectrogram (Cmd + L)", command=self.AddToCurrLabelGroup)
            self.master.bind("<Command-l>", self.AddToCurrLabelGroup)
        elif platform.system() == "Windows":
            spectrogramMenu.add_command(
                label="Label Spectrogram (Ctrl + L)", command=self.AddToCurrLabelGroup)
            self.master.bind("<Control-l>", self.AddToCurrLabelGroup)

        self.menuBar.add_cascade(label="File", menu=fileMenu)
        self.menuBar.add_cascade(label="Play", menu=playMenu)
        self.menuBar.add_cascade(label="Spectrogram", menu=spectrogramMenu)

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
        loadFileThread = threading.Thread(
            target=self.SelectFileThread, args=(selectedFileName,))
        loadFileThread.start()

    def SelectFileThread(self, selectedFileName):
        """
        Helper method to select a file
        """
        # Check selected file name is not empty
        if selectedFileName == "":
            print("No file selected")
            return

        # Set the status to loading
        self.status.set("Status: Loading...")

        # Load audio file
        self.rootAudio.LoadAudio(selectedFileName)
        print("Loaded audio file")
        print("Audio length (s): " + str(self.rootAudio.audioLength))
        print("Audio length (frame): " + str(len(self.rootAudio.audioArray)))
        print("Audio sample rate: " + str(self.rootAudio.sampleRate))

        # TODO: Get current offset.
        self.currOffset = 0
        self.LoadAudioOffsetThread()

        # Set the status to ready
        self.status.set("Status: Ready")

    def LoadAudioOffset(self):
        # Pause the audio
        self.Pause()

        # Start a thread to load the audio offset
        loadAudioOffsetThread = threading.Thread(
            target=self.LoadAudioOffsetThread)
        loadAudioOffsetThread.start()

    def LoadAudioOffsetThread(self):
        # If root audio is not loaded, return
        if self.rootAudio.audioArray is None:
            messagebox.showerror("Error", "No audio file loaded")
            return

        # Set the status to loading
        self.status.set("Status: Slicing audio...")

        # Get offsetValue
        try:
            self.currOffset = float(self.offsetValue.get())
        except ValueError:
            messagebox.showerror("Error", "Offset value is not a number")
            # Set the status to ready
            self.status.set("Status: Ready")
            return
        # Get current audio frame
        offsetFrame = int(self.currOffset * self.rootAudio.sampleRate)
        # Min offsetFrame is 0
        if offsetFrame < 0:
            offsetFrame = 0
        # Max offsetFrame is the length of the audio file
        if offsetFrame > len(self.rootAudio.audioArray) - MIN_AUDIO_LENGTH * self.rootAudio.sampleRate:
            offsetFrame = int(len(self.rootAudio.audioArray) -
                              MIN_AUDIO_LENGTH * self.rootAudio.sampleRate)
        self.currOffset = offsetFrame / self.rootAudio.sampleRate
        # Set the offset value in the label
        self.offsetValue.set(self.currOffset)
        # frames in the window
        windowFrame = MAX_AUDIO_LENGTH * self.rootAudio.sampleRate
        # Get current window frames
        if offsetFrame + windowFrame > len(self.rootAudio.audioArray):
            windowFrame = len(self.rootAudio.audioArray) - offsetFrame
        # Load main audio with offset
        self.mainAudio.LoadAudioArray(
            self.rootAudio.audioArray[offsetFrame:offsetFrame+windowFrame],
            self.rootAudio.sampleRate
        )

        # Set up audio player
        self.mainAudioPlayer = AudioPlayer(
            self.mainAudio,
            0.2,
            self.UpdateAudioCursor
        )

        # Plot audio file
        self.audioMagnitudePlot.Plot()
        self.audioSpectrumPlot.Plot(keepLim=False)

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

    def SetAudioPosition(self, value):
        """
        Set the audio position
        """
        if self.mainAudioPlayer is None:
            return

        # Set the audio position only if not playing
        if not self.mainAudioPlayer.isPlaying:
            # Set the audio position
            self.mainAudioPlayer.SetAudioPosition(float(value))
            # Update the audio cursor
            self.audioMagnitudePlot.SetCursorPosition(
                float(value) * self.mainAudio.audioLength)

    def UpdateAudioCursor(self, value):
        """
        Method to update the audio cursor
        """
        self.audioMagnitudePlot.SetCursorPosition(value)
        self.audioProgressBar.set(value/self.mainAudio.audioLength)

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

        # Check if xSpan is out of bounds
        if xSpan[0] < 0 or xSpan[1] > self.mainAudio.fftSpectrum.shape[1]:
            print("Invalid coordinates")
            return

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

        freqArr = librosa.fft_frequencies(
            sr=self.mainAudio.sampleRate, n_fft=self.mainAudio.nFft)
        self.fftInspector.SetFFTDetail(
            xSpan[0] / self.mainAudio.fftSpectrum.shape[1] *
            self.mainAudio.audioLength,
            xSpan[1] / self.mainAudio.fftSpectrum.shape[1] *
            self.mainAudio.audioLength,
            freqArr[int(ySpan[0])],
            freqArr[int(ySpan[1])]
        )

        self.fftInspector.fftDetailAudio.ReconstructAudio(
            self.mainAudio.sampleRate,
            slicedSpectrum,
            self.mainAudio.fftSpectrum.shape[0],
            ySpan
        )

        self.fftInspector.fftDetailAudioPlayer.Play()

    def AddToCurrLabelGroup(self, event=None):
        # Check current selected group is not None
        if self.dataSetLabelInspector.selectedGroup is None:
            messagebox.showerror("Error", "No group selected")
            return

        # Add the fft detail to the current label group
        self.dataSetLabelInspector.selectedGroup.AddDataSetLabel(
            DataSetLabel(
                self.dataSetLabelInspector.selectedGroup.groupName,
                self.fftInspector.startTime + self.currOffset,
                self.fftInspector.endTime + self.currOffset,
                self.fftInspector.startFreq,
                self.fftInspector.endFreq
            )
        )

        # Update the label inspector
        self.dataSetLabelInspector.UpdateGroupLabels()

    def UpdateLabelHighlight(self, selectedLabels: list[DataSetLabel]):
        """
        Method to update the label highlight
        """
        # Deep copy the selected labels
        selectedLabelsOffset = [
            selectedLabel.OffsetCopy(0-self.currOffset) for selectedLabel in selectedLabels
        ]

        self.audioSpectrumPlot.UpdateHighlightedLabels(selectedLabelsOffset)

        # Check if the selected label is valid
        if selectedLabelsOffset is None or len(selectedLabels) == 0:
            return

        # Check if the length of the selected label > 1
        if len(selectedLabelsOffset) > 1:
            print("Multiple labels selected")
            return

        # Get the start and end time and frequency
        currLabel = selectedLabelsOffset[0]
        freqArr = librosa.fft_frequencies(
            sr=self.mainAudio.sampleRate, n_fft=self.mainAudio.nFft)

        # Get the start and end of x
        xStart = currLabel.startTime / self.mainAudio.audioLength * \
            self.mainAudio.fftSpectrum.shape[1]
        xEnd = currLabel.endTime / self.mainAudio.audioLength * \
            self.mainAudio.fftSpectrum.shape[1]
        # Get the first frequency index in freqArr >= label.startFreq
        yStart = np.argmax(freqArr >= currLabel.startFreq)
        yEnd = np.argmax(freqArr >= currLabel.endFreq)

        # Update the fft detail inspector
        self.SpectrumSelected((xStart, yStart), (xEnd, yEnd))

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
dataSetGenerator.master.title("Spectrum Labeling Toolset")
dataSetGenerator.master.minsize(width=1200, height=600)
dataSetGenerator.master.geometry("1200x600")
dataSetGenerator.master.configure(menu=dataSetGenerator.menuBar)

# start the program
dataSetGenerator.mainloop()
