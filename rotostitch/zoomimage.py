from tkinter import Canvas, NW
from PIL import Image, ImageTk


class ZoomImage(Canvas):

    def __init__(self, master, **kwargs):
        Canvas.__init__(self, master, **kwargs)

        self.bufImageID = self.create_image(0, 0, anchor=NW)

        self.event_add("<<Dragged>>", "<z>")
        self.bind("<Configure>", self._reconfigure)
        self.bind("<Button-2>", self._click)
        self.bind("<Button2-Motion>", self._pan)

        self.loc = [.0, .0]
        self.lastMouseLoc = None
        self.zoom = 1.0
        self._imageSet = False

    def _reconfigure(self, event):
        self.size = (event.width, event.height)
        self._redraw()

    def _redraw(self):
        if self._imageSet:
            x, y = self.loc
            z = self.zoom
            zim = self.image.transform(self.size,
                                       Image.EXTENT,
                                       (x, y, x + (self.size[0]*z), y + (self.size[1]*z)))
            self.bufImageTk = ImageTk.PhotoImage(zim)
            self.itemconfigure(self.bufImageID, image=self.bufImageTk)

    def setImage(self, image):
        """
        Takes a PIL image.
        """
        if image:
            self.image = image
            self._imageSet = True
            self._redraw()

    def getImage(self):
        return self.image

    def moveImage(self, dx, dy):
        self.loc[0] += dx*self.zoom
        self.loc[1] += dy*self.zoom
        self._redraw()

    def _click(self, event):
        self.lastMouseLoc = (event.x, event.y)

    def _pan(self, event):
        dx = self.lastMouseLoc[0] - event.x
        dy = self.lastMouseLoc[1] - event.y
        self.loc[0] += dx*self.zoom
        self.loc[1] += dy*self.zoom
        self.lastMouseLoc = (event.x, event.y)
        self._redraw()
        self.event_generate("<<Dragged>>", x=dx, y=dy)

    def resetZoom(self):
        self.zoom = 1.0
        self._redraw()

    def zoomIn(self, center=None):
        if center:
            self._zoomAdjust(.5, center)
        else:
            self._zoomAdjust(.5, (self.size[0]/2.0, self.size[1]/2.0))

    def zoomOut(self, center=None):
        if center:
            self._zoomAdjust(2.0, center)
        else:
            self._zoomAdjust(2.0, (self.size[0]/2.0, self.size[1]/2.0))

    def reset(self):
        self.delete(self.bufImageID)
        self.bufImageID = self.create_image(0, 0, anchor=NW)
        self.image = None
        self._imageSet = False
        self.resetZoom()
        self.loc = [.0, .0]

    def _zoomAdjust(self, factor, center):
        # Transform scale center into image space
        ox, oy = self.screenToWorld(center)

        # Find the image coords of the view origin in relation to the scale center
        x = self.loc[0] - ox
        y = self.loc[1] - oy

        # Scale the point by the adjustment scale factor
        x *= factor
        y *= factor

        # Transform back into image coords and assign results
        self.loc[0] = ox + x
        self.loc[1] = oy + y

        # Update the old transformation
        self.zoom *= factor
        self._redraw()

    def screenToWorld(self, point):
        x = self.loc[0] + point[0]*self.zoom
        y = self.loc[1] + point[1]*self.zoom
        return (x, y)

    def worldToScreen(self, point):
        x = (point[0] - self.loc[0])/self.zoom
        y = (point[1] - self.loc[1])/self.zoom
        return (x, y)