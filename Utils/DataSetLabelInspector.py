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
        
        self.selectedGroup: DataSetLabelGroup = None
        self.selectedLabel: DataSetLabel = None
        
        # -----RENDER-----
        # Title
        title = ttk.Label(master, text="Data Set Label Inspector")
        title.pack(side=TOP)
        
        # Drop down menu to select a group
        self.selectedGroupName = tk.StringVar()
        availableGroupNames = self.GetDataSetLabelGroupNames()
        self.selectedGroupName.set(availableGroupNames[0])
        self.groupOptions = ttk.OptionMenu(
            master,
            self.selectedGroupName,
            availableGroupNames,
            command=self.OnSelectGroup
        )
        self.groupOptions.pack(side=tk.TOP, fill=tk.X)
        
        # Name of the new group
        self.newGroupName = tk.StringVar()
        self.newGroupName.set("Group 1")
        newGroupEntry = ttk.Entry(master, textvariable=self.newGroupName)
        newGroupEntry.pack(side=tk.TOP, fill=tk.X)
        
        # Button to add a new group
        addGroupButton = ttk.Button(master, text="Add Group", command=self.AddGroup)
        addGroupButton.pack(side=tk.TOP, fill=tk.X)
        
        # Button to delete current group
        deleteGroupButton = ttk.Button(master, text="Delete Group", command=self.DeleteGroup)
        deleteGroupButton.pack(side=tk.TOP, fill=tk.X)
        
        # Remove selected label button
        removeSelectedLabelButton = ttk.Button(master, text="Remove Selected Label", command=self.RemoveSelectedLabel)
        removeSelectedLabelButton.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Add a scrollbar to the canvas
        labelListScrollbar = ttk.Scrollbar(master, orient=tk.VERTICAL)
        labelListScrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # List of current group labels
        self.currGroupLabels = tk.Listbox(master, selectmode=tk.EXTENDED, yscrollcommand=labelListScrollbar.set)
        self.currGroupLabels.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.currGroupLabels.bind("<<ListboxSelect>>", self.OnLabelSelected)

    def OnFrameConfigure(self, event):
        self.labelListCanvas.configure(scrollregion=self.labelListCanvas.bbox("all"))
    
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
        self.selectedLabel = None
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
        indx = self.currGroupLabels.curselection()[0]
        # Select the label in the label list
        self.selectedLabel = self.selectedGroup.dataSetLabels[indx]
        
        print(f"Selected label: {str(self.selectedLabel)}")
    
    def RemoveSelectedLabel(self) -> None:
        """
        Remove the selected label.
        """
        # Check if a label is valid
        if self.selectedLabel is None:
            messagebox.showerror("Error", "No label selected.")
            return
        
        # Remove the selected label from the group
        print(f"Removing label: {str(self.selectedLabel)}")
        self.selectedGroup.dataSetLabels.remove(self.selectedLabel)
        
        # Update the label list
        self.UpdateGroupLabels()
        # Set the selected label to None
        self.selectedLabel = None
        
        print("Label removed.")