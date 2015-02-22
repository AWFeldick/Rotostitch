from tkinter import IntVar
import tkinter.constants as Tkc
from tkinter.ttk import Frame, Label, Progressbar


class StatusBar(Frame):

    def __init__(self, master, progressMax=100, **kwargs):
        Frame.__init__(self, master, **kwargs)

        self.label = Label(self, text="Ready...")
        self.label.pack(anchor=Tkc.W)

        self.progressVar = IntVar()
        self.progress = Progressbar(self, mode='determinate',
                                    maximum=abs(progressMax),
                                    length="150",
                                    variable=self.progressVar)

    def showText(self, message):
        self.label.configure(text=message)
        self.progress.stop()
        self.progress.pack_forget()
        self.label.pack(anchor=Tkc.W)

    def showProgress(self):
        self.progress.configure(mode='determinate')
        self.label.pack_forget()
        self.progress.pack(anchor=Tkc.W)
        self.update_idletasks()

    def setProgress(self, value):
        self.progressVar.set(value)
        self.update_idletasks()

    def setProgressMax(self, value):
        self.progress.configure(maximum=abs(value))

    def showActivity(self):
        self.progress.configure(mode='indeterminate')
        self.progress.start()
        self.showProgress()