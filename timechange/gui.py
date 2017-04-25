#!/usr/bin/env python3

import os
from tkinter import *
import time
from tkinter.ttk import *
from tkinter import _setit
from tkinter import messagebox
from tkinter import filedialog
sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
import timechange
from threading import *


class CheckBoxSet(Frame):
    def __init__(self, parent, picks=[], side=LEFT, anchor=W):
        Frame.__init__(self, parent)
        self.parent = parent
        self.vars = []
        self.boxes = {}
        self.items = {}
        for pick in picks:
            checkbox_var = IntVar()
            checkbox_var.set(1)
            checkbox = Checkbutton(self, text=pick, variable=checkbox_var)
            checkbox.pack()
            self.items[pick] = checkbox_var
            self.boxes[pick] = checkbox
    def update_choices(self, picks):
        """Changes the choices for the boxes
        Parameters
            picks -- List of strings representing the choices"""
        #Delete existing checkboxes
        for box in self.boxes.values():
            box.pack_forget()
            box.destroy()
        #Clear internal state
        self.vars=[]
        self.boxes = {}
        self.items = {}
        #Set checkboxes
        for pick in picks:
            checkbox_var = IntVar()
            checkbox_var.set(1)
            checkbox = Checkbutton(self, text=pick, variable=checkbox_var)
            checkbox.pack()
            self.items[pick] = checkbox_var
            self.boxes[pick] = checkbox

class WelcomeScreen(Frame):
    def defaultProject(self):
        try:
            self.parent.tc = timechange.TimeChange()
            self.parent.columns = self.parent.tc.get_csv_columns() 
            projectDir = os.path.join(os.path.expanduser('~'), 'timechange', 'default')
            self.parent.loadProject(projectDir)
            #Start event loop
            self.parent.handle_queue()
        except Exception as e:
            messagebox.showerror("Project Loading Error", str(e)) # Show error message

    def __init__(self, parent):
        Frame.__init__(self, parent)
        self.parent = parent
        self.DEFAULTBUTTON = Button(self)
        self.DEFAULTBUTTON["text"] = "Default Project"
        self.DEFAULTBUTTON["command"] = self.defaultProject
        self.DEFAULTBUTTON.pack()
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
            if label == "":
            	label = "unlabeled"
            fullpath = self.IMPORTFILES.item(item)["values"][1]
            self.parent.tc.add_training_file(label, fullpath)
        self.parent.columns = self.parent.tc.get_csv_columns()
        self.parent.TransformDataScreen.refresh()
        messagebox.showinfo("Success", "Successfully added files")
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
        self.IMPORTFILESFRAME = Frame(self)
        self.IMPORTFILES = Treeview(self.IMPORTFILESFRAME, columns=('Label', 'fullpath'))
        self.IMPORTFILES.heading('#0', text='File')
        self.IMPORTFILES.heading('#1', text='Label')
        self.IMPORTFILES.heading('#2', text='fullpath')
        self.IMPORTFILES.column('#0', stretch=YES)
        self.IMPORTFILES.column('#1', stretch=YES)
        self.IMPORTFILES.column('#2', stretch=YES)
        self.IMPORTFILES.bind("<<TreeviewSelect>>", self.selectTreeRow)
        self.IMPORTFILES["displaycolumns"] = ("Label")
        self.yscroll =Scrollbar(self.IMPORTFILESFRAME, orient=VERTICAL, command=self.IMPORTFILES.yview)
        self.IMPORTFILES.config(yscrollcommand = self.yscroll.set)
        self.IMPORTFILES.pack(side=LEFT)
        self.yscroll.pack(side=LEFT,fill=Y)
        self.IMPORTFILESFRAME.pack()
        self.ADDBUTTON = Button(self)
        self.ADDBUTTON["text"] = "Add to Project"
        self.ADDBUTTON["command"] = self.addFiles
        self.ADDBUTTON.pack()
        self.pack()
        
        
class PickHeaders(Frame):
    def transform_data(self):
        #Freeze transformation button
        
        #Get columns from data
        columns = []
        for column_name, state in self.column_boxes.items.items():
            if state.get() == 1:
                columns.append(column_name)
        self.parent.tc.set_columns(columns)
        #Set transform parameters
        try:
            self.parent.tc.set_transform_parameters(method = self.method.get(),
                                                    chunk_size = str(int(self.chunksize_entry.get())),
                                                    fft_size = str(int(self.fftsize_entry.get())))
        except Exception as exc:
            messagebox.showerror("Error", "Invalid transformation parameters")
            return
        #Initialize training
        self.parent.tc.convert_all_csv()
        self.parent.notebook.pack_forget()
        #Fix: some systems don't have wait cursor
        try:
            self.parent.config(cursor="wait")
        except:
            pass
        self.parent.notebook.pack()
    def refresh(self):
        self.column_boxes.update_choices(self.parent.tc.get_csv_columns())
        #Set up the boxes
        transform_defaults = self.parent.tc.get_transform_parameters()
        if transform_defaults["columns"] != "":
            for column in self.column_boxes.items:
                if column not in transform_defaults["columns"]:
                    self.column_boxes.items[column].set(0)
    def __init__(self, parent):
        Frame.__init__(self, parent)
        self.parent = parent
        #Instructions to user
        instruction_label = Label(self)
        instruction_label["text"] =  "                                      Instructions\n" \
                            "\n" \
                            "Set parameters for the data transformation here.\n" \
                            "Press \"Transform Data\" to start the data transformation"
        #Label for column list
        column_label = Label(self)
        column_label["text"] = "Columns to include"
        #List of columns
        self.column_boxes = CheckBoxSet(self, self.parent.columns)
        self.column_boxes.configure(height=20)
        scrollbar = Scrollbar(self.column_boxes)
        scrollbar.pack(side=RIGHT, fill=Y)
        #Create configuration for fft parameters
        #Label for method input
        method_label = Label(self, text="Method : ")
        #Types of transforms that can be performed
        methods = ["fft", "spectrogram", "nothing"]
        #Get the default parameters
        transform_defaults = self.parent.tc.get_transform_parameters()
        #Used to store the chosen method
        self.method = StringVar(self)
        #Used to read in the type of transform to perform
        self.method_entry = OptionMenu(self, self.method, transform_defaults["method"], *methods)
        #Set up the methods
        if transform_defaults["columns"] != "":
            for column in self.column_boxes.items:
                if column not in transform_defaults["columns"]:
                    self.column_boxes.items[column].set(0)
        #Read in chunk size and fft size
        chunksize_label = Label(self, text="Chunk Size", )
        self.chunksize_entry = Entry(self, width=5)
        self.chunksize_entry.insert(0, transform_defaults["chunk_size"])
        fftsize_label = Label(self, text="FFT Size")
        self.fftsize_entry = Entry(self, width=5)
        self.fftsize_entry.insert(0, transform_defaults["fft_size"])
        #Used to initiate transformation
        self.transform_button = Button(self)
        self.transform_button["text"] = "Transform Data"
        self.transform_button["command"] = self.transform_data
        #Pack elements
        instruction_label.grid(row=0,column=0)
        column_label.grid(row=1, column=0)
        self.column_boxes.grid(row=2, column=0, sticky=W+E)
        method_label.grid(row=1, column=1)
        self.method_entry.grid(row=1, column=2)
        chunksize_label.grid(row=2, column=1)
        self.chunksize_entry.grid(row=2, column=2)
        fftsize_label.grid(row=3, column=1)
        self.fftsize_entry.grid(row=3, column=2)
        self.transform_button.grid(row=4, column=1)

class FFTPreviewScreen(Frame):
    def __init__(self, parent):
        Frame.__init__(self, parent)
        self.parent = parent
        self.page_label = Label(self)
        self.page_label["text"] = "FFT Previews go here. Work in Progress..."
class ConfigureScreen(Frame):
    def save(self):
        # Disable the save button 
        self.SAVEBUTTON.config(state=DISABLED)
        #Save the config file
        with open(self.parent.configFile, 'w') as fh:
            fh.write(self.CONFIG.get("1.0",END))
        #Generate model
        self.parent.tc.build_model()
        #Re-enable save button
        self.SAVEBUTTON.config(state=NORMAL)

    def setDirty(self, event):
        self.dirty = True
        self.SAVEBUTTON.config(state=NORMAL)

    def __init__(self, parent):
        Frame.__init__(self, parent)
        self.parent = parent
        self.dirty = False
        self.parent.configFile = os.path.join(self.parent.projectPath, "parameters.conf")
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
        self.SAVEBUTTON.pack()
        self.CONFIG.bind("<<Modified>>", self.setDirty)
        self.pack()


class ResultsScreen(Frame):
    def __init__(self, parent):
        Frame.__init__(self, parent)
        self.parent = parent
        self.LBL = Label(self)
        self.LBL["text"] = "Results go here. Work in Progress..."
        self.LBL.pack()
        self.TRAINBUTTON = Button(self)
        self.TRAINBUTTON["text"] = "Train"
        self.TRAINBUTTON["command"] = self.start_training
        self.TRAINBUTTON.pack()
        self.pack()
    #Button for training
    def start_training(self):
        #Disable the button
        self.TRAINBUTTON.config(state=DISABLED)
        #Perform training
        self.parent.tc.train()
        #Re-enable the button
        self.TRAINBUTTON.config(state=NORMAL)
        #Return the results
        #results_message = "Training Results\n"
        #results_message += "Training Accuracy: {}\n".format(training_results["acc"][-1])
        #results_message += "Training Loss: {}".format(training_results["loss"][-1])
        #self.LBL["text"] = results_message

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
    def loadProject(self, projectPath):
        self.projectPath = projectPath
        self.WelcomeScreen.pack_forget()
        self.notebook = Notebook(self)
        self.ProjectHomeScreen = ProjectHomeScreen(self)
        self.LoadFilesScreen = LoadFilesScreen(self)
        self.TransformDataScreen = PickHeaders(self)
        self.FFTPreviewScreen = FFTPreviewScreen(self)
        self.ConfigureScreen = ConfigureScreen(self)
        self.ResultsScreen = ResultsScreen(self)
        self.notebook.add(self.ProjectHomeScreen, text="Home")
        self.notebook.add(self.LoadFilesScreen, text="Load Files")
        self.notebook.add(self.TransformDataScreen, text="Transform Data")
        self.notebook.add(self.FFTPreviewScreen, text="FFT Preview")
        self.notebook.add(self.ConfigureScreen, text="Configure Classifier")
        self.notebook.add(self.ResultsScreen, text="Results")
        self.notebook.pack()
        self.TransformDataScreen.refresh()
    def handle_queue(self):
        #Check for events on the queue
        try:
            event = self.tc.result_queue.get_nowait()
            if event["type"] == "success":
                if event["job"] == "transform":
                    messagebox.showinfo("Success", "Data was successfully transformed.")
                elif event["job"] == "build_model":
                    messagebox.showinfo("Success", "Model build was successful.")
                elif event["job"] == "train":
                    #Create a results show
                    results_string = ""
                    for metric, result in event["message"].items():
                        results_string += "{}: {:.4f}\n".format(metric, result[-1])
                    self.ResultsScreen.LBL["text"] = results_string
                    #Success popup
                    messagebox.showinfo("Success", "Model training complete.")
            elif event["type"] == "error":
                error_title = {"transform":"Data Transformaton Error",
                               "build_model": "Model Build Error",
                               "train": "Training Error"}[event["job"]]
                messagebox.showerror(error_title, event["message"])
        except:
            pass
        self.after(250, self.handle_queue)
    def __init__(self, master=None):
        Frame.__init__(self, master)
        self.WelcomeScreen = WelcomeScreen(self)
        self.WelcomeScreen.pack()
        self.columns = []
        self.pack()

root = Tk()
app = Application(master=root)
app.mainloop()
try:
    root.destroy()
except:
    print("root frame already destroyed!")
