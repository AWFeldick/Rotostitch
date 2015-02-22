## Rotostitch

A simple python/tkinter GUI utility to assist in assembling a cylindrical map of an object from a image sequence representing the object being rotated 360 degrees in uniform increments.

### Installation

Before you can use Rotostitch, you will need:

	1. Python 3 (developed with 3.4.2)
    2. Required dependencies (listed in requirements.txt)

To install Python 3 see [python.org](https://www.python.org/). After installing Python and cloning the Rotostitch repository (or downloading the ZIP), the next step is to install the dependencies.

To install the dependencies you can use Python pip and 'requirements.txt' to easily do so. On Windows, you could open an instance of 'cmd.exe' with admin privileges and run the following command (assuming you cloned/unzipped the app to the folder 'Rotostitch' that is located on your Desktop):

```bat
python -m pip install -r "C:\Users\[Your Username]\Desktop\Rotostitch\requirements.txt"
```
After the dependencies have been downloaded and installed, you can then run 'Rotostitch.pyw' to launch the program.

### Basic Usage

To really make use of Rotostitch, you have to have an image sequence of an object being rotated 360 degrees around the vertical axis (in relation to the image sequence) in uniform steps. Once you have that, load it with Rotostitch (File >> Open... select one of the frames from the sequence).

If the sequence loads successfully, the first frame will appear in the left image preview area, and the last frame will appear in the right. Navigation of the previews is accomplished by panning with the middle mouse button and zooming in and out with the mouse wheel or '+' and '-' buttons between the previews. Use the entry boxes beneath each preview to select a first and last frame between which the object has rotated 360 degrees. Difference mode (activated with the button below and inbetween the previews) can help with this. Your first and last frame should result in a nearly black image in the left preview with difference mode on.

Having set the start and end frame, set the cylinder map reference width in the left preview with the left and right mouse buttons. If your object is a cylinder itself (as it probably should be), this can simple be the left and right edge of the object. The blue vertical line shows the rotation axis. 

Last, set the rotation direction, ouput file path, and hit 'Create'!
