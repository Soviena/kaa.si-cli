import os
import requests

url = 'https://graphql.anilist.co'

def login():
    print("LOGIN WITH ANILIST")
    os.system(r'open "https://anilist.co/api/v2/oauth/authorize?client_id=7201&response_type=token"')
    print("Open this url in the browser:\nhttps://anilist.co/api/v2/oauth/authorize?client_id=7201&response_type=token")
    return input("Paste token here : ")

def getUserId(token):
    query = """
        query { 
            Viewer{
                id
                name
            }
        }
    """    
    header = {'Authorization': 'Bearer ' + token, 'Content-Type': 'application/json', 'Accept': 'application/json'}
    return  requests.post('https://graphql.anilist.co',headers=header,json={'query' : query})

def saveMediaListEntry(id,token,status,episode):
    query = """
    mutation ($mediaId: Int, $status: MediaListStatus, $episode : Int) {
        SaveMediaListEntry (mediaId: $mediaId, status: $status, progress : $episode) {
            media{
                title{
                    userPreferred
                }
            }
            status
            progress
        }
    }
    """
    var = {
        "mediaId" : id,
        "status" : status,
        "episode" : episode
    }

    header = {'Authorization': 'Bearer ' + token, 'Content-Type': 'application/json', 'Accept': 'application/json'}
    return  requests.post('https://graphql.anilist.co',headers=header,json={'query' : query, 'variables' : var})    

def searchAnime(title,page=False):
    if page:
        query = """
            query ($title: String) { 
                Page(perPage:10){
                    media (search: $title, type: ANIME){
                        id
                        title {
                            romaji
                            english
                        }
                        description
                        status
                        nextAiringEpisode{
                            airingAt
                        }            
                    }                    
                }

            }            
        """
    else:
        query = """
            query ($title: String) { 
            Media (search: $title, type: ANIME){
                id
                title {
                    romaji
                    english
                }
                description
                status
                nextAiringEpisode{
                    airingAt
                }            
            }
            }
            """
    variable = {'title' : title}
    return requests.post(url, json={'query': query, 'variables': variable})

def searchAnimeId(id):
    query = """
        query ($id: Int) { 
        Media (id: $id, type: ANIME){
            id
            title {
                romaji
                english
            }
            description
            status
            nextAiringEpisode{
                airingAt
            }
        }
        }
        """
    variable = {'id' : id}
    return requests.post(url, json={'query': query, 'variables': variable})

def getListOfAnime(user,status):
    query = """
        query ($user: String, $status : [MediaListStatus]) { 
            MediaListCollection(userName : $user,status_in: $status, type : ANIME) {
                lists{
                    entries{
                        media{
                            title {
                                romaji
                                english
                                native
                                userPreferred
                            }
                            status
                            id
                            nextAiringEpisode{
                                airingAt
                            }                                     
                        }
                        progress
                    }
                }
            } 
        }    
    """
    variable = {'user' : user, 'status' : status}
    return requests.post(url, json={'query': query, 'variables': variable}).content

def checkMediaInUser(user,title):
    title = searchAnime(title)
    title = eval(title.content)
    mediaId = title['data']['Media']['id']
    query = """
        query ($user: String, $mediaId : Int) { 
            MediaList(userName : $user, mediaId : $mediaId){
                media{
                    title{
                        userPreferred
                    }
                }
            }
        }
    """
    variable = {'user' : user, 'mediaId' : mediaId}
    return requests.post(url, json={'query': query, 'variables': variable})