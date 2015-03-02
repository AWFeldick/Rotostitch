import os
import math
import tkinter
from tkinter import Menu, IntVar, StringVar, PhotoImage
import tkinter.constants as Tkc
from tkinter.ttk import Frame, Button, Label, Radiobutton, Entry
from tkinter import filedialog, messagebox

from PIL import Image, ImageChops

from rotostitch import RESOURCE_DIR, __version__
from rotostitch.sequence import FrameSequence
from rotostitch.statusbar import StatusBar
from rotostitch.togglebutton import ToggleButton
from rotostitch.zoomimage import ZoomImage
from rotostitch.spinbox import Spinbox


class Coord():
    """ Helper class defining the 2D coordinate (x, y)."""
    def __init__(self, x=0, y=0):
        self.x = 0
        self.y = 0

    def set(self, x, y):
        self.x = x
        self.y = y

    def get(self):
        return (self.x, self.y)


class Application(tkinter.Tk):
    def __init__(self):
        tkinter.Tk.__init__(self)

        # Menu Setup
        menuBar = Menu(self)

        fileMenu = Menu(menuBar, tearoff=False)
        fileMenu.add_command(label="Open...", command=self.loadSequence)
        fileMenu.add_command(label="Close", command=self.closeSequence)
        fileMenu.add_separator()
        fileMenu.add_command(label="Exit", command=self.destroy)

        aboutMenu = Menu(menuBar, tearoff=False)
        aboutMenu.add_command(label="Help", command=self.showHelp)
        aboutMenu.add_command(label="About...", command=self.showAbout)

        menuBar.add_cascade(label="File", menu=fileMenu)
        menuBar.add_cascade(label="About", menu=aboutMenu)

        # Window Setup
        self.title("Rotostitch " + __version__)
        self.config(menu=menuBar)
        self.iconbitmap(default=os.path.join(RESOURCE_DIR, "rotostitch-icon.ico"))

        masterFrame = Frame(self)
        masterFrame.pack(expand=1, fill=Tkc.BOTH, padx=2, pady=2)

        self.status = StatusBar(self)
        self.status.pack(anchor=Tkc.W, fill=Tkc.X, side=Tkc.BOTTOM)

        # Image review panels frame
        imgFrame = Frame(masterFrame, borderwidth=2, relief=Tkc.GROOVE)
        imgFrame.pack(expand=1, fill=Tkc.BOTH)
        imgFrame.columnconfigure(0, weight=1)
        imgFrame.columnconfigure(1, weight=0)
        imgFrame.columnconfigure(2, weight=1)
        imgFrame.rowconfigure(0, weight=1)
        imgFrame.rowconfigure(1, weight=0, pad=3)

        # Creation options frame
        settingsFrame = Frame(masterFrame, borderwidth=2, relief=Tkc.GROOVE)
        settingsFrame.pack(fill=Tkc.X)
        settingsFrame.columnconfigure(1, weight=1, pad=4)

        create = Button(masterFrame, text="Create", command=self.merge)
        create.pack(anchor='se', pady=2)

        self.previewStart = ZoomImage(imgFrame,
                                      width=200,
                                      height=200,
                                      borderwidth=2,
                                      relief=Tkc.RIDGE,
                                      cursor="crosshair")
        self.previewStart.grid(row=0, column=0, sticky=Tkc.NSEW)
        self.previewEnd = ZoomImage(imgFrame, width=200, height=200, borderwidth=2, relief=Tkc.RIDGE)
        self.previewEnd.grid(row=0, column=2, sticky=Tkc.NSEW)

        self.previewStart.bind("<Button>", self._startPreviewClicked)
        self.previewStart.bind("<<Dragged>>", self._previewDragged)
        self.previewEnd.bind("<<Dragged>>", self._previewDragged)

        # Binding just the previews to the MouseWheel event should work but doesn't.
        # The workaround is to bind everything to the mousewheel event 
        # and filter it for just our previews in our callback...
        self.bind_all("<MouseWheel>", self.previewsScrollZoom)

        zoomFrame = Frame(imgFrame)
        zoomFrame.grid(row=0, column=1)

        self.zoomInImg = PhotoImage(file=os.path.join(RESOURCE_DIR, "plus.gif"))
        zoomIn = Button(zoomFrame, image=self.zoomInImg, command=self.previewsZoomIn)
        zoomIn.pack()
        self.zoomResetImg = PhotoImage(file=os.path.join(RESOURCE_DIR, "refresh.gif"))
        zoomReset = Button(zoomFrame, image=self.zoomResetImg, command=self.previewsResetZoom)
        zoomReset.pack()
        self.zoomOutImg = PhotoImage(file=os.path.join(RESOURCE_DIR, "minus.gif"))
        zoomOut = Button(zoomFrame, image=self.zoomOutImg, command=self.previewsZoomOut)
        zoomOut.pack()

        self.differenceImg = PhotoImage(file=os.path.join(RESOURCE_DIR, "difference.gif"))
        self.differenceBtn = ToggleButton(imgFrame, image=self.differenceImg)
        self.differenceBtn.grid(row=1, column=1)
        self.differenceBtn.bind("<Button1-ButtonRelease>", self.toggleDifference)

        startSpinFrame = Frame(imgFrame)
        startSpinFrame.grid(row=1, column=0)
        endSpinFrame = Frame(imgFrame)
        endSpinFrame.grid(row=1, column=2)

        startLabel = Label(startSpinFrame, text="Start Frame:")
        startLabel.pack(side=Tkc.LEFT)

        self.startSpin = Spinbox(startSpinFrame)
        self.startSpin.pack()
        self.startSpin.changedCallback = self.updateStartPreview

        endLabel = Label(endSpinFrame, text="End Frame:")
        endLabel.pack(side=Tkc.LEFT)

        self.endSpin = Spinbox(endSpinFrame)
        self.endSpin.pack()
        self.endSpin.changedCallback = self.updateEndPreview

        widthHeightFrame = Frame(settingsFrame)
        widthHeightFrame.grid(row=0, column=1, columnspan=2, sticky=Tkc.E+Tkc.W)

        widthLabel = Label(settingsFrame, text="Width:")
        widthLabel.grid(row=0, column=0, sticky=Tkc.W)
        self.activePic = PhotoImage(file=os.path.join(RESOURCE_DIR, "go.gif"))
        self.widthSetButton = Button(widthHeightFrame,
                                     text="Set",
                                     command=self.activateSetWidth,
                                     image=self.activePic,
                                     compound=Tkc.LEFT)
        self.widthSetButton.grid(row=0, column=1, sticky=Tkc.W)

        heightLabel = Label(widthHeightFrame, text="Height:")
        heightLabel.grid(row=0, column=2, padx=10, sticky=Tkc.E)
        self.unactivePic = PhotoImage(file=os.path.join(RESOURCE_DIR, "stop.gif"))
        self.heightSetButton = Button(widthHeightFrame,
                                      text="Set",
                                      command=self.activateSetHeight,
                                      image=self.unactivePic,
                                      compound=Tkc.LEFT)
        self.heightSetButton.grid(row=0, column=3, sticky=Tkc.W)

        rotationLabel = Label(settingsFrame, text="Rotation:")
        rotationLabel.grid(row=1, column=0, sticky=Tkc.W)
        rotFrame = Frame(settingsFrame)
        rotFrame.grid(row=1, column=1, sticky=Tkc.W)
        self.rotVar = IntVar()
        self.rotVar.set(1)
        rotLeft = Radiobutton(rotFrame, text="Counter Clockwise", value=1, variable=self.rotVar)
        rotLeft.pack(side=Tkc.LEFT, padx=4)
        rotRight = Radiobutton(rotFrame, text="Clockwise", value=2, variable=self.rotVar)
        rotRight.pack(padx=4)

        outputLabel = Label(settingsFrame, text="Save As:")
        outputLabel.grid(row=2, column=0, sticky=Tkc.W)
        self.outputPathVar = StringVar()
        outputEntry = Entry(settingsFrame, textvariable=self.outputPathVar)
        outputEntry.grid(row=2, column=1, sticky=Tkc.EW)
        self.outputImg = PhotoImage(file=os.path.join(RESOURCE_DIR, "folder.gif"))
        outputSearch = Button(settingsFrame, image=self.outputImg, command=self.setSavePath)
        outputSearch.grid(row=2, column=2, sticky=Tkc.W)

        # Object variables
        self.sequenceLoaded = False
        self.currentSequence = None
        self.startImage = None
        self.endImage = None
        self.differenceOn = False
        self.overlayTag = "OverlayItems"
        self.settingWidth = True
        self.settingHeight = False
        self.width = {'start': Coord(), 'end': Coord()}
        self.height = {'start1': Coord(), 'end1': Coord(), 'start2': Coord(), 'end2': Coord()}

    def showAbout(self):
        pass

    def showHelp(self):
        pass

    def loadSequence(self):
        path = filedialog.askopenfilename(title="Select image from image sequence...")
        if path and os.path.isfile(path):
            self.status.showText("Loading sequence: '{}'".format(path))
            s = self.currentSequence = FrameSequence(path)
            self.sequenceLoaded = True
            self.setupForSequence()
            self.status.showText("Finished loading: '{}'".format(''.join([s.name, "#" * s.frameDigits, s.ext])))
        else:
            self.status.showText("No sequence at: '{}'".format(path))

    def closeSequence(self):
        self.currentSequence = None
        self.sequenceLoaded = False
        self.previewStart.delete(self.overlayTag)
        self.width = {'start': Coord(), 'end': Coord()}
        self.height = {'start1': Coord(), 'end1': Coord(), 'start2': Coord(), 'end2': Coord()}
        self.previewStart.reset()
        self.previewEnd.reset()
        self.startSpin.reset()
        self.endSpin.reset()

    def setSavePath(self):
        path = filedialog.asksaveasfilename(title="Select save location...")
        if path:
            self.outputPathVar.set(path)

    def setupForSequence(self):
        s = self.currentSequence

        if self.differenceOn:
            self.differenceBtn.setSelected(False)
            self.differenceOn = False

        start = s.start
        end = s.end
        self.setStartPreview(start)
        self.setEndPreview(end)

        self.startSpin.min(start)
        self.startSpin.set(start)

        self.endSpin.max(end)
        self.endSpin.set(end)

        self.startSpin.max(end)
        self.endSpin.min(start)

    def setStartPreview(self, frame):
        self.startImage = self.currentSequence.image(frame)
        if self.startImage:
            if self.startImage.mode != "RGBA":
                self.startImage = self.startImage.convert("RGBA")
            self._refreshStartPreview()

    def _refreshStartPreview(self):
        im = self.startImage.copy()
        if self.differenceOn:
            endIm = self.previewEnd.getImage()
            im = ImageChops.difference(im, endIm)
            im.putalpha(255)
        self.previewStart.setImage(im)

    def setEndPreview(self, frame):
        self.endImage = self.currentSequence.image(frame)
        if self.endImage:
            if self.endImage.mode != "RGBA":
                self.endImage = self.endImage.convert("RGBA")
            self._refreshEndPreview()

    def _refreshEndPreview(self):
        im = self.endImage
        if self.differenceOn:
            dif = ImageChops.difference(self.startImage, im)
            dif.putalpha(255)
            self.previewStart.setImage(dif)
        self.previewEnd.setImage(im)

    def updateStartPreview(self):
        i = self.startSpin.get()
        self.endSpin.min(i)
        if self.sequenceLoaded:
            self.setStartPreview(i)

    def updateEndPreview(self):
        i = self.endSpin.get()
        self.startSpin.max(i)
        if self.sequenceLoaded:
            self.setEndPreview(i)

    def previewsScrollZoom(self, event):
        w = self.winfo_containing(event.x_root, event.y_root)
        if w == self.previewStart or w == self.previewEnd:
            center = (event.x_root - w.winfo_rootx(), event.y_root - w.winfo_rooty())
            if event.delta < 0:
                self.adjustZoom("out", center)
            else:
                self.adjustZoom("in", center)

    def previewsZoomIn(self):
        self.adjustZoom("in")

    def previewsZoomOut(self):
        self.adjustZoom("out")

    def adjustZoom(self, direction, center=None):
        if self.sequenceLoaded:
            x, y = center if center else (self.previewStart.size[0] / 2, self.previewStart.size[1] / 2)
            if direction == "in":
                self.previewStart.zoomIn(center)
                self.previewEnd.zoomIn(center)
                self.previewStart.scale(self.overlayTag, x, y, 2.0, 2.0)
            elif direction == "out":
                self.previewStart.zoomOut(center)
                self.previewEnd.zoomOut(center)
                self.previewStart.scale(self.overlayTag, x, y, .5, .5)
            self.drawOverlay()

    def previewsResetZoom(self):
        self.previewStart.resetZoom()
        self.previewEnd.resetZoom()
        self.drawOverlay()

    def _previewDragged(self, event):
        if event.widget == self.previewStart:
            self.previewEnd.moveImage(event.x, event.y)
        else:
            self.previewStart.moveImage(event.x, event.y)
        self.previewStart.move(self.overlayTag, -event.x, -event.y)

    def toggleDifference(self, event):
        if not self.differenceBtn.selected():
            self.differenceOn = True
        else:
            self.differenceOn = False
        self.setDifference()

    def setDifference(self):
        if self.sequenceLoaded:
            if self.differenceOn:
                startIm = self.previewStart.getImage()
                endIm = self.previewEnd.getImage()
                dif = ImageChops.difference(startIm, endIm)
                dif.putalpha(255)
                self.previewStart.setImage(dif)
                self.differenceOn = True
            else:
                self.previewStart.setImage(self.startImage)
                self.differenceOn = False

    def activateSetWidth(self):
        self.widthSetButton.configure(image=self.activePic)
        self.heightSetButton.configure(image=self.unactivePic)
        self.settingWidth = True
        self.settingHeight = False

    def activateSetHeight(self):
        self.widthSetButton.configure(image=self.unactivePic)
        self.heightSetButton.configure(image=self.activePic)
        self.settingWidth = False
        self.settingHeight = True

    def _startPreviewClicked(self, event):
        if self.sequenceLoaded and (event.num == 1 or event.num == 3):
            x, y = self.previewStart.screenToWorld((event.x, event.y))
            if self.settingWidth:
                self._setWidth(event.num, x, y)
            elif self.settingHeight:
                self._setHeight(event.num, x, y, event.state)

    def _setWidth(self, button, x, y):
        if button == 1:
            self.width['start'].set(x, y)
        else:
            self.width['end'].set(x, y)
        self.drawOverlay()

    def _setHeight(self, button, x, y, mod):
        shift = 0x0001
        if button == 1:
            if mod & shift == shift:
                self.height['start2'].set(x, y)
            else:
                self.height['start1'].set(x, y)
        else:
            if mod & shift == shift:
                self.height['end2'].set(x, y)
            else:
                self.height['end1'].set(x, y)
        self.drawOverlay()

    def drawOverlay(self):
        prev = self.previewStart

        # Draw the width line and center line
        x, y = prev.worldToScreen(self.width['start'].get())  # Width line and dot start point
        x2, y2 = prev.worldToScreen(self.width['end'].get())  # Width line and dot end point
        x3 = (x + x2) / 2  # Rotation center line x
        __, y3 = prev.worldToScreen((0, 0))  # Rotation center line top y
        __, y4 = prev.worldToScreen(prev.getImage().size)  # Rotation center line bottom y
        prev.delete(self.overlayTag)
        prev.create_line(x3, y3, x3, y4, tags=self.overlayTag, fill="blue")
        prev.create_line(x, y, x2, y2, tags=self.overlayTag, fill="red")
        prev.create_oval(x - 2, y - 2, x + 3, y + 3, tags=self.overlayTag, fill="green")
        prev.create_oval(x2 - 2, y2 - 2, x2 + 3, y2 + 3, tags=self.overlayTag, fill="green")

        # Draw the height lines
        x, y = prev.worldToScreen(self.height['start1'].get())
        x2, y2 = prev.worldToScreen(self.height['end1'].get())
        prev.create_line(x, y, x2, y2, tags=self.overlayTag, fill="violet")
        prev.create_oval(x - 2, y - 2, x + 3, y + 3, tags=self.overlayTag, fill="green")
        prev.create_oval(x2 - 2, y2 - 2, x2 + 3, y2 + 3, tags=self.overlayTag, fill="green")

        x, y = prev.worldToScreen(self.height['start2'].get())
        x2, y2 = prev.worldToScreen(self.height['end2'].get())
        prev.create_line(x, y, x2, y2, tags=self.overlayTag, fill="cyan")
        prev.create_oval(x - 2, y - 2, x + 3, y + 3, tags=self.overlayTag, fill="green")
        prev.create_oval(x2 - 2, y2 - 2, x2 + 3, y2 + 3, tags=self.overlayTag, fill="green")

    def merge(self):
        path = self.outputPathVar.get()
        if self.sequenceLoaded and path != "":
            self.status.showProgress()
            start = self.startSpin.get()
            end = self.endSpin.get()

            s = self.currentSequence
            rotationCenter = int((self.width['start'].x + self.width['end'].x) / 2)
            height = s.frameSize[1]

            frameCount = end - start
            self.status.setProgressMax(frameCount)

            h = self.height
            len1 = abs(h['start1'].y - h['end1'].y)
            len2 = abs(h['start2'].y - h['end2'].y)
            if len1 > len2:
                adjustmentRatio = len1/len2
            else:
                adjustmentRatio = len2/len1
            crossSection = abs(self.width['start'].x - self.width['end'].x)
            idealWidth = crossSection * math.pi * adjustmentRatio
            arcLen = (1.0 / frameCount) * idealWidth
            stripWidth = int(round(arcLen))
            width = stripWidth * frameCount
            mergeIm = Image.new("RGB", (width, height), None)

            if self.rotVar.get() == 1:
                x = width - stripWidth
                dx = -1
            else:
                x = 0
                dx = 1

            self.status.setProgress(0)
            for fnum in range(start, end):
                frame = s.image(fnum)
                if frame:
                    frameStrip = frame.crop((rotationCenter, 0, rotationCenter + stripWidth, height))

                    mergeIm.paste(frameStrip, (x, 0))
                    x += (dx * stripWidth)
                self.status.setProgress(fnum)

            mergeIm = mergeIm.resize((int(idealWidth), height), Image.ANTIALIAS)
            try:
                mergeIm.save(path)
            except IOError:
                messagebox.showerror("Sorry...", message="Unable to save the final image.")
                self.status.showText("Finished merging. Unable to save to '{}'".format(path))
            self.status.showText("Finished merging. Saved to '{}'".format(path))


if __name__ == '__main__':
    RESOURCE_DIR = "resources"
    __version__ = ""
    app = Application()
    app.mainloop()
