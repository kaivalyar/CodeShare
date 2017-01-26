import sys
import os
import requests
import json
import re
import random
from bs4 import BeautifulSoup


"""
1. get the filename from user
2. read the source file
3. post the relevant details to pastebin (paste.ubuntu.com)
4. fetch the resultant url
5. shorten the received url (via tinyurl.com)
6. print the url for sharing


# Setup autocompletion for author names
# http://stackoverflow.com/questions/5637124/tab-completion-in-pythons-raw-input

# Setup autocompletion for filepaths
# http://stackoverflow.com/questions/6656819/filepath-autocompletion-using-users-input
"""

def welcome():
    print("Welcome to CodeShare 1.0\nPlease report any errors to Kaivalya.\n")

def terminate():
    print("\nThank you for using CodeShare 1.0\nPlease report any errors to Kaivalya.")

def main():
    silent = False
    if (len(sys.argv) >= 2):
        ip = sys.argv[1].lower()
        if (ip == 'silent' or ip == 'quiet' or ip == 'incognito'):
            silent = True
    welcome()
    upload()
    terminate()

def upload(silent = False):
    name = get_user() # ToDo (2.0) : Setup autocompletion based on current author names
    path = get_filename() # ToDo (2.0) : Setup filepath autocompletion, starting from a directory defined in a .config file
    ft = find_filetype(path)
    text = read_file(path)
    lURL = paste(text, name, ft)
    cURL = cleanURL(lURL)
    alias = get_alias(name)
    sURL = get_url(cURL, alias)
    if (ft == "text") :
        print("\n" + name + "\'s text from file \'" + path + "\' can be viewed and downloaded from :\t" + sURL)
    else:
        print("\n" + name + "\'s " + ft + " code from file \'" + path + "\' can be viewed and downloaded from :\t" + sURL)
    c = input("\nPress 'Enter' to quit, or type 'u' to upload another file:\t")
    if (c == 'u' or c == 'U'):
        upload()

#returns the name of the author
def get_user():
    name = input("Enter the name of the author:\t")
    while (name == '' or len(name) > 30):
        name = input("\nEnter the name of the author (max 30 characters):\t")
    name = name[0:30] # redundant
    return name

# will get filepath from the user
def get_filename():
    path = input("Enter the (relative) path to the file:\t")
    while (not os.path.isfile(path)):
        path = input("invalid filename, try again:\t")
    return path

# will return a string containing the entire conents of the file
def read_file(path):
    f = open(path)
    s = f.read()
    f.close()
    return s

# returns a string containing the filetype of the file, as required by pastebin
def find_filetype(path):
    if (path.endswith('.py')):
        return "python3"
    elif (path.endswith('.cpp')):
        return "cpp"
    elif(path.endswith('.java')):
        return "java"
    else:
        return "text"
    # should add more types

# will post s to the pastebin, and then return the resultant url as a string
def paste(s, author, filetype):
    r = requests.post("http://paste.ubuntu.com/", data = {'poster':author, 'syntax':filetype, 'content':s})
    lURL = r.url
    return lURL

def cleanURL(url):
    url = url.replace("/", "%2F")
    url = url.replace(":", "%3A")
    return url
    #http://paste.ubuntu.com/13389890/ should become http%3A%2F%2Fpaste.ubuntu.com%2F13389890%2F

# returns random nicks, of the form "rxxx", where x ~ (0,9)
def generate_random_code():
    return "r" + str(random.randint(100, 999)) # could be optmised to generate by selecting randomly from available codes

# converts author name into author nick
def get_author_code(author, silent = False):# code is synonymous with nick (author code ~ author nick), and used for shortened urls
    result = "ERROR"
    dic = eval(read_file("codes.k"))
    if (author in dic.keys()):
        result = dic[author]
    else: # encapsulate into new function?
        newcode = author[0:4].lower()
        if (newcode in dic.values()):
            #print("Author code generation failed, another author has the same first four letters as this author. Retrying with random code.")
            while (newcode in dic.values()):
                newcode = generate_random_code()
            #print("Code generation successful. Author " + author + " has been assigned the code " + newcode)
        print("\nThe system generated nick for this new author is :\t" + newcode)
        altcode = input("If you wish to override this nick, enter the new nick here \n(or press \'Enter\' to keep default) :\t").lower()
        while (altcode in dic.values()):
            altcode = input("That nick already exists, please enter a unique nick \n(or press \'Enter\' to keep default) :\t").lower()
        if (altcode != ''):
            newcode = altcode
        print("\tSetting nick for " + author + " to " + newcode + ".")
        dic[author] = newcode
        result = newcode
        with open("codes.k", "w") as g:
            g.write(str(dic))
    return result

#converts the author name into a complete shortened url
def get_alias(author, silent = False):
    result = 'ERROR'
    author = get_author_code(author)# author now contains author code/nick, not author name
    dic = eval(read_file("authors.k"))
    if (author in dic.keys()):
        n = dic[author]
        dic[author] = n+1
        result = author + str((n+1))
    else:
        dic[author] = 1001
        result = author + "1001"
    print("\nThe system generated short url for this file is tinyurl.com/" + result + ".")
    altresult = input("If you wish to override this url, enter the new url here \n(or press \'Enter\' to keep default) :\ttinyurl.com/").lower()
    if (altresult != ''):
        result = altresult
        dic[author] = dic[author]-1
    with open("authors.k", "w") as g:
        g.write(str(dic))
    print("\tTrying to reserve tinyurl.com/" + result + " for this file.")
    return result # url is tinyurl.com/result

# returns a shortened url, using tinyurl
def get_url(url, alias, silent = False):
    r = requests.get("http://tinyurl.com/create.php?source=indexpage&url=" + url + "&submit=Make+TinyURL!&alias=" + alias)
    #eg: http://tinyurl.com/create.php?source=indexpage&url=http%3A%2F%2Fpaste.ubuntu.com%2F13389890%2F&submit=Make+TinyURL!&alias=kapp987657654
    bs = BeautifulSoup(r.text, 'html.parser')
    s = bs.find_all(id='contentcontainer')[0].text
    result = ((re.search(r'http://tinyurl.com/\w{1,250}', s)).group())
    if (alias not in result):
        print("\tUnfortunately, tinyurl.com/" + alias + " is already taken, " + result[7:] + " was used instead.")
    return result

if __name__ == '__main__':
    main()

