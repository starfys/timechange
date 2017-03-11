#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
from tkinter import *
from tkinter.ttk import *
from tkinter import messagebox
from tkinter import filedialog
import configparser

import timechange
from PIL import Image

tc = timechange.TimeChange()

class CheckBoxSet(Frame):
    def __init__(self, parent, picks=[], side=LEFT, anchor=W):
        Frame.__init__(self, parent)
        self.parent = parent
        self.vars = []
        self.items = {}
        for pick in picks:
            var = IntVar()
            chkbox = Checkbutton(self, text=pick, variable=var)
            chkbox.pack()
            self.items[pick] = var
    def state(self):
        return self.items

class WelcomeScreen(Frame):
    def createProject(selfs):
        messagebox.showerror("Error", "Creating new projects not implemented yet")

    def loadProject(self):
        projectDir = filedialog.askdirectory(initialdir=os.path.expanduser("~"))
        configFile = os.path.join(projectDir, "timechange.cfg")
        if os.path.isfile(configFile):
            self.parent.loadProject(projectDir)
        else:
            messagebox.showerror("Error", "%s is an invalid project directory" % projectDir)

    def __init__(self, parent):
        Frame.__init__(self, parent)
        self.parent = parent
        self.CREATENEWBUTTON = Button(self)
        self.CREATENEWBUTTON["text"] = "Create New Project"
        self.CREATENEWBUTTON["command"] = self.createProject
        self.CREATENEWBUTTON.pack()
        self.LOADEXISTINGBUTTON = Button(self)
        self.LOADEXISTINGBUTTON["text"] = "Load Existing Project"
        self.LOADEXISTINGBUTTON["command"] = self.loadProject
        self.LOADEXISTINGBUTTON.pack()
        self.pack()

class LoadFilesScreen(Frame):
    def importFiles(self):
        self.importFiles = filedialog.askopenfilenames(filetypes=[("Comma Seperated Values","*.csv")])
        for importFile in self.importFiles:
            basename = os.path.basename(importFile)
            self.IMPORTFILES.insert("", "end", text=basename, values=("", importFile))

    def selectTreeRow(self, event):
        #messagebox.showerror("Error", "Editing labels not implemented yet")
        selectedItems = self.IMPORTFILES.selection()
        for selectedItem in selectedItems:
            self.IMPORTFILES.set(selectedItem, column="Label", value=self.LABEL.get())

    def addFiles(self):
        for item in self.IMPORTFILES.get_children():
            file = self.IMPORTFILES.item(item)["text"]
            label = self.IMPORTFILES.item(item)["values"][0]
            fullpath = self.IMPORTFILES.item(item)["values"][1]
            tc.add_training_file(label, fullpath)
        self.parent.updateExistingFiles()


    def __init__(self, parent):
        Frame.__init__(self, parent)
        self.parent = parent

        self.LABELLBL = Label(self)
        self.LABELLBL["text"] = "Instructions: \n" \
                                "Step 1) Click the \"Select Files\" button to select files from the filesystem\n" \
                                "Step 2) Type a label into the following text box\n" \
                                "Step 3) Click the files you want to apply this label to\n" \
                                "Step 4) Repeat steps 2 and 3 until all files are labeled\n" \
                                "Step 5) Click \"Add to Project\" button to add these labeled files to the project"
        self.LABELLBL.pack()
        self.LABEL = Entry(self)
        self.LABEL.pack()

        self.IMPORTFILESBUTTON = Button(self)
        self.IMPORTFILESBUTTON["text"] = "Select Files"
        self.IMPORTFILESBUTTON["command"] = self.importFiles
        self.IMPORTFILESBUTTON.pack()

        self.IMPORTFILES = Treeview(self, columns=('Label', 'fullpath'))
        self.IMPORTFILES.heading('#0', text='File')
        self.IMPORTFILES.heading('#1', text='Label')
        self.IMPORTFILES.heading('#2', text='fullpath')
        self.IMPORTFILES.column('#0', stretch=YES)
        self.IMPORTFILES.column('#1', stretch=YES)
        self.IMPORTFILES.column('#2', stretch=YES)
        self.IMPORTFILES.bind("<<TreeviewSelect>>", self.selectTreeRow)
        self.IMPORTFILES["displaycolumns"] = ("Label")

        self.IMPORTFILES.pack()

        self.ADDBUTTON = Button(self)
        self.ADDBUTTON["text"] = "Add to Project"
        self.ADDBUTTON["command"] = self.addFiles
        self.ADDBUTTON.pack()


        self.pack()

class PickHeaders(Frame):
    def genFFT(self):
        checkBoxState = self.HEADERS.state()
        print(str(checkBoxState))

        self.selectedDataColumns = []
        for key in checkBoxState:
           if checkBoxState[key] == 0:
                self.selectedDataColumns.append(key)

        self.dataDir = os.path.join(self.parent.projectPath, "data")
        self.resultsDir = os.path.join(self.dataDir, "results")
        if not os.path.isdir(self.dataDir):
            os.mkdir(self.dataDir)
        if not os.path.isdir(self.resultsDir):
            os.mkdir(self.resultsDir)

        for file in self.files:
            file_path = os.path.join(self.csvDir, file)
            data = tc.read_csv(file_path, usecols=self.selectedDataColumns)
            features = tc.extract_features(data, data_size=1000)
            img = Image.fromarray(255 * features, 'L')
            img.save("{}/test{}.png".format(self.resultsDir, self.parent.first_file))

    def __init__(self, parent):
        Frame.__init__(self, parent)
        self.parent = parent
        self.HEADERS = CheckBoxSet(self, self.parent.dataColumns)
        self.HEADERS.pack()
        self.parent.updateExistingFiles()
        self.GENFFTBUTTON = Button(self)
        self.GENFFTBUTTON["text"] = "Generate FFT"
        self.GENFFTBUTTON["command"] = self.genFFT
        self.GENFFTBUTTON.pack()
        self.pack()



class FFTPreviewScreen(Frame):
    def __init__(self, parent):
        Frame.__init__(self, parent)
        self.parent = parent
        self.pack()

class ConfigureScreen(Frame):
    def __init__(self, parent):
        Frame.__init__(self, parent)
        self.parent = parent

        self.configFile = self.parent.projectPath

        self.CONFIG = Text(self)

        self.pack()

class ResultsScreen(Frame):
    def __init__(self, parent):
        Frame.__init__(self, parent)
        self.parent = parent
        self.pack()

class ProjectHomeScreen(Frame):
    def __init__(self, parent):
        Frame.__init__(self, parent)
        self.parent = parent
        self.pack()

class Application(Frame):
    def updateExistingFiles(self):
        self.csvDir = os.path.join(self.projectPath, "csv")
        if not os.path.isdir(self.csvDir):
            os.mkdir(self.csvDir)
        self.files = os.listdir(self.csvDir)
        self.dataColumns = []
        for file in self.files:
            #self.EXISTINGFILES.insert("", "end", text=file)
            if not self.dataColumns:
                self.dataColumns = tc.get_csv_columns(os.path.join(self.csvDir, file))
            else:
                nextDataColumns = tc.get_csv_columns(os.path.join(self.csvDir, file))
                if self.dataColumns != nextDataColumns:
                    messagebox.showerror("Error", "Csv headers are inconsistent!")
        self.selectedDataColumns = self.dataColumns

    def loadProject(self, projectPath):
        self.projectPath = projectPath
        self.WelcomeScreen.pack_forget()
        self.updateExistingFiles()
        self.notebook = Notebook(self)
        self.ProjectHomeScreen = ProjectHomeScreen(self)
        self.LoadFilesScreen = LoadFilesScreen(self)
        self.PickHeadersScreen = PickHeaders(self)
        self.FFTPreviewScreen = FFTPreviewScreen(self)
        self.ConfigureScreen = ConfigureScreen(self)
        self.ResultsScreen = ResultsScreen(self)
        self.notebook.add(self.ProjectHomeScreen, text="Home")
        self.notebook.add(self.LoadFilesScreen, text="Load Files")
        self.notebook.add(self.PickHeadersScreen, text="Pick Headers")
        self.notebook.add(self.FFTPreviewScreen, text="FFT Preview")
        self.notebook.add(self.ConfigureScreen, text="Configure Classifier")
        self.notebook.add(self.ResultsScreen, text="Results")
        self.notebook.pack()

    def __init__(self, master=None):
        Frame.__init__(self, master)

        self.WelcomeScreen = WelcomeScreen(self)
        self.WelcomeScreen.pack()

        self.dataColumns = []

        self.pack()

root = Tk()
app = Application(master=root)
app.mainloop()
try:
    root.destroy()
except:
    print("root frame already destroyed!")
