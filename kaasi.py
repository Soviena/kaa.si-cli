from pypresence import Presence
import cloudscraper
import time
from bs4 import BeautifulSoup
import requests as s
import re, json
import base64, os

dcrpc = False;
try:
    client_id = "926022094976852038"  # Enter your Application ID here.
    RPC = Presence(client_id=client_id)
    RPC.connect()
    dcrpc = True
except:
    print("Can't Connect to discord")

Base_Url = "https://www2.kickassanime.ro/"
watch_history = {'anime' : {}, 'last' : {}}
logo = """

\033[95m██   ██\033[93m  █████   █████ \033[95m       \033[94m ██████ \033[92m██     \033[91m ██ 
\033[95m██  ██ \033[93m ██   ██ ██   ██\033[95m       \033[94m██      \033[92m██     \033[91m ██ 
\033[95m█████  \033[93m ███████ ███████\033[95m █████ \033[94m██      \033[92m██     \033[91m ██ 
\033[95m██  ██ \033[93m ██   ██ ██   ██\033[95m       \033[94m██      \033[92m██     \033[91m ██ 
\033[95m██   ██\033[93m ██   ██ ██   ██\033[95m       \033[94m ██████ \033[92m███████\033[91m ██ 
\033[0m                                          
"""
try:
    with open('./h.txt','r',encoding='utf-8') as histo:
        watch_history = eval(histo.read())
except:
    with open('./h.txt','w',encoding='utf-8') as histo:
        histo.write(str(watch_history))

# connect with anilist ?
# connect with my anime list ?

mediaPlayer = 'mpv' # Change this to your desired media player

def vidstreaming(url,json_data):
    soup = parse_web(url)
    player = soup.find('script', text=re.compile("player.on"))
    jw_link = re.findall(r"'([http|\/].*)'",re.findall(r"{ w.*",str(player))[0])[0]
    if "http" not in jw_link:
        jw_link = "https:"+jw_link
    print("Getting link...")
    soup = parse_web(jw_link, True)
    soup = soup.findAll('li', class_="linkserver")
    for i in soup:
        if "sbplay2" in str(i['data-video']):
            jw_link = i['data-video']
    jw_link = jw_link.replace("/e/","/d/")
    try:
        soup = parse_web(jw_link)
        soup = soup.findAll('a', text=re.compile("quality")) 
        x = input("Quality High 1080 - Normal 720 - Low 360\nSelect quality [h/n/l] : ")
        if x not in ('h','n','l'):
            x = 'h'
        hash = re.findall(r"'([1234567890\-abcdef]*)'",soup[0]['onclick'])[0]
        id = re.findall(r"d\/(.*)",jw_link)[0]
        soup = parse_web("https://sbplay2.com/dl?op=download_orig&id={id}&mode={quality}&hash={hash}".format(id=id, quality=x, hash=hash))
        Vlink = soup.find('a', text=re.compile("Direct Download Link"))['href']
    except:
        x = input("Error occured, try again ? [y/n]: ")
        if x=='n' : return "Cancelled"
        return vidstreaming(url,json_data)
    return play_vid(Vlink,json_data)

def play_vid(link,json_data):
    if dcrpc:
        try:
            RPC.update(state=json_data['anime']['name'] + " ("+ re.findall(r' (\d*)',json_data['episode']['name'])[0] +" of "+str(len(json_data['episodes'])) + ")", details="Watching anime", start=time.time())
        except:
            RPC.update(state=json_data['anime']['name'], details="Watching anime", start=time.time())
    print('Trying to play video...')
    link = link.replace('\\','')
    # uncomment for termux
    #os.system('am start --user 0 -a android.intent.action.VIEW -d "{link}" -n is.xyz.mpv/.MPVActivity'.format(link=link))
    os.system('{pl} "{link}"'.format(pl=mediaPlayer,link=link))
    try :
        watch_history['anime'][json_data['anime']['name']] = {'label' : json_data['episode']['name'], 'next-link' : Base_Url+json_data['episode']['next']['slug'], 'status': json_data['anime']['status'], 'json-data': json_data}
        watch_history['last'] = {'name' : json_data['anime']['name'] ,'episode-label' : json_data['episode']['name'], 'next-link' : Base_Url+json_data['episode']['next']['slug'], 'status': json_data['anime']['status'], 'json-data': json_data}
    except :
        watch_history['anime'][json_data['anime']['name']] = {'label' : json_data['episode']['name'], 'next-link' : '', 'status': json_data['anime']['status'], 'json-data': json_data}
        watch_history['last'] = {'name' : json_data['anime']['name'] ,'episode-label' : json_data['episode']['name'], 'next-link' : '', 'status': json_data['anime']['status'], 'json-data': json_data}
    with open('h.txt','w',encoding='utf-8') as histo:
        histo.write(str(watch_history))
    print("[0] Next episode\n[1] Play again\n[2] Select episode\n[3] Back to menu")
    x = int(input("Input : "))
    if x == 0 :
        try:
            soup = parse_web(Base_Url+json_data['episode']['next']['slug'])
            js = parse_appData(soup)
            return check_link(js)
        except:
            return "No next episode"
    elif x == 1:
        return play_vid(link,json_data)
    elif x == 2:
        return select_episode(Base_Url+json_data['anime']['slug'])
    return "Success"

def parse_web(url, cloudflare=False):
    if cloudflare:
        scraper = cloudscraper.create_scraper()
        page = scraper.get(url).text
        return BeautifulSoup(page, "html.parser")
    else:
        page = s.get(url)
        return BeautifulSoup(page.content, "html.parser")

def parse_appData(soup):
    json_data = soup.find('script', text=re.compile("appData") )
    data = str(json_data)[str(json_data).find('{"clip'):str(json_data).find('} ||')+1]
    return json.loads(data)

def check_link(js):
    if js['episode']['link1'] != '':
        if "gogoplay1.com" in str(js['episode']['link1']):
            return vidstreaming(js['episode']['link1'],js)
        else :
            soup = parse_web(js['episode']['link1'])
            player = soup.find('script',text=re.compile("sources"))
            player = re.search(r'var sources = \[.*\]',str(player)).group()
            player = player[14:]
            player = eval(player)
            try:
                return sel_source(player,js)
            except:
                print("No source found\nTrying other sources...")
                for i in range(len(js['ext_servers'])):
                    if js['ext_servers'][i]['name'] == 'Vidstreaming':
                        return vidstreaming(js['ext_servers'][i]['link'],js)                
    elif js['ext_servers'] != None:
        for i in range(len(js['ext_servers'])):
            if js['ext_servers'][i]['name'] == 'Vidstreaming':
                return vidstreaming(js['ext_servers'][i]['link'],js)
    else:
        return "Direct download"

def sel_source(json_list,json_data):
    j = 0;
    for i in range(len(json_list)):
        if not ((json_list[i]['name'] == "MAVERICKKI") or (json_list[i]['name'] == "BETAPLAYER")):
            print("[{num}] {source}".format(num=i,source=json_list[i]['name']))
            j+=1;
    if j == 0 :
        raise Exception("No available source")
    x = int(input("Select source : "))
    if json_list[i]['name'] == "A-KICKASSANIME":
        return check_method(str(json_list[x]['src']).replace('\\',''),json_data,json_list)
    else:
        return s_pref_iframe(str(json_list[x]['src']).replace('\\',''),json_data,json_list)

def s_pref_iframe(link,json_data,json_list):
    soup = parse_web(link)
    player = soup.find('iframe')
    if 'embed.php' in link:
        return check_method(link[:link.find('embed.php')]+player['src'],json_data,json_list)
    elif 'player.php' in link:
        return check_method(link[:link.find('player.php')]+player['src'],json_data,json_list)

def search_anime(query):
    Search_Url = "search?q="
    soup = parse_web(Base_Url+Search_Url+query)
    js = parse_appData(soup)
    if ((not ("animes" in js)) or (len(js['animes']) == 0)):
        print("not found")
        return
    animes = js['animes']
    for i in range(len(animes)):
        if i%2==0:
            print("\033[96m[",i,"] ",animes[i]['name'],"\033[0m")
        else:
            print("\033[92m[",i,"] ",animes[i]['name'],"\033[0m")
    x = int(input("\033[4m\033[92mInput\033[0m : "))
    return select_episode(Base_Url+animes[x]['slug'])

def select_episode(link):
    soup = parse_web(link)
    js = parse_appData(soup)
    episodes = js['anime']['episodes']
    x = int(input("Select episode [1-{episode}] : ".format(episode=len(episodes))))
    soup = parse_web(Base_Url+episodes[len(episodes)-x]['slug'])
    js = parse_appData(soup)
    return check_link(js)

def check_method(link,json_data,json_list):
    print('getting link...')
    soup = parse_web(link)
    player = soup.findAll('script')
    #print(soup)
    for i in player:
        if 'Base64.decode' in str(i):
            enc = str(i)[str(i).find('Base64.decode("')+15:str(i).find('"))')]
            dec = decode_base64(enc)
        elif 'atob' in str(i):
            enc = str(i)[str(i).find('atob("')+6:str(i).find('"))')]
            dec = decode_base64(enc,lossless=True)
        else:
            dec = i
        if re.search(r'(\[.*file.*\])',str(dec)) != None:
            group = re.search(r'(\[.*file.*\])',str(dec)).group()
            if re.search(r'(http[^"\']*)',group) != None:
                url = re.findall(r'(http[^\'"]*)',group)
                label = re.findall(r'(?:label.+?")([^\'\"]*)',group)
                for i in range(len(url)):
                    try:
                        print("[{num}] {label}".format(num=i,label=label[i]))
                    except:
                        break
                x = int(input("Select quality : "))
                return play_vid(url[x],json_data)
            else:
                return sel_source(json_list,json_data)

        elif re.search(r'(?:(?:source.*|file.*|src.*)(?!.*(googleuserconten|googletagmanager|subtitle|\.js).*)(https:\/\/[^"]*))',str(dec)) != None:
            return play_vid(re.search(r'(?:(?:source.*|file.*|src.*)(?!.*(googleuserconten|googletagmanager|subtitle|\.js).*)(https:\/\/[^"]*))',str(dec)).group(2),json_data)

def decode_base64(text,lossless=False):
    base64_bytes = text.encode('ascii')
    if lossless:
        base64_bytes += b'=='
    message_bytes = base64.b64decode(base64_bytes)
    return message_bytes.decode('ascii')

def main_menu():
    if dcrpc:
        RPC.update(state="In Main Menu", details="Browsing anime")
    print(logo+"\033[93mtype H for history\ntype R to resume watching\ntype A to see rencently uploaded\n\033[1mOr just type the anime title to search\033[0m\n")
    query = input("\033[4m\033[92mInput\033[0m : ")
    if query in ('H','h'):
        return history(watch_history)
    elif query in ('R','r'):
        return resume(watch_history)
    elif query in ('A','a'):
        return recently_uploaded()        
    else:
        return search_anime(query)

def history(histo):
    animes_v = list(histo['anime'].values())
    animes_k = list(histo['anime'].keys())
    for i in range(len(animes_k)):
        if i%2 == 0:
            print('\033[96m[{i}] {anime} {episode}'.format(i=i, anime=animes_k[i], episode=animes_v[i]['label']), end=' ')
        else:
            print('\033[92m[{i}] {anime} {episode}'.format(i=i, anime=animes_k[i], episode=animes_v[i]['label']), end=' ')            
        if animes_v[i]['next-link'] == '' and animes_v[i]['status'] == 'Finished Airing':
            print('Finished',end='')
        print('\033[0m')
    x = input('[D] to delete finished anime\nSelect anime to resume watching : ')
    if x in ('D','d'):
        clean_finished(histo)
        return "Finished anime is deleted from history"
    else:
        x = int(x)
    if animes_v[x]['status'] == 'Finished Airing' and animes_v[x]['next-link'] == '':
        return 'The anime is finished airing and no next episode' 
    elif animes_v[x]['next-link'] == '':
        soup = parse_web(Base_Url+animes_v[x]['json-data']['anime']['slug']+'/'+animes_v[x]['json-data']['episode']['slug']+'-'+animes_v[x]['json-data']['episode']['slug_id'])
        js = parse_appData(soup)  
        if js['episode']['next'] == None:
            return 'not yet updated' 
        else:
            return check_link(js)          
    soup = parse_web(animes_v[x]['next-link'])
    js = parse_appData(soup)    
    return check_link(js)    

def clean_finished(histo):
    animes_v = list(histo['anime'].values())
    animes_k = list(histo['anime'].keys())
    for i in range(len(animes_k)):
        if animes_v[i]['next-link'] == '' and animes_v[i]['status'] == 'Finished Airing':
            histo['anime'].pop(animes_k[i])    

def resume(histo):
    print('Last session :',histo['last']['name'],histo['last']['episode-label'])
    if histo['last']['status'] == 'Finished Airing' and histo['last']['next-link'] == '': return 'The anime is finished airing and no next episode' 
    if histo['last']['next-link'] == '':
        soup = parse_web(Base_Url+histo['last']['json-data']['anime']['slug']+'/'+histo['last']['json-data']['episode']['slug']+'-'+histo['last']['json-data']['episode']['slug_id'])
        js = parse_appData(soup)  
        if js['episode']['next'] == None:
            return 'not yet updated' 
        else:
            return check_link(js)             
    soup = parse_web(histo['last']['next-link'])
    js = parse_appData(soup)
    return check_link(js)

def recently_uploaded():
    soup = parse_web(Base_Url)
    js = parse_appData(soup)
    for i in range(len(js['animeList']['sub'])):
        if i%2==0:
            print('\033[96m[{num}]'.format(num=i),js['animeList']['sub'][i]['name']+" Episode "+js['animeList']['sub'][i]['episode']+"\033[0m")
        else:
            print('\033[92m[{num}]'.format(num=i),js['animeList']['sub'][i]['name']+" Episode "+js['animeList']['sub'][i]['episode']+"\033[0m")            
    x = int(input("input : "))
    soup = parse_web(Base_Url+js['animeList']['sub'][x]['slug'])
    js = parse_appData(soup)
    return check_link(js)

while True:
    print(main_menu())

