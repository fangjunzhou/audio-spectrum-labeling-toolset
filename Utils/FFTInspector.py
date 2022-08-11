from tkinter import *
import tkinter as tk
from tkinter import ttk
from matplotlib import pyplot as plt

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from Utils.AudioProcess import Audio, AudioPlayer

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
    def __init__(self, rightFrame,  master = None) -> None:
        super().__init__(master)
        
        # FFT detail view
        self.fftDetailViewFig, self.fftDetailViewAx = plt.subplots()
        self.fftDetailViewFig.set_size_inches(4, 3)
        self.fftDetailViewFig.tight_layout()
        # FFT detail audio
        self.fftDetailAudio: Audio = Audio()
        self.fftDetailAudioPlayer: AudioPlayer = AudioPlayer(self.fftDetailAudio, 1)
        
        # Pack the fft detail canvas
        self.fftDetailCanvas = FigureCanvasTkAgg(self.fftDetailViewFig, rightFrame)
        self.fftDetailCanvas.draw()
        self.fftDetailCanvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=False)
        
        # Create canvas for spectrum frame
        rightCanvas = Canvas(rightFrame)
        rightCanvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Add a scrollbar to the canvas
        rightCanvasScrollbar = ttk.Scrollbar(rightFrame, orient=tk.VERTICAL, command=rightCanvas.yview)
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
        
        self.startTime = LabeledEntry(
            basicInfoFrame,
            0,
            "Start Time",
            initVal="0.0"
        )
        self.endTime = LabeledEntry(
            basicInfoFrame,
            1,
            "End Time",
            initVal="0.0"
        )
        self.startFreq = LabeledEntry(
            basicInfoFrame,
            2,
            "Start Freq",
            initVal = "0.0"
        )
        self.endFreq = LabeledEntry(
            basicInfoFrame,
            3,
            "End Freq",
            initVal = "0.0"
        )
        
        playFFTDetailButton = ttk.Button(
            rightFrameScrollable, text="Play Detail", command=self.PlayFFTDetail)
        playFFTDetailButton.pack(side=tk.TOP, fill=X)
        
    
    def PlayFFTDetail(self):
        """
        Play the fft detail
        """
        if self.fftDetailAudioPlayer is None:
            return
        
        # Play the audio file
        self.fftDetailAudioPlayer.Play()