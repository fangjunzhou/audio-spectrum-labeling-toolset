from tkinter import *
import tkinter as tk
from tkinter import ttk, messagebox

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
    
    def __str__(self) -> str:
        return "{0:.2f}s->{1:.2f}s:{2:.2f}Hz->{3:.2f}Hz".format(
            self.startTime,
            self.endTime,
            self.startFreq,
            self.endFreq,
        )

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
        master: tk.Frame = None
    ) -> None:
        super().__init__(master)
        
        # -----INITIALIZE-----
        self.dataSetLabelGroups: list[DataSetLabelGroup] = []
        
        # -----RENDER-----
        # Create canvas for spectrum frame
        self.labelGroupCanvas = Canvas(master, takefocus=0)
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
            command=self.OnSelectGroup
        )
        self.groupOptions.pack(side=tk.TOP, fill=tk.X)
        
        # Name of the new group
        self.newGroupName = tk.StringVar()
        self.newGroupName.set("Group 1")
        newGroupEntry = ttk.Entry(frameScrollable, textvariable=self.newGroupName)
        newGroupEntry.pack(side=tk.TOP, fill=tk.X)
        
        # Button to add a new group
        addGroupButton = ttk.Button(frameScrollable, text="Add Group", command=self.AddGroup)
        addGroupButton.pack(side=tk.TOP, fill=tk.X)
        
        # Button to delete current group
        deleteGroupButton = ttk.Button(frameScrollable, text="Delete Group", command=self.DeleteGroup)
        deleteGroupButton.pack(side=tk.TOP, fill=tk.X)
        
        # List of current group labels
        self.currGroupLabels = tk.Listbox(frameScrollable, selectmode=tk.EXTENDED)
        self.currGroupLabels.pack(side=tk.TOP, fill=tk.X)
        self.currGroupLabels.bind("<<ListboxSelect>>", self.OnLabelSelected)
    
    def FrameWidth(self, event):
        canvas_width = event.width
        self.labelGroupCanvas.itemconfig(self.canvasFrame, width = canvas_width)

    def OnFrameConfigure(self, event):
        self.labelGroupCanvas.configure(scrollregion=self.labelGroupCanvas.bbox("all"))
    
    def UpdateGroupOptions(self) -> None:
        """
        Update the group options.
        """
        availableGroupNames = self.GetDataSetLabelGroupNames()
        self.groupOptions["menu"].delete(0, "end")
        for groupName in availableGroupNames:
            self.groupOptions["menu"].add_command(
                label=groupName,
                command=lambda groupName=groupName: self.OnSelectGroup(groupName)
            )
        # Check if the selected group is still available
        if self.selectedGroupName.get() not in availableGroupNames:
            self.OnSelectGroup(availableGroupNames[0])
    
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
        self.selectedGroupName.set(groupName)
        
        # Update the selected group
        self.selectedGroup = None
        for group in self.dataSetLabelGroups:
            if group.groupName == groupName:
                self.selectedGroup = group
                break
        
        if self.selectedGroup is None:
            # Clear label list display.
            self.currGroupLabels.delete(0, "end")
            return
        
        # Update label list in the group.
        self.UpdateGroupLabels()
    
    def AddGroup(self) -> None:
        """
        Add a new group to the group list.
        """
        # Get the name of the new group
        newGroupName = self.newGroupName.get()
        # Check if the name is valid
        if newGroupName == "":
            messagebox.showerror("Error", "Group name cannot be empty.")
            return
        if newGroupName in self.GetDataSetLabelGroupNames():
            messagebox.showerror("Error", "Group name already exists.")
            return
        
        group = DataSetLabelGroup(newGroupName)
        self.dataSetLabelGroups.append(group)
        self.UpdateGroupOptions()
        self.OnSelectGroup(newGroupName)
        
        # Clear the new group name entry
        # Find an available group name
        for i in range(1, 100):
            groupName = "Group " + str(i)
            if groupName not in self.GetDataSetLabelGroupNames():
                self.newGroupName.set(groupName)
                return
        self.newGroupName.set("")
    
    def DeleteGroup(self) -> None:
        """
        Delete the current group.
        """
        # Double check that the user wants to delete the group
        if not messagebox.askyesno("Delete Group", "Are you sure you want to delete the current group?"):
            return
        
        if self.selectedGroup is None:
            messagebox.showerror("Delete Group", "No group selected.")
            return
        
        self.dataSetLabelGroups.remove(self.selectedGroup)
        self.UpdateGroupOptions()
        self.OnSelectGroup(self.GetDataSetLabelGroupNames()[0])
    
    def UpdateGroupLabels(self) -> None:
        """
        Update the group labels.
        """
        if self.selectedGroup is None:
            return
        
        # Get all the labels in current group
        currLabels = self.selectedGroup.dataSetLabels
        currLabelTexts = [str(label) for label in currLabels]
        # Set the labels in the listbox
        self.currGroupLabels.delete(0, "end")
        for label in currLabelTexts:
            self.currGroupLabels.insert(tk.END, label)
    
    def OnLabelSelected(self, event) -> None:
        """
        Select a label.
        """
        # Get the selected index
        indx = self.currGroupLabels.curselection()
        print(f"Selected index: {indx}")