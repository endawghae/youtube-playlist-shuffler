import asyncio
import os
import random
from tkinter import *
from tkinter import ttk
from tkinter import messagebox
from tkinter import filedialog
import json
import vlc
import yt_dlp

#Display URL Entry GUI
def newSession():
    mainframe.grid_forget()
    playerframe.grid_forget()
    sessionFrame.grid_forget()
    urlframe.grid()
    
    root.bind('<Return>', tryURL)
    root.bind('<Escape>', backToMain)
    return

#Display player GUI, read session file for setup
def resumeSession():
    global sessionSavePath
    global sessionName
    
    root.unbind('<Return>')
    root.unbind('<Escape>')

    messagebox.showwarning(title="Select a session save", message="Be sure to only select session saves in the sessions folder, or the player may not function")

    save = filedialog.askopenfilename(filetypes=[("Text files", "*.txt")], initialdir = sessionSavePath)
    sessionName = save.split('/')[-1]
    session = open(save, "r", encoding = 'utf8')
    lines = session.readlines()
    session.close()
    for song in range(1, len(lines) - 1):
        playlistBox.insert("end", lines[song])

    mainframe.grid_forget()
    urlframe.grid_forget()
    sessionFrame.grid_forget()
    playerframe.grid()
    
    resumePlayer(lines[-1].split(), int(lines[0]))
    return

def nameSession():
    mainframe.grid_forget()
    playerframe.grid_forget()
    urlframe.grid_forget()
    sessionFrame.grid()
    root.bind('<Return>', trySession)
    root.bind('<Escape>', backToMain)

#Display Main Page GUI
def backToMain(event = None):
    urlEntry.delete(0, 'end')
    sessionEntry.delete(0, 'end')
    root.unbind('<Return>')
    root.unbind('<Escape>')
    urlframe.grid_forget()
    playerframe.grid_forget()
    sessionFrame.grid_forget()
    mainframe.grid()
    return

#Toggle player UI Elements
def togglePlayerUIElements(enabled):
    setState = "disabled"
    if enabled is True:
        setState = "normal"
    prevButton.configure(state=setState)
    pauseButton.configure(state=setState)
    playButton.configure(state=setState)
    nextButton.configure(state=setState)
    shuffleButton.configure(state=setState)
    exitPlayerButton.configure(state=setState)
    playlistBox.configure(state=setState)

#Test if URL entered is valid, go to name session if valid
def tryURL(event = None):
    urlEntryButton.configure(state="disabled")
    urlEntryCancelButton.configure(state="disabled")
    
    link = urlEntry.get()
    ydl_opts = {
    'quiet': True,
    "extract_flat": True
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            if "/playlist?list=" not in link:
                raise Exception()
            info = ydl.extract_info(link, download=False)
        except:
            messagebox.showerror("Issue Fetching Playlist", "Could not find playlist from URL.\n(Tip: it should have \"/playlist?list=\" in it)")
        else:
            global playlist
            playlist = link
            nameSession()    
        urlEntry.delete(0, 'end')
        urlEntryButton.configure(state="normal")
        urlEntryCancelButton.configure(state="normal")

#Test if session name is valid, set up music player if valid
def trySession(event = None):
    global sessionSavePath
    
    sessionEntryButton.configure(state="disabled")
    name = sessionEntry.get()
    
    try:
        if not name.isalnum() or os.path.isfile(f'{sessionSavePath}/{name}.txt') is True:
            raise Exception()
        
    except:
        messagebox.showerror("Issue Starting Session", "Session name was invalid or already exists. Please enter a valid session name.")

    else:
        global sessionName
        global playlist
        sessionName = f"{name}.txt"
        ydl_opts = {
        'quiet': True,
        "extract_flat": True
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(playlist, download=False)
            parsedInfo = ydl.sanitize_info(info)['entries']
            playlistURLs = []
            playlistNames = []
            for video in range(0, len(parsedInfo)):
                link = parsedInfo[video]['url']
                title = parsedInfo[video]['title']
                if link != None and title != None:
                    playlistURLs.append(link)
                    playlistNames.append(title)
        setupPlayer(playlistURLs, playlistNames)
    sessionEntry.delete(0, 'end') 
    sessionEntryButton.configure(state="normal")
        

#Display player GUI, loads playlist into music player
def setupPlayer(playlistURLs, playlistNames, pos = 0):
    global sessionSavePath
    global sessionName
    root.unbind('<Return>')
    root.unbind('<Escape>')
    
    mainframe.grid_forget()
    urlframe.grid_forget()
    sessionFrame.grid_forget()
    playerframe.grid()
    
    session = open(f"{sessionSavePath}/{sessionName}", "w", encoding = 'utf8')
    session.write("0\n")
    session = open(f"{sessionSavePath}/{sessionName}", "a", encoding = 'utf8')
    for song in playlistNames:
        session.write("{}\n".format(song))
        playlistBox.insert("end", song)
    for song in playlistURLs:
        session.write("{} ".format(song))
    session.close()
    
    togglePlayerUIElements(False)
    
    global loop
    loop = asyncio.create_task(player(playlistURLs, pos))

#loads playlist into player from file
def resumePlayer(playlistURLs, pos):
    togglePlayerUIElements(False)
    
    global loop
    loop = asyncio.create_task(player(playlistURLs, pos))
    
#plays music in playlist, updates session file
async def player(playlistURLs, startPos):
    global sessionSavePath
    global sessionName
    
    ydl_opts = {
    'format': 'bestaudio/best',
    'quiet': True,
    "extract_flat": True
    }
    for pos in range(startPos, len(playlistURLs)):
        if playlistURLs[pos] != None:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                try:
                    song = ydl.extract_info(playlistURLs[pos], download=False)
                except:
                    pass
                else:
                    session = open(f"{sessionSavePath}/{sessionName}", "r", encoding = 'utf8')
                    lines = session.readlines()
                    lines[0] = "{}\n".format(str(pos))
                    session = open(f"{sessionSavePath}/{sessionName}", "w", encoding = 'utf8')
                    session.writelines(lines)
                    session.close()
                    mediaPlayer.stop()
        
                    if pos == 0:
                        prevButton.configure(state="disabled")
                    elif pos == len(playlistURLs) - 1:
                        nextButton.configure(state="disabled")
                    
                    media = vlc.Media(song['url'])
                    media.get_mrl()
                    mediaPlayer.set_media(media)
                    mediaPlayer.play()

                    await asyncio.sleep(0.5) # disabled buttons will trigger events once reenabled without this... I guess
                    togglePlayerUIElements(True)
                    playlistBox.select_clear(0, len(playlistURLs) - 1)
                    playlistBox.selection_set(pos)
                    playlistBox.see(pos)
                    
                    await asyncio.sleep(5)
                    while mediaPlayer.is_playing() or mediaPlayer.get_state() == vlc.State.Paused:
                        await asyncio.sleep(1)

#Play previous song in playlist
def prevSong():
    global sessionSavePath
    global sessionName
    
    session = open(f"{sessionSavePath}/{sessionName}", "r", encoding = 'utf8')
    lines = session.readlines()
    session.close()
    if int(lines[0] != 0):
        togglePlayerUIElements(False)
        mediaPlayer.stop()
        global loop
        loop.cancel()
        resumePlayer(lines[-1].split(), int(lines[0]) - 1)
    return

#Pause song
def pauseSong():
    mediaPlayer.pause()
    playButton.grid(column = 2, row = 1)
    pauseButton.grid_forget()
    return

#Play song
def playSong():
    mediaPlayer.play()
    pauseButton.grid(column = 2, row = 1)
    playButton.grid_forget()
    return

#Play next song in playlist
def nextSong():
    global sessionName
    global sessionSavePath
    
    session = open(f"{sessionSavePath}/{sessionName}", "r", encoding = 'utf8')
    lines = session.readlines()
    session.close()
    if int(lines[0]) != len(lines[-1].split()) - 1:
        togglePlayerUIElements(False)
        mediaPlayer.stop()
        global loop
        loop.cancel()
        resumePlayer(lines[-1].split(), int(lines[0]) + 1)
    return

#Play song manually selected from listbox
def onSelect(event):
    global sessionName
    global sessionSavePath
    
    widget = event.widget
    index = int(widget.curselection()[0])
    session = open(f"{sessionSavePath}/{sessionName}", "r", encoding = 'utf8')
    lines = session.readlines()
    session.close()
    if int(lines[0]) != len(lines[-1].split()) - 1:
        togglePlayerUIElements(False)
        mediaPlayer.stop()
        global loop
        loop.cancel()
        resumePlayer(lines[-1].split(), index)

#Shuffle playlist and play from beginning
def shufflePlaylist():
    global loop
    global sessionName
    global sessionSavePath
    
    mediaPlayer.stop()
    loop.cancel()
    session = open(f"{sessionSavePath}/{sessionName}", "r", encoding = 'utf8')
    lines = session.readlines()
    session.close()
    names = [lines[line] for line in range(1, len(lines) - 1)]
    urls = lines[-1].split()
    temp = []
    for i in range(len(names)):
        tempDict = {}
        tempDict["url"] = urls[i]
        tempDict["name"] = names[i]
        temp.append(tempDict)
    random.shuffle(temp)
    names = [name.get("name") for name in temp]
    urls = [url.get("url") for url in temp]
    playlistBox.delete(0, "end")
    session = open(f"{sessionSavePath}/{sessionName}", "w", encoding = 'utf8')
    session.write("0\n")
    session = open(f"{sessionSavePath}/{sessionName}", "a", encoding = 'utf8')
    for song in names:
        try:
            session.write("{}".format(song))
        except:
            pass
        else:
            playlistBox.insert("end", song)
    for song in urls:
        try:
            session.write("{} ".format(song))
        except:
            pass
    session.close()
    togglePlayerUIElements(False)
    resumePlayer(urls, 0)
    return

#Stop playing music and reset to Main Page GUI
def exitToMain():
    mediaPlayer.stop()
    global loop
    loop.cancel()
    urlframe.grid_forget()
    playerframe.grid_forget()
    playlistBox.delete(0, "end")
    mainframe.grid()
    
#Main Frame and Widgets
root = Tk()
root.title("YTPlayer")
root.columnconfigure(0, weight = 1)
root.rowconfigure(0, weight = 1)

mainframe = ttk.Frame(root, padding = "50 25 50 25")
mainframe.grid(column = 0, row = 0, sticky = (N, W, E, S))

enterURLButton = ttk.Button(mainframe, text = "Start New Session", command = newSession)
enterURLButton.grid(column = 2, row = 1, sticky = (N, W, E, S))
resumeSessionButton = ttk.Button(mainframe, text = "Resume Previous Session", command = resumeSession)
resumeSessionButton.grid(column = 2, row = 5, sticky = (N, W, E, S))

#Start New Session Frame and Widgets
urlframe = ttk.Frame(root, padding = "20 10 100 10")
urlframe.grid(column = 0, row = 0, sticky = (N, W, E, S))

urlLabel = ttk.Label(urlframe, text = "Enter a Youtube Playlist URL")
urlLabel.grid(column = 2, row = 1, sticky = W)

url = StringVar()
urlEntry = ttk.Entry(urlframe, width = 80, textvariable = "url")
urlEntry.grid(column = 2, row = 2, sticky = W)

urlEntryButtonFrame = ttk.Frame(urlframe)
urlEntryButtonFrame.grid(column = 2, row = 3, sticky = E)

urlEntryButton = ttk.Button(urlEntryButtonFrame, text = "Enter", default = "active", command = tryURL)
urlEntryButton.grid(column = 2, row = 3, sticky = E)
urlEntryCancelButton = ttk.Button(urlEntryButtonFrame, text = "Cancel", command = backToMain)
urlEntryCancelButton.grid(column = 3, row = 3, sticky = E)

urlframe.grid_forget()

sessionFrame = ttk.Frame(root, padding = "20 10 100 10")
sessionFrame.grid(column = 0, row = 0, sticky = (N, W, E, S))

sessionLabel = ttk.Label(sessionFrame, text = "Choose a Session Name (alphanumeric only, please)")
sessionLabel.grid(column = 2, row = 1, sticky = W)

name = StringVar()
sessionEntry = ttk.Entry(sessionFrame, width = 80, textvariable = "name")
sessionEntry.grid(column = 2, row = 2, sticky = W)

sessionEntryButtonFrame = ttk.Frame(sessionFrame)
sessionEntryButtonFrame.grid(column = 2, row = 3, sticky = E)

sessionEntryButton = ttk.Button(sessionEntryButtonFrame, text = "Start Session", default = "active", command = trySession)
sessionEntryButton.grid(column = 2, row = 3, sticky = E)
sessionEntryCancelButton = ttk.Button(sessionEntryButtonFrame, text = "Cancel", command = backToMain)
sessionEntryCancelButton.grid(column = 3, row = 3, sticky = E)

sessionFrame.grid_remove()

#Playlist Frame and Widgets
playerframe = ttk.Frame(root, padding = "50 20 50 20")
playerframe.grid(column = 0, row = 0, sticky = (N, W, E, S))

playerButtonFrame = ttk.Frame(playerframe)
playerButtonFrame.grid(column = 2, row = 1)

prevButton = ttk.Button(playerButtonFrame, text = "Prev", command = prevSong)
prevButton.grid(column = 1, row = 1)
playButton = ttk.Button(playerButtonFrame, text = "Play", command = playSong)
playButton.grid(column = 2, row = 1)
pauseButton = ttk.Button(playerButtonFrame, text = "Pause", command = pauseSong)
pauseButton.grid(column = 2, row = 1)
nextButton = ttk.Button(playerButtonFrame, text = "Next", command = nextSong)
nextButton.grid(column = 3, row = 1)
shuffleButton = ttk.Button(playerButtonFrame, text = "Shuffle", command = shufflePlaylist)
shuffleButton.grid(column = 4, row = 1)

playlistFrame = ttk.Frame(playerframe)
playlistFrame.columnconfigure(0, weight = 1)
playlistFrame.grid(column = 2, row = 2, sticky = (N, W, E, S))

playerframeOverlay = ttk.Frame(root, padding = "50 20 50 20")
playerframeOverlay.grid(column = 0, row = 0, sticky = (N, W, E, S))

#listbox refuses to fit by itself so I'm manually eyeballing it
playlistBox = Listbox(playlistFrame, selectmode = "single", height = 10, width = 47)
playlistBox.bind('<<ListboxSelect>>', onSelect)
playlistBox.grid(column = 1, row = 0, sticky = (N, W, E, S))
playlistScroll = ttk.Scrollbar(playlistFrame, orient = VERTICAL, command = playlistBox.yview)
playlistBox.configure(yscrollcommand = playlistScroll.set)
playlistScroll.grid(column = 2, row = 0, sticky = (N, S))

exitPlayerButton = ttk.Button(playerframe, text = "Exit", command = exitToMain)
exitPlayerButton.grid(column = 2, row = 3, sticky = E)

playerframe.grid_forget()
playerframeOverlay.grid_remove()

#Media Player
mediaPlayer = vlc.MediaPlayer()
loop = None
stop = False

if getattr(sys, 'frozen', False):
    path = os.path.dirname(sys.executable)
else:
    path = os.path.dirname(os.path.abspath(__file__))
if not os.path.exists(f"{path}/sessions"):
    os.makedirs(f"{path}/sessions")       
sessionSavePath = f"{path}/sessions"

sessionName = "session.txt"
playlist = ""

#Check for Session File, Display Main Page GUI
root.resizable(width=False, height=False)

async def run_tk(root, interval=0.05):
    try:
        while True:
            root.update()
            await asyncio.sleep(interval)
    except TclError as e:
        if "application has been destroyed" not in e.args[0]:
            raise

def main():
    asyncio.run(run_tk(root))

if __name__ == "__main__":
    main()

    


    
