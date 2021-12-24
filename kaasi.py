from bs4 import BeautifulSoup
import requests as s
import re, json
import base64, os, cloudscraper

Base_Url = "https://www2.kickassanime.ro/"

def vidstreaming(url):
    from requests_html import HTMLSession
    soup = parse_web(url)
    player = soup.find('script', text=re.compile("player.on"))
    jw_link = re.search(r"{ w.*",str(player)).group()

    if "https" in jw_link:
        jw_link = jw_link[21:-5]
    else :
        jw_link = "https:"+jw_link[21:-5]

    ses = HTMLSession()
    page = ses.get(jw_link)
    json = page.html.render(wait=1, script='jwplayer("myVideo").getPlaylistItem()')
    for i in range(len(json['sources'])):
        print("[{num}] {label}".format(num=i,label=json['sources'][i]['label']))
    x = int(input("Select quality : "))
    return json['sources'][x]['file']
    #play_vid(json['sources'][x]['file'])

def play_vid(link,player='mpv'):
    link = link.replace('\\','')
    os.system('{pl} "{link}"'.format(pl=player,link=link))
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
            return vidstreaming(js['episode']['link1'])
        else :
            soup = parse_web(js['episode']['link1'])
            player = soup.find('script',text=re.compile("sources"))
            player = re.search(r'var sources = \[.*\]',str(player)).group()
            player = player[14:]
            player = eval(player)
            return sel_source(player)
    elif js['ext_servers'] != None:
        for i in range(len(js['ext_servers'])):
            if js['ext_servers'][i]['name'] == 'Vidstreaming':
                return vidstreaming(js['ext_servers'][i]['link'])
    else:
        return "Direct download"

def sel_source(json_list):
    for i in range(len(json_list)):
        if not ((json_list[i]['name'] == "MAVERICKKI") or (json_list[i]['name'] == "BETAPLAYER")):
            print("[{num}] {source}".format(num=i,source=json_list[i]['name']))
    x = int(input("Select source : "))
    if json_list[i]['name'] == "A-KICKASSANIME":
        return check_method(str(json_list[x]['src']).replace('\\',''),json_list)
    else:
        return s_pref_iframe(str(json_list[x]['src']).replace('\\',''),json_list)

def s_pref_iframe(link,json_list):
    soup = parse_web(link)
    player = soup.find('iframe')
    if 'embed.php' in link:
        return check_method(link[:link.find('embed.php')]+player['src'],json_list)
    elif 'player.php' in link:
        return check_method(link[:link.find('player.php')]+player['src'],json_list)

def search_anime(query):
    Search_Url = "search?q="
    soup = parse_web(Base_Url+Search_Url+query)
    js = parse_appData(soup)
    if ((not ("animes" in js)) or (len(js['animes']) == 0)):
        print("not found")
        return
    animes = js['animes']
    for i in range(len(animes)):
        print("[",i,"] ",animes[i]['name'])
    x = int(input("input : "))
    soup = parse_web(Base_Url+animes[x]['slug'])
    js = parse_appData(soup)
    episodes = js['anime']['episodes']
    x = int(input("Select episode [1-{episode}] : ".format(episode=len(episodes))))
    soup = parse_web(Base_Url+episodes[len(episodes)-x]['slug'])
    js = parse_appData(soup)
    return check_link(js)


    # for i in range(4):
    #     if js['episode']['link{num}'.format(num=i+1)] != '':
    #         print("LINK ",i+1,js['episode']['link{num}'.format(num=i+1)])
    #if js['episode']['link3'] == '': 
    #print(js['episode'])
    #if "gogoplay1.com" in str(js['episode']['link1']):
    #    print(True)
    #return js['episode']['link3']

def check_method(link,json_list):
    print(link)
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
                return play_vid(url[x])
            else:
                return sel_source(json_list)

        elif re.search(r'(?:(?:source.*|file.*|src.*)(?!.*(googleuserconten|googletagmanager|subtitle|\.js).*)(https:\/\/[^"]*))',str(dec)) != None:
            return play_vid(re.search(r'(?:(?:source.*|file.*|src.*)(?!.*(googleuserconten|googletagmanager|subtitle|\.js).*)(https:\/\/[^"]*))',str(dec)).group(2))
        

def decode_base64(text,lossless=False):
    base64_bytes = text.encode('ascii')
    if lossless:
        base64_bytes += b'=='
    message_bytes = base64.b64decode(base64_bytes)
    return message_bytes.decode('ascii')

query = input("Search anime : ")
print(search_anime(query))
