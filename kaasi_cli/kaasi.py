from pypresence import Presence
import time, re, os

# local
from kaasi_cli import kaa, scraper, anilist

logo = """

\033[95m██   ██\033[93m  █████   █████ \033[95m       \033[94m ██████ \033[92m██     \033[91m ██ 
\033[95m██  ██ \033[93m ██   ██ ██   ██\033[95m       \033[94m██      \033[92m██     \033[91m ██ 
\033[95m█████  \033[93m ███████ ███████\033[95m █████ \033[94m██      \033[92m██     \033[91m ██ 
\033[95m██  ██ \033[93m ██   ██ ██   ██\033[95m       \033[94m██      \033[92m██     \033[91m ██ 
\033[95m██   ██\033[93m ██   ██ ██   ██\033[95m       \033[94m ██████ \033[92m███████\033[91m ██ v1.0.2
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
    if anilist != None:
        watch_history['anime'][epsData['anime']['name']]['mediaId'] = anilist['media']['id']
        watch_history['last']['mediaId'] = anilist['media']['id']
        if epsData['anime']['status'] == "Currently Airing" and anilist['media']['status'] in ('RELEASING','NOT_YET_RELEASED'):
            watch_history['airing'][epsData['anime']['name']] = watch_history['anime'][epsData['anime']['name']]
            watch_history['airing'][epsData['anime']['name']]['airingAt'] = anilist['media']['nextAiringEpisode']['airingAt']
    elif epsData['anime']['status'] == "Currently Airing":
        watch_history['airing'][epsData['anime']['name']] = watch_history['anime'][epsData['anime']['name']]
    with open('history.txt','w',encoding='utf-8') as histo:
        histo.write(str(watch_history))

def updateAnilist(epsData,ani):
    ani = ani['Media']
    id = ani['id']
    episode = int(re.findall(r"\s(\d*)",epsData['episode']['name'])[0])
    if epsData['episode']['next'] == None and (epsData['anime']['status'] in ("Finished Airing","Completed") or ani['status'] == 'FINISHED'):
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
    global watch_history
    watch_history = {'anime' : {}, 'last' : {}, 'airing' : {}}
    j = 0
    x = eval(anilist.getListOfAnime(cfg['username'],'CURRENT').replace(b'null',b'None'))
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

def searchAnilist(query):
    q = anilist.searchAnime(query,True)
    if q.status_code == 404:
        raise Exception("NOT FOUND")
    else:
        q = q.content.replace(b'null',b'None')
        q = eval(q)['data']['Page']
        for i in range(len(q['media'])):
            print(f"[{i}] {q['media'][i]['title']['romaji']}")
        x = int(input("select anime : "))
        q['media'] = q['media'][x]
        return q
        

def play_vid(link,epsData):
    global watch_history
    if dcrpc:
        try:
            RPC.update(state=epsData['anime']['name'] + " ("+ re.findall(r' (\d*)',epsData['episode']['name'])[0] +" of "+str(len(epsData['episodes'])) + ")", details="Watching anime", start=time.time(),large_image="https://www2.kickassanime.ro/uploads/"+epsData['anime']['image'],large_text=epsData['anime']['name'])
        except:
            RPC.update(state=epsData['anime']['name'], details="Watching anime", start=time.time())
    referer = ''
    sub = ''
    if type(link) is dict:
        if cfg['termux']:
            print("NOT SUPPORTED FOR TERMUX")
            raise Exception("Unsupported")
        sub = ' --sub-file='+re.findall(r'(https:\/\/[^/]*)',link['vlink'])[0]+link['sub']
        link = link['vlink']
        referer = ' --referrer="'+re.findall(r'(https:\/\/[^/]*)',link)[0]+'" '
    elif re.search(r'maverickki|betaplayer|vidstreamingcdn',str(link)):
        if cfg['termux']:
            if cfg['player'] == "mpv":
                link = link.replace('\\','')
                if re.search(r'vidstreamingcdn',str(link)):
                    referer = '"https://gogoanime.fi"'
                else:
                    referer = '"{url}"'.format(url=re.findall(r'(https:\/\/[^/]*)',link)[0])
                print("Can't pass header in mpv android!!\npls add it manually\nGoto settings -> Advanced -> Edit mpv.conf\nadd referrer={}".format(referer))
                if input("only do this once for each server you choose. Open mpv ? [y/n] : ") in ('Y', 'y'):
                    os.system('am start --user 0 -a android.intent.action.VIEW -n is.xyz.mpv/.MainActivity')
                referer = ''
                # raise Exception("CANT PASS HEADER!")
            else:
                print(link,"IS NOT TESTED IN VLC")
                raise Exception("Unsupported")
        else:
            link = link.replace('\\','')
            if cfg['player'] == "mpv":
                if re.search(r'vidstreamingcdn',str(link)):
                    referer = ' --referrer="https://gogoanime.fi"'
                else:
                    referer = ' --referrer="'+re.findall(r'(https:\/\/[^/]*)',link)[0]+'" '
            else:
                if re.search(r'vidstreamingcdn',str(link)):
                    referer = ' --http-referrer="https://gogoanime.fi"'
                else:                
                    referer = ' --http-referrer="{0}"'.format(re.findall(r'(https:\/\/[^/]*)',link)[0])
    print('Trying to play video...')
    link = link.replace('\\','')
    if cfg['termux']:
        if cfg['player'] == "mpv":
            syx = 'am start --user 0 -a android.intent.action.VIEW -d "{link}" -n is.xyz.mpv/.MPVActivity'.format(link=link)
            if referer != '':
                syx += referer
        else:
            syx = 'am start --user 0 -a android.intent.action.VIEW -d "{link}" -n org.videolan.vlc/org.videolan.vlc.gui.video.VideoPlayerActivity'.format(link=link)
    else:
        syx = '{pl} "{link}"'.format(pl=cfg['player'],link=link)
        if referer != '':
            syx += referer
        if sub != '':
            syx += sub
    os.system(syx)
    if epsData['anime']['name'] in watch_history['anime']:
        ani_id = watch_history['anime'][epsData['anime']['name']]['mediaId']
        ani = anilist.searchAnimeId(ani_id).content.replace(b'null',b'None')
        ani = eval(ani)['data']
        ani['media'] = ani['Media']
    else:
        try:
            ani = kaa.searchAnimefromAnilist(epsData)
        except:
            ani = None
            print("CANT FOUND ANIME IN ANILIST!")
            n = input("Manually search anime in anilist ? [y/n] : ") in ('Y','y')
            while n:
                q = input("Anime name : ")
                try:
                    ani = searchAnilist(q)
                    n = False
                except:
                    n = input("Not found, try again ? [y/n] : ") in ('Y','y')
    
    updateWatchHistory(epsData,ani)
    if cfg['anilist'] and ani != None:
        if cfg['auto']:
            updateAnilist(epsData,ani)
        else:
            if input("Update anilist progress ? [y/n] : ") in ('Y','y'):
                updateAnilist(epsData,ani)


def kaasi():
    pass


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
        airing_v = list(watch_history['airing'].values())
        for i in range(len(animes_k)):
            if i%2 == 0:
                print('\033[96m[{i}] {anime} {episode}'.format(i=i, anime=animes_k[i], episode=animes_v[i]['label']), end=' ')
            else:
                print('\033[92m[{i}] {anime} {episode}'.format(i=i, anime=animes_k[i], episode=animes_v[i]['label']), end=' ')
            if animes_v[i]['next-link'] == '' and animes_v[i]['status'] in ("Finished Airing","Completed"):
                print('\033[94mFinished',end='')
            elif animes_k[i] in airing_k:
                print('\033[93mAiring ',end='')
            print('\033[0m')
        x = input('\n[D] to delete finished anime\n[S] to sync with anilist\n[A] to check next airing episode\nSelect anime to resume watching : ')
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
        elif x in ('A','a'):
            for i in range(len(airing_k)):
                if i%2 == 0:
                    print('\033[96m[{i}] {anime} {episode}'.format(i=i, anime=airing_k[i], episode=airing_v[i]['label']), end=' ')
                else:
                    print('\033[92m[{i}] {anime} {episode}'.format(i=i, anime=airing_k[i], episode=airing_v[i]['label']), end=' ')
                next = kaa.parse_appData(airing_v[i]['episodeLink'])  
                if next['anime']['status'] not in ("Finished Airing","Completed"):
                    print('\033[93mAiring ',end='')
                    if next['episode']['next'] != None:
                        print('\033[95mUPDATED!',end='')
                    else:
                        unix = watch_history['airing'][airing_k[i]]['airingAt']-int(time.time())
                        if unix > 0:
                            print("in ",end='')
                            hour = (unix//60)//60
                            d = hour//24
                            h = hour%24
                            if d != 0:
                                print(d,'day and',end=' ')
                            print(h,'hour',end='')
                        else:
                            print('\033[95mAIRED, not yet Updated',end='')
                print('\033[0m')
            x = input('\nSelect anime to resume watching : ')
            try:
                x = int(x)
                animeLink = re.findall(r"(.*)\/episode",airing_v[x]['episodeLink'])[0]
                if airing_v[x]['next-link'] == '':
                    episodeData = kaa.parse_appData(airing_v[x]['episodeLink'])  
                    if episodeData['episode']['next'] == None:
                        print('not yet updated' )
                        x = 0
                    else:
                        episodeData = kaa.parse_appData(kaa.Base_Url+episodeData['episode']['next']['slug'])
                        embedVideoLink = kaa.check_link(episodeData)
                        x = -1
                else:
                    episodeData = kaa.parse_appData(airing_v[x]['next-link'])    
                    embedVideoLink = kaa.check_link(episodeData) 
                    x = -1
            except :
                print("Error")
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
                        episodeData = kaa.parse_appData(kaa.Base_Url+episodeData['episode']['next']['slug'])
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
                episodeData = kaa.parse_appData(kaa.Base_Url+episodeData['episode']['next']['slug'])
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
