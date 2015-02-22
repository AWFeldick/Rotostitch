from tkinter.ttk import Checkbutton


class ToggleButton(Checkbutton):

    def __init__(self, master, **kwargs):
        Checkbutton.__init__(self, master, **kwargs)

        self.configure(style="TButton", command=self._stateChanged)

    def setSelected(self, selected):
        if selected:
            self.state(statespec=["selected"])
            self.configure(style="Toolbutton")
        else:
            self.state(statespec=["!selected"])
            self.configure(style="TButton")

    def selected(self):
        return self.instate(["selected"])

    def _stateChanged(self):
        if self.instate(["selected"]):
            self.configure(style="Toolbutton")
        else:
            self.configure(style="TButton")