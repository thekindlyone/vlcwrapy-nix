#vlcwrapy-nix
##vlcwrapy-nix is a wrapper over vlc written in python for ubuntu. 

It does the following:

1. It hooks into the keyboard and detects Home and End keys and plays previous and next file in directory. 
2. It places a system tray indicator,exposing similar controls.
3. It remembers the last played file for each directory, which can be loaded by pressing F2 or clicking on the appropriate item in the appindicator menu
4. When started from Dash, or the desktop file or the terminal, if it is not the first time the script is running, it loads the last played file using vlcwrapy-nix.

A video demonstration is available [HERE](https://www.youtube.com/watch?v=80WZLCe3rR0).


##Dependencies
```python-appindicator```, ```python-natsort```, ```python-psutil```     
to install via apt,     
```sudo apt-get install python-appindicator```       
```sudo apt-get install python-natsort```     
```sudo apt-get install python-psutil```       
It also uses pyxhook.py from [this](https://github.com/jeorgen/pyworklogger) project. Many thanks to the author.

##How to use
1. Either git clone this repository, or download zip and extract contents.
2. Edit the last line of vlcwrapy-nix.desktop to reflect location of vlcwrapy-nix.py
3. Place vlcwrapy-nix.desktop in ```~/.local/share/applications``` and make it executable( ```chmod +x vlcwrapy-nix.desktop``` in the applications directory)
4. Enable menu icons via ```gsettings set org.gnome.desktop.interface menus-have-icons true```
5. Open vlc, and disable system tray icon from preferences (it will confuse you as vlcwrapy-nix has the same icon)
6. Right click on any video file in nautius, open with.. browse applications, locate vlcwrapy-nix.py and open.
7. [optional] To use as nautilus script, place symlinks of vlcwrapy-nix.py and pyxhook.py to nautilus scripts directory.

