#! /usr/bin/python3.4-32
# -*- coding: utf-8 -*-

import os
import sys
import distutils.dir_util
from cx_Freeze import (setup, Executable)

base = None

# Windows
if sys.platform == "win32":
    base = "Win32GUI"

    # x86 Python/exe
    if sys.maxsize < 2 ** 32:
        destfolder = os.path.join("bin", "Windows", "x86")

    # x64 Python/exe
    else:
        destfolder = os.path.join("bin", "Windows", "x64")

# Mac OS X
elif sys.platform == "darwin":
    destfolder = os.path.join("bin", "Mac OS X")

# Linux
else:
    destfolder = os.path.join("bin", "Linux")

# Create the freeze path if it doesn't exist
if not os.path.exists(destfolder):
    os.makedirs(destfolder)

# Copy required files
build_exe_options = {
    "build_exe": destfolder,
    "icon": "rotostitch/resources/rotostitch-icon.ico"
}

distutils.dir_util.copy_tree(os.path.join("rotostitch", "resources"),
                             os.path.join(destfolder, "resources"))

setup(
    name="Rotostitch",
    version="1.0.0",
    author="AnW",
    description="Rotostitch",
    license="MIT License",
    options={"build_exe": build_exe_options},
    executables=[Executable("Rotostitch.pyw",
                 targetName="Rotostitch.exe", base=base)]
)
