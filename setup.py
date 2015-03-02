#! /usr/bin/python3.4-32
# -*- coding: utf-8 -*-

import os
import sys
import shutil
from distutils.dir_util import copy_tree

from cx_Freeze import setup, Executable

import rotostitch


base = None

outputName = "Rotostitch-" + rotostitch.__version__
# Windows
if sys.platform == "win32":
    base = "Win32GUI"

    # x86 Python/exe
    if sys.maxsize < 2 ** 32:
        destfolder = os.path.join("bin", outputName + "_Win-x86")

    # x64 Python/exe
    else:
        destfolder = os.path.join("bin", outputName + "_Win-x64")

# Mac OS X
elif sys.platform == "darwin":
    destfolder = os.path.join("bin", outputName + "_OSX")

# Linux
else:
    destfolder = os.path.join("bin", outputName + "Linux")

# Copy the resources folder into the bin folder
copy_tree("rotostitch/resources", os.path.join(destfolder, "resources"))

build_exe_options = {
    "build_exe": destfolder
}

setup(
    name="Rotostitch",
    version=rotostitch.__version__,
    author="AnW",
    description="Rotostitch",
    license="MIT License",
    options={"build_exe": build_exe_options},
    executables=[Executable("Rotostitch.pyw",
                            targetName="Rotostitch.exe",
                            icon="rotostitch/resources/rotostitch-icon.ico",
                            base=base)]
)

# Remove some needlessly copied folders, some of which are fairly large.
junkFolders = {"tk": ["demos", "images", "msgs"], "tcl": ["tzdata", "encoding", "http1.0", "msgs", "opt0.4"]}
for baseFolder, subFolders in junkFolders.items():
    for subF in subFolders:
        shutil.rmtree(os.path.join(destfolder, baseFolder, subF))
