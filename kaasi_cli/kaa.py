import re, json
from kaasi_cli import scraper, anilist

Base_Url = "https://www2.kickassanime.ro/"

def parse_appData(url):
    soup = scraper.parse_web(url)
    json_data = soup.find('script', text=re.compile("appData") )
    data = str(json_data)[str(json_data).find('{"clip'):str(json_data).find('} ||')+1]
    return json.loads(data)

def search_anime(query):
    Search_Url = "search?q="
    js = parse_appData(Base_Url+Search_Url+query)
    if ((not ("animes" in js)) or (len(js['animes']) == 0)):
        return None
    return js['animes']

def searchAnimefromAnilist(epsData):
    if epsData['anime']['en_title'] != None:
        q = anilist.searchAnime(epsData['anime']['en_title'])
        if q.status_code == 404:
            q = anilist.searchAnime(epsData['anime']['name'])
    else:
        q = anilist.searchAnime(epsData['anime']['name'])
    if q.status_code == 404:
        raise Exception('NOT FOUND!')
    q = q.content.replace(b'null',b'None')
    q = eval(q)['data']
    q['media'] = q['Media']
    return q

def recently_uploaded():
    js = parse_appData(Base_Url)
    return js['animeList']['sub']

def select_episode(link,direct=False,eps=None):
    episodes = parse_appData(link)['anime']['episodes']
    if direct:
        x = eps # NOT RELIABLE BECAUSE SOME ANIME HAVE 0 EPISODE IN THE LIST!
    else:
        x = int(input("Select episode [1-{episode}] : ".format(episode=len(episodes))))
    return parse_appData(Base_Url+episodes[len(episodes)-x]['slug'])

def check_link(js):
    bestremo = False
    vidstreaming = False
    if js['episode']['link1'] != '':
        bestremo = True
    if js['ext_servers'] != None:
        for i in range(len(js['ext_servers'])):
            if js['ext_servers'][i]['name'] == 'Vidstreaming':
                vidstreaming = True
                vid = js['ext_servers'][i]['link']
    else:
        raise Exception("ONLY DIRECT DOWNLOAD AVAILABLE!!")
    if bestremo and vidstreaming:
        print("[0] Bestremo (kaa)\n[1] Vidstreaming (gogo)")
        x = int(input("Choose main server : "))
        if x == 0:
            return js['episode']['link1']
        elif x == 1:
            return vid
        else:
            raise Exception("Invalid input!!")
    if bestremo:
        return js['episode']['link1']
    elif vidstreaming:
        return vid
