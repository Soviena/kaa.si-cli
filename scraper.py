import cloudscraper, re, base64, requests
from bs4 import BeautifulSoup

def parse_web(url):
    try:
        scraper = cloudscraper.create_scraper()
        page = scraper.get(url).content
    except:
        page = requests.get(url).content
    return BeautifulSoup(page, "html.parser")

def vidstreaming(url):
    player = parse_web(url).find('script', text=re.compile("player.on"))
    jw_link = re.findall(r"'([http|\/].*)'",re.findall(r"{ w.*",str(player))[0])[0]
    if "http" not in jw_link:
        jw_link = "https:"+jw_link
    print("Getting link...")
    soup = parse_web(jw_link).findAll('li', class_="linkserver")
    for i in soup:
        if "sbplay2" in str(i['data-video']):
            jw_link = i['data-video'].replace("/e/","/d/")
    try:
        soup = parse_web(jw_link).findAll('a', text=re.compile("quality")) 
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
        return vidstreaming(url)
    return Vlink


def bestremo(js):
    soup = parse_web(js['episode']['link1'])
    player = soup.find('script',text=re.compile("sources"))
    player = re.search(r'var sources = \[.*\]',str(player)).group()
    player = player[14:]
    player = eval(player)
    try:
        return sel_source(player)
    except:
        for i in range(len(js['ext_servers'])):
            if js['ext_servers'][i]['name'] == 'Vidstreaming':
                return vidstreaming(js['ext_servers'][i]['link'])

def sel_source(json_list):
    j = 0;
    for i in range(len(json_list)):
        if not ((json_list[i]['name'] == "MAVERICKKI") or (json_list[i]['name'] == "BETAPLAYER")):
            print("[{num}] {source}".format(num=i,source=json_list[i]['name']))
            j+=1;
    if j == 0 :
        raise Exception("No available source")
    x = int(input("Select source : "))
    if json_list[x]['name'] in ("A-KICKASSANIME","THETA-ORIGINAL"):
        return check_method(str(json_list[x]['src']).replace('\\',''),json_list)
    else:
        return s_pref_iframe(str(json_list[x]['src']).replace('\\',''),json_list)

def decode_base64(text,lossless=False):
    base64_bytes = text.encode('ascii')
    if lossless:
        base64_bytes += b'=='
    message_bytes = base64.b64decode(base64_bytes)
    return message_bytes.decode('ascii')

def s_pref_iframe(link,json_list):
    soup = parse_web(link)
    player = soup.find('iframe')
    if 'embed.php' in link:
        return check_method(link[:link.find('embed.php')]+player['src'],json_list)
    elif 'player.php' in link:
        return check_method(link[:link.find('player.php')]+player['src'],json_list)

def check_method(link,json_list):
    print('getting link...')
    soup = parse_web(link)
    player = soup.findAll('script')
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
                return url[x]
            else:
                return sel_source(json_list)
        elif re.search(r'(?:(?:source.*|file.*|src.*)(?!.*(googleuserconten|googletagmanager|subtitle|\.js).*)(https:\/\/[^"]*))',str(dec)) != None:
            return re.search(r'(?:(?:source.*|file.*|src.*)(?!.*(googleuserconten|googletagmanager|subtitle|\.js).*)(https:\/\/[^"]*))',str(dec)).group(2)