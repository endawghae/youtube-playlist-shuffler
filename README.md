# youtube-playlist-shuffler
Youtube's desktop site shuffles playlists by repeatedly picking a random song which results in repeats during a session and Youtube's mobile app shuffles playlists correctly but is inundated with ads (for free riders like me). 
To my knowledge, neither let you continue a session/save the current shuffle order to pick up from later as well.
This project features a simple GUI that lets you listen to youtube playlists with proper shuffling and session saving.

Project uses Python 3.8 and uses the libraries [VLC](https://wiki.videolan.org/Python_bindings/) for audio playback, [yt_dlp](https://github.com/yt-dlp/yt-dlp) (formerly [youtube_dl](https://github.com/ytdl-org/youtube-dl)) to fetch data from youtube links, and [tkinter](https://docs.python.org/3/library/tkinter.html) for GUI.
Because we are using a VLC library for audio playback, [VLC media player](https://www.videolan.org/) will need to be installed as well.


## Installation
### Option 1: Python Script
[Download Python 3.8](https://www.python.org/downloads/) (not tested for newer versions, feel free to try)

Download the libraries the libraries [VLC](https://wiki.videolan.org/Python_bindings/) and [yt_dlp](https://github.com/yt-dlp/yt-dlp) manually or using pip install

Download [VLC media player](https://www.videolan.org/)

Run the python script in the repo

### Option 2: Exe file (spooky)

Download [VLC media player](https://www.videolan.org/)

Run the exe file in the repo

(Optional) Fight with your antivirus as it kneels and begs for you not to run it

## Demo
https://github.com/endawghae/youtube-playlist-shuffler/assets/94265058/b746ee12-9e6b-4bd1-8d77-3fad27a5df4f

