import cloudscraper, re, base64, requests, random
from bs4 import BeautifulSoup
import aes

def parse_web(url,headers=None,raw=False):
    try:
        scraper = cloudscraper.create_scraper()
        page = scraper.get(url,headers=headers).content
    except:
        page = requests.get(url,headers=headers).content
    if raw:
        return page
    return BeautifulSoup(page, "html.parser")

def vidstreaming(url):
    player = parse_web(url).find('script', text=re.compile("player.on"))
    jw_link = re.findall(r"'([http|\/].*)'",re.findall(r"{ w.*",str(player))[0])[0]
    if "http" not in jw_link:
        jw_link = "https:"+jw_link
    print("Getting link...")
    ajax_url = "https://gogoplay4.com/encrypt-ajax.php"
    page = parse_web(jw_link)
    try: # Thanks to https://github.com/MeemeeLab/node-anime-viewer/blob/main/src/modules/anime.js
        iv = '4770478969418267'.encode('utf8')
        ajaxData = '63976882873559819639988080820907'.encode('utf8')
        episodeVal = page.find('script', {'data-name':'episode'})['data-value']
        decData = str(aes.decrypt(episodeVal, ajaxData, iv))
        videoId = re.search(r'(.*)&title', decData).group(1)
        # decData = re.search(r'(&.*)', string).group(1)
        encryptVid = aes.encrypt(videoId, ajaxData, iv)
        param = 'id='.encode('utf8')+encryptVid+re.search(r'(&.*)', decData).group(1).encode('utf8')
        head = {
            "x-requested-with":"XMLHttpRequest",
            "referer": jw_link,
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36 OPR/82.0.4227.50"
        }
        print(param)
        print(str(parse_web(ajax_url.encode('utf8')+b'?'+param,headers=head)))
        json = eval(str(parse_web(ajax_url.encode('utf8')+'?'.encode('utf8')+param,headers=head)))
        for i in range(len(json['source'])):
            print("[{num}] {label}".format(num=i,label=json['source'][i]['label']))
        x = int(input("Select quality : "))
        return (json['source'][x]['file']).replace('&amp;','&')
    except:
        if input("Error occured, try again ? [y/n]: ") in ('Y','y'):
            return vidstreaming(url)
        else:
            raise Exception("Cancelled")

def bestremo(js):
    if js['episode']['link1'] != '':
        soup = parse_web(js['episode']['link1'])
    elif js['episode']['link4'] != '':
        soup = parse_web(js['episode']['link4'])
    elif js['episode']['link3'] != '':
        print("Download Link")
        raise Exception("Not implemented")
    else:
        print("Not tested")
        print(js['episode']['link2'])
        print("Untested")
        raise Exception("Not implemented")
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
    print("sel source")
    j = 0
    for i in range(len(json_list)):
        print("[{num}] {source}".format(num=i,source=json_list[i]['name']))
        j+=1
    if j == 0 :
        raise Exception("No available source")
    x = int(input("Select source : "))
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
    if player == None:
        return check_method(link,json_list)
    elif 'embed.php' in link:
        return check_method(link[:link.find('embed.php')]+player['src'],json_list)
    elif 'player.php' in link:
        return check_method(link[:link.find('player.php')]+player['src'],json_list)

def check_method(link,json_list):
    print('getting link...')
    if 'maverickki' in link:
        s = parse_web(link.replace('embed','api/source'),raw=True)
        s = s.replace(b"true", b"True")
        vjs = eval(s)
        if len(vjs['subtitles']) != 0:
            for i in range(len(vjs['subtitles'])):
                print('[{idx}] {name}'.format(idx=i,name=vjs['subtitles'][i]['name']))
            x = int(input("Select subtitle : "))
            return {'vlink' : 'https://maverickki.com'+vjs['hls'], 'sub' : vjs['subtitles'][x]['src']}
        else:
            return 'https://maverickki.com'+vjs['hls']

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