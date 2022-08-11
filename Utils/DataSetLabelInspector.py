from tkinter import *
import tkinter as tk
from tkinter import ttk

class DataSetLabel:
    """
    Data set label instance.
    """
    
    def __init__(
        self,
        groupName: str,
        startTime: float,
        endTime: float,
        startFreq: float,
        endFreq: float,
    ) -> None:
        self.groupName = groupName
        
        self.startTime: float = startTime
        self.endTime: float = endTime
        self.startFreq: float = startFreq
        self.endFreq: float = endFreq

class DataSetLabelGroup:
    """
    Group of data set labels.
    """
    
    def __init__(self, groupName: str) -> None:
        self.groupName = groupName
        
        self.dataSetLabels: list[DataSetLabel] = []
        
    def AddDataSetLabel(self, label: DataSetLabel) -> None:
        """
        Add a new data set label to the group.
        """
        self.dataSetLabels.append(label)

class DataSetLabelsInspector(tk.Frame):
    """
    Inspector to browse all data set labels
    """
    
    def __init__(
        self,
        dataSetLabelGroups: list[DataSetLabelGroup],
        master: tk.Frame = None
    ) -> None:
        super().__init__(master)
        
        # -----INITIALIZE-----
        self.dataSetLabelGroups: list[DataSetLabelGroup] = dataSetLabelGroups
        
        # -----RENDER-----
        # Create canvas for spectrum frame
        self.labelGroupCanvas = Canvas(master)
        self.labelGroupCanvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Add a scrollbar to the canvas
        labelGroupScrollbar = ttk.Scrollbar(master, orient=tk.VERTICAL, command=self.labelGroupCanvas.yview)
        labelGroupScrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Configure the canvas
        self.labelGroupCanvas.configure(yscrollcommand=labelGroupScrollbar.set)
        self.labelGroupCanvas.bind(
            '<Configure>',
            lambda e: self.labelGroupCanvas.configure(
                scrollregion=self.labelGroupCanvas.bbox('all')
            )
        )
        
        # Create scrollable frame for canvas
        frameScrollable = tk.Frame(self.labelGroupCanvas)
        # Add the frame to the canvas
        self.canvasFrame = self.labelGroupCanvas.create_window((0, 0), window=frameScrollable, anchor=tk.NW)
        # Expand the frame to fill the canvas
        frameScrollable.bind("<Configure>", self.OnFrameConfigure)
        self.labelGroupCanvas.bind('<Configure>', self.FrameWidth)
        
        # Title
        title = ttk.Label(frameScrollable, text="Data Set Label Inspector")
        title.pack(side=TOP)
        
        # Drop down menu to select a group
        self.selectedGroup: DataSetLabelGroup = None
        self.selectedGroupName = tk.StringVar()
        availableGroupNames = self.GetDataSetLabelGroupNames()
        self.selectedGroupName.set(availableGroupNames[0])
        self.groupOptions = ttk.OptionMenu(
            frameScrollable,
            self.selectedGroupName,
            availableGroupNames,
        )
        self.groupOptions.pack(side=tk.TOP, fill=tk.X)
    
    def FrameWidth(self, event):
        canvas_width = event.width
        self.labelGroupCanvas.itemconfig(self.canvasFrame, width = canvas_width)

    def OnFrameConfigure(self, event):
        self.labelGroupCanvas.configure(scrollregion=self.labelGroupCanvas.bbox("all"))
    
    def GetDataSetLabelGroupNames(self) -> list[str]:
        """
        Get the data set label groups.
        """
        defaultGroupName = "None"
        groupNames = [defaultGroupName]
        groupNames.extend([group.groupName for group in self.dataSetLabelGroups])
        return groupNames
    
    def OnSelectGroup(self, groupName: str) -> None:
        """
        Select a group.
        """
        # Update the selected group
        self.selectedGroup = None
        for group in self.dataSetLabelGroups:
            if group.groupName == groupName:
                self.selectedGroup = group
                break
        
        if self.selectedGroup is None:
            return
        
        self.selectedGroupName.set(groupName)
        
        # TODO: Update label list in the group.