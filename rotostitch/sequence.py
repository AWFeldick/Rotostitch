import os
import re

from PIL import Image


class FrameSequence():

    def __init__(self, path=None):
        if path:
            self.load(path)
        else:
            self.path = None
            self.name = None
            self.ext = None
            self.frames = {}
            self.start = 0
            self.end = 0
            self.frameDigits = 0
            self.frameSize = (0, 0)
            self.mode = None

    def load(self, path):
        # TODO: Add better error handling
        self.path, filename = os.path.split(path)
        sequencePrefix, self.ext = os.path.splitext(filename)
        search = re.search(r".*(?!\d*$).", sequencePrefix)
        if search:
            self.name = seqName = search.group(0)
            prefix = True
        else:
            self.name = ""
            seqName = sequencePrefix
            prefix = False

        length = len(seqName)
        self.start = 1000000000
        self.end = -1000000000
        self.frameDigits = length if not prefix else len(sequencePrefix)-length
        self.frames = {}
        for fname in os.listdir(self.path):
            if os.path.isfile(os.path.join(self.path, fname)):
                f, e = os.path.splitext(fname)
                if (prefix and f[:length] == seqName) or (f[:-length] == '' and f.isdigit()) and e == self.ext:
                    frame = int(f[-self.frameDigits:])
                    self.start = min(frame, self.start)
                    self.end = max(frame, self.end)
                    self.frames[frame] = f

        path = os.path.join(self.path, self.frames[self.start]+self.ext)
        im = Image.open(path)
        self.frameSize = im.size
        self.mode = im.mode

    def image(self, frame):
        if frame in self.frames:
            path = os.path.join(self.path, self.frames[frame]+self.ext)
            return Image.open(path)