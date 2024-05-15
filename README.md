# youtube-playlist-shuffler
Youtube's desktop site shuffles playlists by repeatedly picking a random song which results in repeats during a session and Youtube's mobile app shuffles playlists correctly but does not allow the use of adblock. 
To my knowledge, neither let you continue a session or save the current shuffle order for future listening.
So I made a simple GUI that lets you listen to youtube playlists with proper shuffling and session saving.

Project uses Python 3.8 and uses the libraries [VLC](https://wiki.videolan.org/Python_bindings/) for audio playback, [YT_DLP](https://github.com/yt-dlp/yt-dlp) (formerly [YOUTUBE_DL](https://github.com/ytdl-org/youtube-dl)) to fetch data from youtube links, and [TKINTER](https://docs.python.org/3/library/tkinter.html) for GUI.
Because we are using a VLC library for audio playback, the [VLC media player](https://www.videolan.org/) will need to be installed as well.


## Installation
### Option 1: Python Script
[Download Python 3.8](https://www.python.org/downloads/) (not tested for newer versions)

Download the libraries linked above manually or use pip install

Download VLC media player linked above

Run the python script in the repo

###Option 2: Exe file (spooky)

Download VLC media player linked above

Run the exe file in the repo
