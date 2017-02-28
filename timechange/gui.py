#!/usr/bin/env python3

from tkinter import *
import os
import timechange
from PIL import Image

tc = timechange.TimeChange()
class CheckBoxSet(Frame):
    def process_file(self):
        print("processing")
        data_columns = []
        for idx, checked in enumerate(self.state()):
            if checked == 0:
                data_columns.append(self.items[idx])

        if not os.path.isdir("data"):
            os.mkdir("data")
        if not os.path.isdir("data/results"):
            os.mkdir("data/results")

        for file in self.parent.files:
            file_path = os.path.join(self.parent.dir_path, file)
            data = tc.read_csv(file_path, usecols=data_columns)
            features = tc.extract_features(data, data_size=1000)
            img = Image.fromarray(255 * features, 'L')
            img.save("data/results/test{}.png".format(self.parent.first_file))

    def __init__(self, parent, picks=[], side=LEFT, anchor=W):
        Frame.__init__(self, parent)
        self.parent = parent
        self.vars = []
        self.items = []
        for pick in picks:
            var = IntVar()
            chkbox = Checkbutton(self, text=pick, variable=var)
            chkbox.pack()
            self.vars.append(var)
            self.items.append(pick)
        self.PROCESSBUTTON = Button(self)
        self.PROCESSBUTTON["text"] = "PROCESS"
        self.PROCESSBUTTON["command"] = self.process_file
        self.PROCESSBUTTON.pack()
        self.parent.FILENAMETEXTBOX.pack_forget()
        self.parent.OPENBUTTON.pack_forget()
    def state(self):
        return map((lambda var: var.get()), self.vars)

class Application(Frame):
    def open(self):
        self.dir_path = self.FILENAMETEXTBOX.get('1.0', 'end-1c')
        self.files = os.listdir(self.dir_path)
        self.first_file = self.files[0]
        self.first_file_path = os.path.join(self.dir_path, self.first_file)
        data_columns = list(tc.get_csv_columns(self.first_file_path))
        checkboxes = CheckBoxSet(self, data_columns)
        checkboxes.pack()

    def createWidgets(self):
        self.FILENAMETEXTBOX = Text(self, height=1, width=50)
        self.FILENAMETEXTBOX.pack()
        self.OPENBUTTON = Button(self)
        self.OPENBUTTON["text"] = "OPEN"
        self.OPENBUTTON["command"] = self.open
        self.OPENBUTTON.pack()

    def __init__(self, master=None):
        Frame.__init__(self, master)
        self.pack()
        self.createWidgets()

root = Tk()
app = Application(master=root)
app.mainloop()
root.destroy()
