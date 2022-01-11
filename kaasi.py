from pypresence import Presence
import time, re, os

# local
import anilist
import kaa
import scraper

logo = """

\033[95m██   ██\033[93m  █████   █████ \033[95m       \033[94m ██████ \033[92m██     \033[91m ██ 
\033[95m██  ██ \033[93m ██   ██ ██   ██\033[95m       \033[94m██      \033[92m██     \033[91m ██ 
\033[95m█████  \033[93m ███████ ███████\033[95m █████ \033[94m██      \033[92m██     \033[91m ██ 
\033[95m██  ██ \033[93m ██   ██ ██   ██\033[95m       \033[94m██      \033[92m██     \033[91m ██ 
\033[95m██   ██\033[93m ██   ██ ██   ██\033[95m       \033[94m ██████ \033[92m███████\033[91m ██ BETA
\033[0m                                          
"""

def firstSetup():
    try:
        with open('./kaasi.txt','r',encoding='utf-8') as config:
            return eval(config.read())
    except:
        with open('./kaasi.txt','w',encoding='utf-8') as config:
            setup = {}
            print("First time setup")
            if int(input("Preferred media player :\n[1] MPV\n[2] VLC\nInput : ")) == 1 :
                setup['player'] = "mpv"
            else :
                setup['player'] = "vlc"
            setup['termux'] = input("Are you using Termux ? [y/n] : ") in ('Y','y')
            setup['anilist'] = input("Login with anilist ? [y/n] : ") in ('y','Y')
            if setup['anilist']:
                setup['token'] = anilist.login()
                setup['auto'] = input("Auto update anilist after watching anime ? [y/n] : ") in ('y','Y')
                setup['username'] = eval(anilist.getUserId(setup['token']).content)['data']['Viewer']['name']
            config.write(str(setup))
            return setup

def outputAnime(animeList):
    for i in range(len(animeList)):
        if i%2==0:
            print("\033[96m[",i,"] ",animeList[i]['name'],"\033[0m")
        else:
            print("\033[92m[",i,"] ",animeList[i]['name'],"\033[0m")

def updateWatchHistory(epsData,anilist=None):
    epsLink = str(kaa.Base_Url+epsData['anime']['slug']+"/"+epsData['episode']['slug']+'-'+epsData['episode']['slug_id']).replace("\\","")
    try :
        watch_history['anime'][epsData['anime']['name']] = {'label' : epsData['episode']['name'], 'next-link' : kaa.Base_Url+epsData['episode']['next']['slug'], 'episodeLink' : epsLink, 'status': epsData['anime']['status']}
        watch_history['last'] = {'name' : epsData['anime']['name'] ,'episode-label' : epsData['episode']['name'], 'next-link' : kaa.Base_Url+epsData['episode']['next']['slug'], 'episodeLink' : epsLink, 'status' : epsData['anime']['status']}
    except :
        watch_history['anime'][epsData['anime']['name']] = {'label' : epsData['episode']['name'], 'next-link' : '', 'episodeLink' : epsLink, 'status' : epsData['anime']['status']}
        watch_history['last'] = {'name' : epsData['anime']['name'] ,'episode-label' : epsData['episode']['name'], 'next-link' : '', 'episodeLink' : epsLink, 'status' : epsData['anime']['status']}
    if cfg['anilist']:
        watch_history['anime'][epsData['anime']['name']]['mediaId'] = anilist['media']['id']
        watch_history['last']['mediaId'] = anilist['media']['id']
        if epsData['anime']['status'] == "Currently Airing" and anilist['media']['status'] in ('RELEASING','NOT_YET_RELEASED'):
            watch_history['airing'][epsData['anime']['name']] = watch_history['anime'][epsData['anime']['name']]
    else:
        watch_history['airing'][epsData['anime']['name']] = watch_history['anime'][epsData['anime']['name']]
    with open('history.txt','w',encoding='utf-8') as histo:
        histo.write(str(watch_history))

def updateAnilist(epsData):
    if epsData['anime']['en_title'] != None:
        q = anilist.searchAnime(epsData['anime']['en_title'])
        if q.status_code == 404:
            q = anilist.searchAnime(epsData['anime']['name'])
    else:
        q = anilist.searchAnime(epsData['anime']['name'])
    q = eval(q.content)['data']['Media']
    id = q['id']
    episode = int(re.findall(r"\s(\d*)",epsData['episode']['name'])[0])
    if epsData['episode']['next'] == None and (epsData['anime']['status'] in ("Finished Airing","Completed") or q['status'] == 'FINISHED'):
        status = 'COMPLETED'
    else:
        status = 'CURRENT'
    response = anilist.saveMediaListEntry(id,cfg['token'],status,episode)
    if response.status_code == 200:
        print("Anilist updated")
    else:
        print("Could not update anilist")
        print(response.content)

def selectAnime(animeList):
    outputAnime(animeList)
    x = int(input("\033[4m\033[92mInput\033[0m : "))
    return kaa.Base_Url+animeList[x]['slug'] 

def fetchAnilist():
    j = 0
    x = eval(anilist.getListOfAnime(cfg['username'],'CURRENT'))
    for i in x['data']['MediaListCollection']['lists'][0]['entries']:
        print("\033[94mFetching",i['media']['title']['romaji'],"\033[0m")
        anime = kaa.search_anime(i['media']['title']['romaji'])
        if anime == None:
            anime = kaa.search_anime(i['media']['title']['english'])
        if anime == None:
            print("\033[91mCANT FIND",i['media']['title']['romaji'],"episode",i['progress'],"\033[0m")
            animes = kaa.search_anime(input("Pls search manually, type the anime name : "))
            try:
                progress = i['progress']
                animeLink = selectAnime(animes)
                epsData = kaa.select_episode(animeLink,True,progress)
                updateWatchHistory(epsData,i)
            except:
                print("\033[91mError ocurred !\033[0m")
                j+=1
        else:
            progress = i['progress']
            animeLink = kaa.Base_Url+anime[0]['slug']
            epsData = kaa.select_episode(animeLink,True,progress)
            updateWatchHistory(epsData,i)
    if j>0 :
        print("\033[91m",j,"anime's failed to sync!!\033[0m")

def play_vid(link,epsData):
    if dcrpc:
        try:
            RPC.update(state=epsData['anime']['name'] + " ("+ re.findall(r' (\d*)',epsData['episode']['name'])[0] +" of "+str(len(epsData['episodes'])) + ")", details="Watching anime", start=time.time())
        except:
            RPC.update(state=epsData['anime']['name'], details="Watching anime", start=time.time())
    print('Trying to play video...')
    link = link.replace('\\','')
    if cfg['termux']:
        if cfg['player'] == "mpv":
            os.system('am start --user 0 -a android.intent.action.VIEW -d "{link}" -n is.xyz.mpv/.MPVActivity'.format(link=link))
        else:
            os.system('am start --user 0 -a android.intent.action.VIEW -d "{link}" -n org.videolan.vlc/org.videolan.vlc.gui.video.VideoPlayerActivity'.format(link=link))
    else:
        os.system('{pl} "{link}"'.format(pl=cfg['player'],link=link))
    updateWatchHistory(epsData)
    if cfg['anilist']:
        if cfg['auto']:
            updateAnilist(epsData)
        else:
            if input("Update anilist progress ? [y/n] : ") in ('Y','y'):
                updateAnilist(epsData)


#MAIN PROGRAM

dcrpc = False;
try:
    client_id = "926022094976852038"  
    RPC = Presence(client_id=client_id)
    RPC.connect()
    dcrpc = True
except:
    print("Can't Connect to discord")

cfg = firstSetup()

watch_history = {'anime' : {}, 'last' : {}, 'airing' : {}}
try:
    with open('./history.txt','r',encoding='utf-8') as histo:
        watch_history = eval(histo.read())
except:
    with open('./history.txt','w',encoding='utf-8') as histo:
        histo.write(str(watch_history))

while True:
    if dcrpc:
        RPC.update(state="In Main Menu", details="Browsing anime")
    print(logo+"\033[93mtype H for history\ntype R to resume watching\ntype A to see rencently uploaded\n\033[1mor just type the anime title to search\033[0m\n")
    query = input("\033[4m\033[92mInput\033[0m : ")
    if query in ('H','h'):
        animes_v = list(watch_history['anime'].values())
        animes_k = list(watch_history['anime'].keys())
        airing_k = list(watch_history['airing'].keys())
        for i in range(len(animes_k)):
            if i%2 == 0:
                print('\033[96m[{i}] {anime} {episode}'.format(i=i, anime=animes_k[i], episode=animes_v[i]['label']), end=' ')
            else:
                print('\033[92m[{i}] {anime} {episode}'.format(i=i, anime=animes_k[i], episode=animes_v[i]['label']), end=' ')
            if animes_v[i]['next-link'] == '' and animes_v[i]['status'] in ("Finished Airing","Completed"):
                print('\033[94mFinished',end='')
            elif animes_k[i] in airing_k:
                next = kaa.parse_appData(animes_v[i]['episodeLink'])  
                if next['anime']['status'] not in ("Finished Airing","Completed"):
                    print('\033[93mAiring ',end='')
                    if next['episode']['next'] != None:
                        print('\033[95mUPDATED!',end='')
            print('\033[0m')
        x = input('\n[D] to delete finished anime\n[S] to sync with anilist\nSelect anime to resume watching : ')
        if x in ('D','d'):
            for i in range(len(animes_k)):
                if animes_v[i]['next-link'] == '' and animes_v[i]['status'] in ("Finished Airing","Completed"):
                    watch_history['anime'].pop(animes_k[i])    
            print("Finished anime is deleted from history")
            x = 0
        elif x in ('S','s'):
            if cfg['anilist']:
                try:
                    fetchAnilist()
                    print("SYNCED!")
                except:
                    print("\n\033[91mFAILED TO CONNECT TO ANILIST!\033[0m\n\nToo Many request or anilist API is down!\npls wait a few minutes and try again\n")
            else:
                print("NOT CONNECTED TO ANILIST")    
            x = 0
        else:
            try:
                x = int(x)
                animeLink = re.findall(r"(.*)\/episode",animes_v[x]['episodeLink'])[0]
                if animes_v[x]['status'] in ("Finished Airing","Completed") and animes_v[x]['next-link'] == '':
                    print('The anime is finished airing and no next episode')
                    x = 0
                elif animes_v[x]['next-link'] == '':
                    episodeData = kaa.parse_appData(animes_v[x]['episodeLink'])  
                    if episodeData['episode']['next'] == None:
                        print('not yet updated' )
                        x = 0
                    else:
                        embedVideoLink = kaa.check_link(episodeData)
                        x = -1
                else:
                    episodeData = kaa.parse_appData(animes_v[x]['next-link'])    
                    embedVideoLink = kaa.check_link(episodeData) 
                    x = -1
            except :
                print("Error")
                x = 0

    elif query in ('R','r'):
        print('Last session :',watch_history['last']['name'],watch_history['last']['episode-label'])
        animeLink = re.findall(r"(.*)\/episode",watch_history['last']['episodeLink'])[0]
        if watch_history['last']['status'] == ("Finished Airing","Completed") and watch_history['last']['next-link'] == '': 
            print('The anime is finished airing and no next episode' )
        elif watch_history['last']['next-link'] == '':
            episodeData = kaa.parse_appData(watch_history['last']['episodeLink'])
            if episodeData['episode']['next'] == None:
                print('not yet updated' )
            else:
                embedVideoLink = kaa.check_link(episodeData)
                x = -1
        else:
            episodeData = kaa.parse_appData(watch_history['last']['next-link'])
            embedVideoLink = kaa.check_link(episodeData)
            x = -1

    elif query in ('A','a'):
        animes = kaa.recently_uploaded()
        animeLink = selectAnime(animes)
        episodeData = kaa.parse_appData(animeLink)
        animeLink = re.findall(r"(.*)\/episode",animeLink)[0]
        embedVideoLink = kaa.check_link(episodeData)
        x = -1

    else:
        animes = kaa.search_anime(query)
        if animes != None:
            animeLink = selectAnime(animes)
            episodeData = kaa.select_episode(animeLink)
            embedVideoLink = kaa.check_link(episodeData)
            x = -1
        else:
            x = 0

    while x != 0:
        if "gogoplay1.com" in str(embedVideoLink):
            videoLink = scraper.vidstreaming(embedVideoLink)
        else:
            videoLink = scraper.bestremo(episodeData)
        try:
            play_vid(videoLink,episodeData)
        except:
            print("Some error occurred!")
        print("[1] Next episode\n[2] Play again\n[3] Select episode\n[0] Back to menu")
        x = int(input("Input : "))
        if x == 1 :
            try:
                episodeData = kaa.parse_appData(kaa.Base_Url+episodeData['episode']['next']['slug'])
                embedVideoLink = kaa.check_link(episodeData)
            except:
                print("No next episode")
                break
        elif x == 2:
            pass
        elif x == 3:
            episodeData = kaa.select_episode(animeLink)
            embedVideoLink = kaa.check_link(episodeData)
        else:
            break
