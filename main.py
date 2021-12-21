# import library
from bs4 import BeautifulSoup
import requests as s
import pandas as pd
import re, json
import base64, os

Base_Url = "https://www2.kickassanime.ro/"
Search_Url = "search?q="
query = input("Search anime : ")

#search
page = s.get(Base_Url+Search_Url+query)
soup = BeautifulSoup(page.content, "html.parser")
json_data = soup.find('script', text=re.compile("appData") )
data = str(json_data)[str(json_data).find('{"clip'):str(json_data).find('} ||')+1]
js = json.loads(data)
if not ("animes" in js):
    print("not found")
    exit()
animes = js['animes']
for i in range(len(animes)):
    print("[",i,"] ",animes[i]['name'])
x = int(input("input : "))

#fetch episode
page = s.get(Base_Url+animes[x]['slug'])
soup = BeautifulSoup(page.content, "html.parser")
json_data = soup.find('script', text=re.compile("appData") )
data = str(json_data)[str(json_data).find('{"clip'):str(json_data).find('} ||')+1]
js = json.loads(data)
episodes = js['anime']['episodes']

x = int(input("Select episode [1-{episode}] : ".format(episode=len(episodes))))
page = s.get(Base_Url+episodes[len(episodes)-x]['slug'])
soup = BeautifulSoup(page.content, "html.parser")
json_data = soup.find('script', text=re.compile("appData") )
data = str(json_data)[str(json_data).find('{"clip'):str(json_data).find('} ||')+1]
js = json.loads(data)
if not ("link3" in js['episode']): 
    print("not available")
    exit()
link = js['episode']['link3']

page = s.get(link)
soup = BeautifulSoup(page.content, "html.parser")
options = soup.findAll('option')
for i in range(len(options)):
    print("[{idx}] {server}".format(idx=i,server=options[i].text))
x = int(input("Select server : "))
link = options[x]['value']
server_link = link[:str(link).find('dl.php?')]

page = s.get(link)
soup = BeautifulSoup(page.content, "html.parser")
if not soup.find('script',text=re.compile("document.write")):
    mirror = soup.find(id="divDownload")
else:
    mirror = soup.find('script',text=re.compile("document.write"))
    encoded = str(mirror)[str(mirror).find('("')+2:str(mirror).find('")')]
    base64_bytes = encoded.encode('ascii')
    message_bytes = base64.b64decode(base64_bytes+b'==')
    decoded = message_bytes.decode('ascii')
    mirror = BeautifulSoup(decoded, "html.parser")
qualities = mirror.findAll('a')
for i in range(len(qualities)):
    print("[{idx}] {quality}".format(idx=i,quality=qualities[i].text))
x = int(input("Select quality : "))
link = qualities[x]['href']
if link[:str(link).find('rdr.php?')] == "":
    print(server_link+link)
    os.system('mpv "{link}"'.format(link=server_link+link))
else:
    print(link)
    os.system('mpv "{link}"'.format(link=link))













