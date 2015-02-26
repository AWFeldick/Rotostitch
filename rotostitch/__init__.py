import os
import sys

__version__ = "1.0.0"

packageDir = os.path.dirname(__file__)
RESOURCE_DIR = os.path.join(os.path.abspath(packageDir), "resources")
if not os.path.isdir(RESOURCE_DIR):
    RESOURCE_DIR = os.path.join(os.path.dirname(sys.argv[0]), "resources")
