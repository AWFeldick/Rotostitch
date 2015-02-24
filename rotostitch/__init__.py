import os
import sys

__version__ = "1.0.0"

packageDir = os.path.dirname(sys.argv[0])
RESOURCE_DIR = os.path.join(os.path.abspath(packageDir), "resources")
