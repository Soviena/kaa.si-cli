# kaa.si-cli
Status : Broken

[![pypresence](https://img.shields.io/badge/using-pypresence-00bb88.svg?style=for-the-badge&logo=discord&logoWidth=20)](https://github.com/qwertyquerty/pypresence)

Stream anime using MPV player from kaa.si with python
Termux compatible!

Demo video : https://youtu.be/WgQgQmZy5nE

Requirement :
MPV or VLC installed to path

### python library :
- cloudscraper
- requests
- bs4
- pypresence
- pycryptodome

feedback is apreciated

inspired by https://github.com/pystardust/ani-cli

## INSTALLATION
1. Install python (if not installed) [Python website](https://www.python.org/)
- Don't forget to add python to path
2. Install VLC or MPV and add it to path
- [MPV Website](https://mpv.io/)
- [VLC Website](https://www.videolan.org/)
- [Add program to path](https://www.architectryan.com/2018/03/17/add-to-the-path-on-windows-10/)
3. Download latest package from [Release](https://github.com/Soviena/kaa.si-cli/releases) or clone this repository using `git clone https://github.com/Soviena/kaa.si-cli`
5. Extract and open folder as admin in cmd / powershell
6. `python setup.py install` or `sudo python setup.py install` for linux
7. and run `kaasi` in cmd / powershell to open the app
8. Profit!

## UNINSTALL
1. `pip uninstall kaasi-cli` or `sudo pip uninstall kaasi-cli`

### Note
*the program will create kaasi.txt and history.txt in your working directory, i.e home directory in linux and user directory in windows*.

*if you have problem entering the anilist token, you can edit directly kaasi.txt*.

`{'player': 'mpv/vlc', 'termux': False/True, 'anilist': True, 'token': 'paste token here', 'auto': True/False, 'username': 'Anilist_username'}`

*gogo server is unreliable, pls open an issue if gogo server is not working*

*This code updated once in a while, be sure to check it*


<p align=center>
Visit Since 14/4/2022<br/>
  <a href="https://count.getloli.com/"><img src="https://count.getloli.com/get/@V?theme=rule34"/></a><br/>
</p>
