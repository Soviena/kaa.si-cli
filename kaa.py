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
    q = eval(q.content)['data']
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
        for i in range(len(animes_k)):
            if animes_v[i]['next-link'] == '' and animes_v[i]['status'] == 'Finished Airing':
                histo['anime'].pop(animes_k[i])    
        return "Finished anime is deleted from history"
    elif x in ('S','s'):
        pass # Sync with anulist
    else:
        try:
            x = int(x)
            if animes_v[x]['status'] == 'Finished Airing' and animes_v[x]['next-link'] == '':
                return 'The anime is finished airing and no next episode' 
            elif animes_v[x]['next-link'] == '':
                js = parse_appData(Base_Url+animes_v[x]['json-data']['anime']['slug']+'/'+animes_v[x]['json-data']['episode']['slug']+'-'+animes_v[x]['json-data']['episode']['slug_id'])  
                if js['episode']['next'] == None:
                    return 'not yet updated' 
                else:
                    return check_link(js)          
            js = parse_appData(animes_v[x]['next-link'])    
            return check_link(js) 
        except :
            print("Error") 