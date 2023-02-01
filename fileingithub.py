import requests
import base64
import json
import datetime
import pandas as pd
import io

def read_csv_in_github(url,username,token,**kwargs):
    ''' 
    Read a csv file from GITHUB and load it in a pandas DataFrame
    Param:
    url = link to the csv file in raw format
    username = Username of your GitHub account
    token = Personal Access Token (PAO) from your GitHub account
    '''
    # Creates a re-usable session object with your creds in-built
    github_session = requests.Session()
    github_session.auth = (username, token)
    # Downloading the csv file from your GitHub
    download = github_session.get(url).content
    # Reading the downloaded content and making it a pandas dataframe
    df = pd.read_csv(io.StringIO(download.decode('utf-8')),**kwargs)
    return df

def read_file_in_github(url,username,token):
    ''' 
    Read a csv file from GITHUB and load it in a pandas DataFrame
    Param:
    url = link to the csv file in raw format
    username = Username of your GitHub account
    token = Personal Access Token (PAO) from your GitHub account
    '''
    # Creates a re-usable session object with your creds in-built
    github_session = requests.Session()
    github_session.auth = (username, token)
    # Downloading the csv file from your GitHub
    download = github_session.get(url).content.decode('utf-8')
    # Reading the downloaded content 
    return download


def push_to_repo_branch(fileName, repo_slug, branch, user, token):
    '''
    Push file update to GitHub repo
    
    :param fileName: the name of the file on the local branch
    :param repo_slug: the github repo slug, i.e. username/repo
    :param branch: the name of the branch to push the file to
    :param user: github username
    :param token: github user token
    :return None
    :raises Exception: if file with the specified name cannot be found in the repo
    '''
    
    message = f"Automated backup created for the file {fileName} as of {str(datetime.date.today())}"
    path = "https://api.github.com/repos/%s/branches/%s" % (repo_slug, branch)

    r = requests.get(path, auth=(user,token))
    if not r.ok:
        print("Error when retrieving branch info from %s" % path)
        print("Reason: %s [%d]" % (r.text, r.status_code))
        
    rjson = r.json()
    
    treeurl = rjson['commit']['commit']['tree']['url']
    # print(treeurl)
    r2 = requests.get(treeurl, auth=(user,token))
    if not r2.ok:
        print("Error when retrieving commit tree from %s" % treeurl)
        print("Reason: %s [%d]" % (r2.text, r2.status_code))

    
    r2json = r2.json()
    sha = None

    for file in r2json['tree']:
        # Found file, get the sha code
        if file['path'] == fileName:
            sha = file['sha']

    # if sha is None after the for loop, we did not find the file name!
    if sha is None:
        print ("\nThe file " + fileName + " is not in repos 'tree'. \nLet's create a new one .. \n", end=",\n 1 \n 2 \n 3 \n")

    with open(fileName, 'rb') as data:
        byte_content = data.read()
        content = base64.b64encode(byte_content).decode("ascii")

    # gathered all the data, now let's push
    inputdata = {}
    inputdata["branch"] = branch
    inputdata["message"] = message
    inputdata["content"] = content

    if sha:
        inputdata["sha"] = str(sha)

    updateURL = f"https://api.github.com/repos/{repo_slug}/contents/{fileName}"  
    try:
        rPut = requests.put(updateURL, auth=(user,token), data = json.dumps(inputdata))
        if not rPut.ok:
            print("Error when pushing to %s" % updateURL)
            print("Reason: %s [%d]" % (rPut.text, rPut.status_code))

    except requests.exceptions.RequestException as e:
        print('Something went wrong! I will print all the information that is available so you can figure out what happend!')
        print(rPut)
        print(rPut.headers)
        print(rPut.text)
        print(e)


# GITHUBTOKEN = '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'
# data = read_file_in_github('https://raw.githubusercontent.com/bertofant/MyOfficeBookingWebApp/master/users.yaml','bertofant',GITHUBTOKEN)
# print(data)
# df = read_csv_in_github('https://raw.githubusercontent.com/bertofant/MyOfficeBookingWebApp/master/presenzeUtenti.csv','bertofant',GITHUBTOKEN,index_col=0)
# print(df)
#push_to_repo_branch('ultimoaggiornamento.txt', 'bertofant/MyOfficeBookingWebApp', 'master', 'bertofant',GITHUBTOKEN)
