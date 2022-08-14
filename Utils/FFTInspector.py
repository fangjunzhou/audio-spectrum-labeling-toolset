from tkinter import *
import tkinter as tk
from tkinter import ttk, messagebox
from matplotlib import pyplot as plt

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from Config import FIG_DPI

from Utils.AudioProcess import Audio, AudioPlayer
from Utils.DataSetLabelInspector import DataSetLabel, DataSetLabelsInspector

class LabeledEntry:
    """
    Labeled entry.
    """
    
    def __init__(self, parentFrame: ttk.Frame, row: int, label: str, initVal: str = "") -> None:
        label = ttk.Label(parentFrame, text = label)
        label.grid(row=row, column=0)
        self.textContent = tk.Text(parentFrame, state="disabled", height=1, width=44)
        self.textContent.configure(state="normal")
        self.textContent.insert(tk.END, initVal)
        self.textContent.configure(state="disabled")
        self.textContent.grid(row=row, column=1)
    
    def SetText(self, text: str) -> None:
        self.textContent.configure(state="normal")
        self.textContent.delete(1.0, tk.END)
        self.textContent.insert(tk.END, text)
        self.textContent.configure(state="disabled")
        

class FFTDetailInspector(tk.Frame):
    """
    Inspector to browse FFT Detials.
    """
    def __init__(self, labelInspector: DataSetLabelsInspector, master = None) -> None:
        super().__init__(master)
        
        self.labelInspector = labelInspector
        
        # FFT detail view
        self.fftDetailViewFig, self.fftDetailViewAx = plt.subplots()
        self.fftDetailViewFig.set_size_inches(4, 3)
        self.fftDetailViewFig.set_dpi(FIG_DPI)
        self.fftDetailViewFig.tight_layout()
        # FFT detail audio
        self.fftDetailAudio: Audio = Audio()
        self.fftDetailAudioPlayer: AudioPlayer = AudioPlayer(self.fftDetailAudio, 1)
        
        # Pack the fft detail canvas
        self.fftDetailCanvas = FigureCanvasTkAgg(self.fftDetailViewFig, master)
        self.fftDetailCanvas.draw()
        self.fftDetailCanvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=False)
        
        # Create canvas for spectrum frame
        rightCanvas = Canvas(master)
        rightCanvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Add a scrollbar to the canvas
        rightCanvasScrollbar = ttk.Scrollbar(master, orient=tk.VERTICAL, command=rightCanvas.yview)
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
        
        title = ttk.Label(rightFrameScrollable, text = "FFT Detail Inspector")
        title.pack(side=TOP)
        
        basicInfoFrame = ttk.Frame(rightFrameScrollable)
        basicInfoFrame.pack(side=TOP, fill=X)
        
        self.startTime: float = 0.0
        self.startTimeLabeledEntry = LabeledEntry(
            basicInfoFrame,
            0,
            "Start Time",
            initVal="0.0"
        )
        self.endTime: float = 0.0
        self.endTimeLabeledEntry = LabeledEntry(
            basicInfoFrame,
            1,
            "End Time",
            initVal="0.0"
        )
        self.startFreq: float = 0.0
        self.startFreqLabeledEntry = LabeledEntry(
            basicInfoFrame,
            2,
            "Start Freq",
            initVal = "0.0"
        )
        self.endFreq: float = 0.0
        self.endFreqLabeledEntry = LabeledEntry(
            basicInfoFrame,
            3,
            "End Freq",
            initVal = "0.0"
        )
        
        playFFTDetailButton = ttk.Button(
            rightFrameScrollable, text="Play Detail", command=self.PlayFFTDetail)
        playFFTDetailButton.pack(side=tk.TOP, fill=X)
        
        # Add to current label group
        addToCurrentLabelGroupButton = ttk.Button(
            rightFrameScrollable, text="Add to Current Label Group", command=self.AddToCurrentLabelGroup)
        addToCurrentLabelGroupButton.pack(side=tk.TOP, fill=X)
    
    def SetFFTDetail(self, startTime, endTime, startFreq, endFreq):
        """
        Set the detail of fft.
        """
        self.startTime = startTime
        self.startTimeLabeledEntry.SetText(str(startTime))
        self.endTime = endTime
        self.endTimeLabeledEntry.SetText(str(endTime))
        self.startFreq = startFreq
        self.startFreqLabeledEntry.SetText(str(startFreq))
        self.endFreq = endFreq
        self.endFreqLabeledEntry.SetText(str(endFreq))
    
    def PlayFFTDetail(self):
        """
        Play the fft detail
        """
        if self.fftDetailAudioPlayer is None:
            return
        
        # Play the audio file
        self.fftDetailAudioPlayer.Play()
        
    def AddToCurrentLabelGroup(self, event=None):
        """
        Add the fft detail to the current label group
        """
        # Check current selected group is not None
        if self.labelInspector.selectedGroup is None:
            messagebox.showerror("Error", "No group selected")
            return
        
        # Add the fft detail to the current label group
        self.labelInspector.selectedGroup.AddDataSetLabel(
            DataSetLabel(
                self.labelInspector.selectedGroup.groupName,
                self.startTime,
                self.endTime,
                self.startFreq,
                self.endFreq
            )
        )
        
        # Update the label inspector
        self.labelInspector.UpdateGroupLabels()