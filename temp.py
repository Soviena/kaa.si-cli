from pypresence import Presence
import cloudscraper
import time
from bs4 import BeautifulSoup
import re, json
import base64, os

logo = """

\033[95m██   ██\033[93m  █████   █████ \033[95m       \033[94m ██████ \033[92m██     \033[91m ██ 
\033[95m██  ██ \033[93m ██   ██ ██   ██\033[95m       \033[94m██      \033[92m██     \033[91m ██ 
\033[95m█████  \033[93m ███████ ███████\033[95m █████ \033[94m██      \033[92m██     \033[91m ██ 
\033[95m██  ██ \033[93m ██   ██ ██   ██\033[95m       \033[94m██      \033[92m██     \033[91m ██ 
\033[95m██   ██\033[93m ██   ██ ██   ██\033[95m       \033[94m ██████ \033[92m███████\033[91m ██ BETA
\033[0m                                          
"""

dcrpc = False;
try:
    client_id = "926022094976852038"  
    RPC = Presence(client_id=client_id)
    RPC.connect()
    dcrpc = True
except:
    print("Can't Connect to discord")

Base_Url = "https://www2.kickassanime.ro/"
watch_history = {'anime' : {}, 'last' : {}}

try:
    with open('./history.txt','r',encoding='utf-8') as histo:
        watch_history = eval(histo.read())
except:
    with open('./history.txt','w',encoding='utf-8') as histo:
        histo.write(str(watch_history))

try:
    with open('./kaasi.txt','r',encoding='utf-8') as histo:
        watch_history = eval(histo.read())
except:
    with open('./kaasi.txt','w',encoding='utf-8') as histo:
        print("First time setup :")
        mediaPlayer = int(input("Preferred media player :\n[1] MPV\n[2] VLC\nInput : "))
        if mediaPlayer == 1 :
            mediaPlayer = "mpv"
        else :
            mediaPlayer = "vlc"
        anilist = input("Login with anilist ? [y/n] : ") in ('y','Y')
        if anilist:
            pass
        setup = {}
        histo.write(str(setup))
