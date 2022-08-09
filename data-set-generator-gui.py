from curses.panel import bottom_panel
import os

from matplotlib import pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk

import tkinter as tk
from tkinter import *
from tkinter import ttk
from tkinter import filedialog


class App(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.pack(fill=BOTH, expand=True)

        # =====INITIALIZE=====

        # Status text
        self.status = tk.StringVar()
        self.status.set("Status: Ready")
        # Loading status
        self.loadingStatus = False

        # Matplotlib figure
        self.fig, self.ax = plt.subplots()

        # =====FRAMES=====

        # Top frame for file selection
        topFrame = tk.Frame(self)
        topFrame.pack(side=TOP, fill=X)

        # Bottom frame for play control
        bottomFrame = tk.Frame(self)
        bottomFrame.pack(side=BOTTOM, fill=X)

        # Left frame for tools
        leftFrame = tk.Frame(self)
        leftFrame.pack(side=LEFT)

        # =====TOP FRAME=====

        # Create a label and button for file selection
        self.openFileName = tk.StringVar()
        self.openFileName.set("Select a file")

        fileNameLabel = tk.Label(topFrame, textvariable=self.openFileName)
        fileNameLabel.pack(side=tk.LEFT, expand=True)
        selectFileButton = tk.Button(
            topFrame, text="Select a file", command=self.selectFile)
        selectFileButton.pack(side=tk.LEFT)

        # =====LEFT FRAME=====

        # =====MAIN FRAME=====

        canvas = FigureCanvasTkAgg(self.fig, self)
        canvas.draw()

        canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        # =====BOTTOM FRAME=====

        toolbarFrame = tk.Frame(bottomFrame)
        toolbarFrame.pack(side=TOP)
        toolbar = NavigationToolbar2Tk(canvas, toolbarFrame)
        toolbar.update()

        # Status bar
        statusBar = tk.Label(bottomFrame, textvariable=self.status)
        statusBar.pack(side=BOTTOM, anchor=W)

    def selectFile(self):
        # Get current working directory
        currDir = os.getcwd()
        # Open a file dialog and set the file name in the label
        selectedFileName = filedialog.askopenfilename(initialdir=currDir, title="Select a file",
                                                      filetypes=(
                                                          ("wav files", "*.wav"),
                                                          ("all files", "*.*")
                                                      ))
        self.openFileName.set(selectedFileName)

        # TODO: Load audio file


# create the application
dataSetGenerator = App()
# here are method calls to the window manager class
dataSetGenerator.master.title("Audio Data Set Generator")
dataSetGenerator.master.minsize(width=400, height=200)

# start the program
dataSetGenerator.mainloop()
