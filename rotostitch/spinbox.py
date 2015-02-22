import os
from tkinter import IntVar, PhotoImage
import tkinter.constants as Tkc
from tkinter.ttk import Frame, Button, Entry

from . import RESOURCE_DIR


class Spinbox(Frame):

    def __init__(self, master, **kwargs):
        Frame.__init__(self, master, **kwargs)

        self._last = 0
        self.entryVar = IntVar(self._last)
        self.entry = Entry(self, textvariable=self.entryVar, width=4)
        self.entry.grid(row=0, column=1)
        self.entry.bind("<FocusIn>", self._store)
        self.entry.bind("<FocusOut>", self._validateEntry)
        self.entry.bind("<KeyPress-Return>", self._validateEntry)

        self.leftImg = PhotoImage(file=os.path.join(RESOURCE_DIR, "arrow-left.gif"))
        self.rightImg = PhotoImage(file=os.path.join(RESOURCE_DIR, "arrow-right.gif"))

        self.left = Button(self, image=self.leftImg, command=self.decrement)
        self.left.grid(row=0, column=0, sticky=Tkc.NS)

        self.down = Button(self, image=self.rightImg, command=self.increment)
        self.down.grid(row=0, column=2, sticky=Tkc.NS)

        self.minimum = 0
        self.maximum = 10

        self.changedCallback = None

    def set(self, value):
        assert type(value) == int
        if self._valid(value):
            self.entryVar.set(value)
            if value != self._last:
                self._last = value
                self._issueChanged()

    def get(self):
        return self.entryVar.get()

    def min(self, value):
        assert type(value) == int
        i = int(value)
        if i < self.maximum:
            self.minimum = i
            if self.get() < self.minimum:
                self.set(self.minimum)
        else:
            self.minimum = self.maximum
            self.set(self.minimum)

    def max(self, value):
        assert type(value) == int
        i = int(value)
        if i > self.minimum:
            self.maximum = i
            if self.get() > self.maximum:
                self.set(self.maximum)
        else:
            self.maximum = self.minimum
            self.set(self.maximum)

    def increment(self):
        i = self.entryVar.get()
        if i < self.maximum:
            self.set(i + 1)

    def decrement(self):
        i = self.entryVar.get()
        if i > self.minimum:
            self.set(i - 1)

    def reset(self):
        self._last = 0
        self.entryVar.set(self._last)
        self.minimum = 0
        self.maximum = 10

    def _issueChanged(self):
        if self.changedCallback is not None:
            self.changedCallback()

    def _validateEntry(self, event):
        try:
            i = int(self.entryVar.get())
        except ValueError:
            i = self._current

        if not self._valid(i):
            i = min(self.maximum, max(self.minimum, i))

        self._current = i
        self.set(i)

    def _store(self, event):
        self._current = self.entryVar.get()

    def _valid(self, value):
        return (value >= self.minimum and value <= self.maximum)