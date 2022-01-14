import re, json
import scraper
import anilist

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
    if js['episode']['link1'] != '':
        return js['episode']['link1'] # RETURN EMBED VIDEO LINK
    
    elif js['ext_servers'] != None:
        for i in range(len(js['ext_servers'])):
            if js['ext_servers'][i]['name'] == 'Vidstreaming':
                return js['ext_servers'][i]['link'] # RETURN EMBED VIDEO LINK
    else:
        raise Exception("ONLY DIRECT DOWNLOAD AVAILABLE!!")
