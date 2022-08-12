from tkinter import *
import tkinter as tk
from tkinter import ttk, messagebox

from Utils.DataSetLabel import DataSetLabel
from Utils.AudioPlot import AudioSpectrumPlot

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
        spectrogramPlot: AudioSpectrumPlot,
        master: tk.Frame = None
    ) -> None:
        super().__init__(master)
        
        # -----INITIALIZE-----
        self.dataSetLabelGroups: list[DataSetLabelGroup] = []
        
        self.selectedGroup: DataSetLabelGroup = None
        self.selectedLabels: list[DataSetLabel] = []
        
        self.spectrogramPlot = spectrogramPlot
        
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
        self.selectedLabels = []
        self.UpdateLabelHighlight()
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
        # Check if group is selected
        if self.selectedGroup is None:
            return
        
        # Get the selected index
        indx = self.currGroupLabels.curselection()
        # Select the label in the label list
        self.selectedLabels = self.selectedGroup.dataSetLabels[indx[0]:indx[-1] + 1]
        self.UpdateLabelHighlight()
        
        print(f"{indx[-1] - indx[0] + 1} labels selected.")
    
    def RemoveSelectedLabel(self) -> None:
        """
        Remove the selected label.
        """
        # Check if a label is valid
        if len(self.selectedLabels) == 0:
            messagebox.showerror("Error", "No label selected.")
            return
        
        if len(self.selectedLabels) > 1 and not messagebox.askyesno("Remove Multiple Labels", "Are you sure you want to remove all the selected labels?"):
            # Remove the label from the group
            self.selectedGroup.dataSetLabels.remove(self.selectedLabels[0])
        
        for label in self.selectedLabels:
            # Remove the selected label from the group
            print(f"Removing label: {str(label)}")
            self.selectedGroup.dataSetLabels.remove(label)
        
        # Update the label list
        self.UpdateGroupLabels()
        # Set the selected label to None
        self.selectedLabels = []
        self.UpdateLabelHighlight()
        
        print("Label removed.")
    
    def UpdateLabelHighlight(self) -> None:
        """
        Update the label highlight.
        """
        self.spectrogramPlot.UpdateHighlightedLabels(self.selectedLabels)