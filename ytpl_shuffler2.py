import asyncio
import os
import random
from tkinter import *
from tkinter import ttk
from tkinter import messagebox
import json
import vlc
import yt_dlp

#Display URL Entry GUI
def newSession():
    mainframe.grid_forget()
    playerframe.grid_forget()
    urlframe.grid()
    root.bind('<Return>', tryURL)
    root.bind('<Escape>', backToMain)
    return

#Display player GUI, read session file for setup
def resumeSession():
    root.unbind('<Return>')
    root.unbind('<Escaoe>')
    mainframe.grid_forget()
    urlframe.grid_forget()
    playerframe.grid()
    session = open("session.txt", "r", encoding = 'utf8')
    lines = session.readlines()
    session.close()
    for song in range(1, len(lines) - 1):
        playlistBox.insert("end", lines[song])
    resumePlayer(lines[-1].split(), int(lines[0]))
    return

#Display Main Page GUI
def backToMain(event = None):
    urlEntry.delete(0, 'end')
    root.unbind('<Return>')
    root.unbind('<Escaoe>')
    urlframe.grid_forget()
    playerframe.grid_forget()
    mainframe.grid()
    return

#Test if URL entered is valid, set up music player if valid
def tryURL(event = None):
    link = urlEntry.get()
    ydl_opts = {
    'quiet': True,
    "extract_flat": True
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            info = ydl.extract_info(link, download=False)
        except:
            messagebox.showerror("Invalid URL", "Could not find playlist from URL")
        else:
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
        urlEntry.delete(0, 'end')

#Display player GUI, loads playlist into music player
def setupPlayer(playlistURLs, playlistNames, pos = 0):
    root.unbind('<Return>')
    root.unbind('<Escaoe>')
    mainframe.grid_forget()
    urlframe.grid_forget()
    playerframe.grid()
    session = open("session.txt", "w", encoding = 'utf8')
    session.write("0\n")
    session = open("session.txt", "a", encoding = 'utf8')
    for song in playlistNames:
        session.write("{}\n".format(song))
        playlistBox.insert("end", song)
    for song in playlistURLs:
        session.write("{} ".format(song))
    session.close()
    global loop
    loop = asyncio.create_task(player(playlistURLs, pos))

#loads playlist into player from file
def resumePlayer(playlistURLs, pos):
    global loop
    loop = asyncio.create_task(player(playlistURLs, pos))
    
#plays music in playlist, updates session file
async def player(playlistURLs, startPos):
    ydl_opts = {
    'format': 'bestaudio/best',
    'quiet': True,
    "extract_flat": True
    }
    for pos in range(startPos, len(playlistURLs)):
        session = open("session.txt", "r", encoding = 'utf8')
        lines = session.readlines()
        lines[0] = "{}\n".format(str(pos))
        session = open("session.txt", "w", encoding = 'utf8')
        session.writelines(lines)
        session.close()
        mediaPlayer.stop()
        playlistBox.select_clear(0, len(playlistURLs) - 1)
        playlistBox.selection_set(pos)
        playlistBox.see(pos)
        prevButton["state"] = "NORMAL"
        pauseButton["state"] = "NORMAL"
        playButton["state"] = "NORMAL"
        nextButton["state"] = "NORMAL"
        shuffleButton["state"] = "NORMAL"
        exitPlayerButton["state"] = "NORMAL"
        if pos == 0:
            prevButton.state(["disabled"])
        elif pos == len(playlistURLs) - 1:
            nextButton.state(["disabled"])
        if playlistURLs[pos] != None:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                try:
                    song = ydl.extract_info(playlistURLs[pos], download=False)
                except:
                    pass
                else:
                    media = vlc.Media(song['url'])
                    media.get_mrl()
                    mediaPlayer.set_media(media)
                    mediaPlayer.play()
                    await asyncio.sleep(5)
                    while mediaPlayer.is_playing() or mediaPlayer.get_state() == vlc.State.Paused:
                        await asyncio.sleep(1)

#Play previous song in playlist
def prevSong():
    session = open("session.txt", "r", encoding = 'utf8')
    lines = session.readlines()
    session.close()
    if int(lines[0] != 0):
        prevButton.state(["disabled"])
        pauseButton.state(["disabled"])
        playButton.state(["disabled"])
        nextButton.state(["disabled"])
        shuffleButton.state(["disabled"])
        exitPlayerButton.state(["disabled"])
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
    session = open("session.txt", "r", encoding = 'utf8')
    lines = session.readlines()
    session.close()
    if int(lines[0]) != len(lines[-1].split()) - 1:
        prevButton.state(["disabled"])
        pauseButton.state(["disabled"])
        playButton.state(["disabled"])
        nextButton.state(["disabled"])
        shuffleButton.state(["disabled"])
        exitPlayerButton.state(["disabled"])
        mediaPlayer.stop()
        global loop
        loop.cancel()
        resumePlayer(lines[-1].split(), int(lines[0]) + 1)
    return

#Play song manually selected from listbox
def onSelect(event):
    widget = event.widget
    index = int(widget.curselection()[0])
    session = open("session.txt", "r", encoding = 'utf8')
    lines = session.readlines()
    session.close()
    if int(lines[0]) != len(lines[-1].split()) - 1:
        prevButton.state(["disabled"])
        pauseButton.state(["disabled"])
        playButton.state(["disabled"])
        nextButton.state(["disabled"])
        shuffleButton.state(["disabled"])
        exitPlayerButton.state(["disabled"])
        mediaPlayer.stop()
        global loop
        loop.cancel()
        resumePlayer(lines[-1].split(), index)

#Shuffle playlist and play from beginning
def shufflePlaylist():
    prevButton.state(["disabled"])
    pauseButton.state(["disabled"])
    playButton.state(["disabled"])
    nextButton.state(["disabled"])
    shuffleButton.state(["disabled"])
    exitPlayerButton.state(["disabled"])
    mediaPlayer.stop()
    global loop
    loop.cancel()
    session = open("session.txt", "r", encoding = 'utf8')
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
    session = open("session.txt", "w", encoding = 'utf8')
    session.write("0\n")
    session = open("session.txt", "a", encoding = 'utf8')
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
    if os.path.isfile('session.txt') is True:
        resumeSessionButton["state"] = "NORMAL"
    
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

#Media Player
mediaPlayer = vlc.MediaPlayer()
loop = None
stop = False

#Check for Session File, Display Main Page GUI
if os.path.isfile('session.txt') is False:
    resumeSessionButton.state(['disabled'])
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

    


    
