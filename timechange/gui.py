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

    def updateExistingFiles(self):
        self.csvDir = os.path.join(self.parent.projectPath, "csv")
        if not os.path.isdir(self.csvDir):
            os.mkdir(self.csvDir)
        self.files = os.listdir(self.csvDir)
        self.dataColumns = []
        for file in self.files:
            self.EXISTINGFILES.insert("", "end", text=file)
            if not self.dataColumns:
                self.dataColumns = tc.get_csv_columns(os.path.join(self.csvDir, file))
            else:
                nextDataColumns = tc.get_csv_columns(os.path.join(self.csvDir, file))
                if self.dataColumns != nextDataColumns:
                    messagebox.showerror("Error", "Csv headers are inconsistent!")
        self.selectedDataColumns = self.dataColumns
    def importFiles(self):
        messagebox.showerror("Error", "Importing files not implemented yet")

    def __init__(self, parent):
        Frame.__init__(self, parent)
        self.parent = parent
        self.EXISTINGFILES = Treeview(self)
        self.EXISTINGFILES.pack()
        self.updateExistingFiles()
        self.HEADERS = CheckBoxSet(self, self.dataColumns)
        self.HEADERS.pack()
        self.IMPORTFILESBUTTON = Button(self)
        self.IMPORTFILESBUTTON["text"] = "Import Files"
        self.IMPORTFILESBUTTON["command"] = self.importFiles
        self.IMPORTFILESBUTTON.pack()
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
    def loadProject(self, projectPath):
        self.projectPath = projectPath
        self.WelcomeScreen.pack_forget()
        self.notebook = Notebook(self)
        self.ProjectHomeScreen = ProjectHomeScreen(self)
        self.LoadFilesScreen = LoadFilesScreen(self)
        self.FFTPreviewScreen = FFTPreviewScreen(self)
        self.ConfigureScreen = ConfigureScreen(self)
        self.ResultsScreen = ResultsScreen(self)
        self.notebook.add(self.ProjectHomeScreen, text="Home")
        self.notebook.add(self.LoadFilesScreen, text="Load Files")
        self.notebook.add(self.FFTPreviewScreen, text="FFT Preview")
        self.notebook.add(self.ConfigureScreen, text="Configure Classifier")
        self.notebook.add(self.ResultsScreen, text="Results")
        self.notebook.pack()

    def __init__(self, master=None):
        Frame.__init__(self, master)

        self.WelcomeScreen = WelcomeScreen(self)
        self.WelcomeScreen.pack()


        self.pack()

root = Tk()
app = Application(master=root)
app.mainloop()
try:
    root.destroy()
except:
    print("root frame already destroyed!")
