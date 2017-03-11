#!/usr/bin/env python3

import os
from tkinter import *
from tkinter.ttk import *
from tkinter import messagebox
from tkinter import filedialog
sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
import timechange

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
    def defaultProject(self):
        self.parent.tc = timechange.TimeChange()
        projectDir = os.path.join(os.path.expanduser('~'), 'timechange', 'default')
        self.parent.loadProject(projectDir)

    def loadProject(self):
        projectDir = filedialog.askdirectory(initialdir=os.path.expanduser("~"))
        dirname = os.path.dirname(os.path.realpath(projectDir))
        basename = os.path.basename(os.path.realpath(projectDir))
        try:
            self.parent.tc = timechange.TimeChange(project_name=basename, parent_folder=dirname)
            self.parent.loadProject(projectDir)
        except:
            messagebox.showerror("Error", "%s is an invalid project directory" % projectDir)

    def __init__(self, parent):
        Frame.__init__(self, parent)
        self.parent = parent
        self.DEFAULTBUTTON = Button(self)
        self.DEFAULTBUTTON["text"] = "Default Project"
        self.DEFAULTBUTTON["command"] = self.defaultProject
        self.DEFAULTBUTTON.pack()
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
        selectedItems = self.IMPORTFILES.selection()
        for selectedItem in selectedItems:
            self.IMPORTFILES.set(selectedItem, column="Label", value=self.LABEL.get())

    def addFiles(self):
        for item in self.IMPORTFILES.get_children():
            file = self.IMPORTFILES.item(item)["text"]
            label = self.IMPORTFILES.item(item)["values"][0]
            fullpath = self.IMPORTFILES.item(item)["values"][1]
            self.parent.tc.add_training_file(label, fullpath)
        self.parent.updateExistingFiles()

    def __init__(self, parent):
        Frame.__init__(self, parent)
        self.parent = parent
        self.LABELLBL = Label(self)
        self.LABELLBL["text"] = "                                            Instructions: \n" \
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
        self.selectedDataColumns = []
        for key in checkBoxState:
           if checkBoxState[key] == 0:
                self.selectedDataColumns.append(key)
        self.parent.tc.columns=self.selectedDataColumns
        self.parent.tc.convert_all_csv()

    def refresh(self):
        self.HEADERS.pack_forget()
        self.HEADERS = CheckBoxSet(self, self.parent.dataColumns)
        self.HEADERS.pack()

    def __init__(self, parent):
        Frame.__init__(self, parent)
        self.parent = parent
        self.LBL = Label(self)
        self.LBL["text"] =  "                                      Instructions\n" \
                            "\n" \
                            "Select any columns you wish to exclude from the fourier transform.\n" \
                            "Any columns that are not castable to a number will result in a crash.\n" \
                            "Hint: make sure to exclude timestamps\n"
        self.LBL.pack()
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
        self.LBL = Label(self)
        self.LBL["text"] = "FFT Previews go here. Work in Progress..."
        self.LBL.pack()
        self.pack()

class ConfigureScreen(Frame):
    def save(self):
        print(self.parent.configFile)
        fh = open(self.parent.configFile, 'w')
        fh.write(self.CONFIG.get("1.0",END))
        fh.close()
        self.SAVEBUTTON.config(state=DISABLED)

    def setDirty(self, event):
        self.dirty = True
        self.SAVEBUTTON.config(state=NORMAL)

    def __init__(self, parent):
        Frame.__init__(self, parent)
        self.parent = parent
        self.dirty = False
        self.parent.configFile = os.path.join(self.parent.projectPath, "timechange.cfg")
        if not os.path.isfile(self.parent.configFile):
            open(self.parent.configFile, 'a').close()
        self.CONFIG = Text(self)
        fh = open(self.parent.configFile, 'r')
        cfg = fh.read()
        self.CONFIG.insert(END, cfg)
        fh.close()
        self.CONFIG.pack()
        self.SAVEBUTTON = Button(self)
        self.SAVEBUTTON["text"] = "Save"
        self.SAVEBUTTON["command"] = self.save
        self.SAVEBUTTON.config(state=DISABLED)
        self.SAVEBUTTON.pack()
        self.CONFIG.bind("<<Modified>>", self.setDirty)
        self.pack()

class ResultsScreen(Frame):
    def __init__(self, parent):
        Frame.__init__(self, parent)
        self.LBL = Label(self)
        self.LBL["text"] = "Results go here. Work in Progress..."
        self.LBL.pack()
        self.parent = parent
        self.pack()

class ProjectHomeScreen(Frame):
    def __init__(self, parent):
        Frame.__init__(self, parent)
        self.LBL = Label(self)
        self.LBL["text"] =  "                              Welcome to TimeChange\n" \
                            "\n" \
                            "This project allows users to easily convert timeseries csv formatted\n" \
                            "data into fourier transform images and classify them using existing\n" \
                            "machine learning libraries without a deep knowledge of those tools.\n" \
                            "\n" \
                            "Begin starting with the next tab to load and label your csv files."

        self.LBL.pack()
        self.parent = parent
        self.pack()

class Application(Frame):
    def updateExistingFiles(self):
        self.csvDir = os.path.join(self.projectPath, "csv")
        if not os.path.isdir(self.csvDir):
            os.mkdir(self.csvDir)
        self.labels = os.listdir(self.csvDir)
        for label in self.labels:
            self.files = os.listdir(os.path.join(self.csvDir, label))
            self.dataColumns = []
            for file in self.files:
                csvFile = os.path.join(self.csvDir, label, file)
                if not self.dataColumns:
                    self.dataColumns = self.tc.get_csv_columns(csvFile)
                else:
                    nextDataColumns = self.tc.get_csv_columns(csvFile)
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
        self.PickHeadersScreen.refresh()

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
