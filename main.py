from genericpath import isfile
import shutil
import requests
from bs4 import BeautifulSoup
import os.path, os
from os import system
import time
import configparser 
import json
from datetime import datetime


s = requests.session()
now = datetime.now()
starting_time = now.strftime("%H:%M:%S")

def setupConfig():
    finished = "N"
    threadDict = {}
    while finished.upper() == "N":
        threadLink = input('Please input thread link: ')
        folderName = input('Please input folder name: ')
        threadDict[threadLink] = folderName
        finished = input('Finished inputting links to monitor? (Y/N):  ')
    monitorMode = input('Monitor thread? (Y/N): ')
    print(threadDict)
    config = configparser.ConfigParser()
    config['SETTINGS'] = {'threadCollection': threadDict,
    "MonitorMode": monitorMode}
    with open('settings.ini', 'w') as configfile:
        config.write(configfile)
    return True

def loadConfig():
    if os.path.isfile('./settings.ini') != True:
        setupConfig()
        newSetup = True
    else:
        newSetup = False
    if newSetup != True:
        lastConfig = input('Use previous settings? (Y/N): ')
        if lastConfig.upper() == "N":
            setupConfig()
        else:
            print("Using last known settings...")

    config = configparser.ConfigParser()
    config.sections()
    config.read('settings.ini')
    threadNumber = config['SETTINGS']["ThreadLink"]
    monitorMode = config['SETTINGS']['MonitorMode']
    folderName = config['SETTINGS']['FolderName']
    while threadNumber == '' or monitorMode == '' or folderName == '':
        print("Invalid config, starting setup...")
        setupConfig()
        config.read('settings.ini')
        threadNumber = config['SETTINGS']["ThreadLink"]
        monitorMode = config['SETTINGS']['MonitorMode']
        folderName = config['SETTINGS']['FolderName']

    return threadNumber, monitorMode, folderName

def loadConfig2():
    if os.path.isfile('./settings.ini') != True:
        setupConfig()
        newSetup = True
    else:
        newSetup = False
    if newSetup != True:
        lastConfig = input('Use previous settings? (Y/N): ')
        if lastConfig.upper() == "N":
            setupConfig()
        else:
            print("Using last known settings...")

    config = configparser.ConfigParser()
    config.sections()
    config.read('settings.ini')
    monitorMode = config['SETTINGS']['MonitorMode']
    linkDict = json.loads(config['SETTINGS']["threadCollection"].replace("'", '"'))
    return linkDict, monitorMode

def checkFolderPath(folderName):
    imageFolderPath = f'./{folderName}/'

    if os.path.isdir(imageFolderPath) != True:
        print(f'Creating new directory at {imageFolderPath}')
        os.mkdir(imageFolderPath)
        time.sleep(3)
    # else:
        # print('Storing images in previously created folder')

def getImageLinksFromThread(threadLink):
    try:
        thread = s.get(threadLink).text
    except Exception as e:
        print(e)
        return False
        
    imageLinks = []
    soup = BeautifulSoup(thread, "html.parser")
    imageElements = soup.find_all('a', class_="fileThumb")

    for link in imageElements:
        if link.has_attr('href'):
            imageLinks.append("https:" + link['href'])
    return imageLinks

def downloadImage(folder, imageLink):
    fileName = imageLink.split("/")[-1]
    if checkDuplicate(folder, fileName) != True:
        response = requests.get(imageLink, stream=True)
        with open(f'./{folder}/{fileName}', 'wb') as out_file:
            shutil.copyfileobj(response.raw, out_file)
        del response
        # print(f"{fileName} succesfully downloaded.")
        time.sleep(1)
        return 1
    else:
        return 0
        # print(f'{fileName} already exists, skipping.')
    

def checkDuplicate(folderName, fileName):
    if os.path.isfile(f'./{folderName}/{fileName}') == True:
        return True
    else:
        return False

thread, monitor = loadConfig2()
if monitor.upper() == "Y":
    totalImages = 0
    while True:
        print("Monitor mode started. Refreshing every 300 seconds.")
        for key, value in thread.items():
            print(f"Downloading images from {key}...")
            downloadedFiles = 0
            checkFolderPath(value)
            imageLinks = getImageLinksFromThread(key)
            for image in imageLinks:
                downloadedFiles += downloadImage(value, image)
            print(f"{downloadedFiles} new files succesfully downloaded to folder {value}")
            totalImages += downloadedFiles
        print(f"{totalImages} new images downloaded as of {starting_time}")
        print("Sleeping for 300 seconds.")
        time.sleep(300)
        system('cls')

#     while True:
#         imageLinks = getImageLinksFromThread(thread)
#         for image in imageLinks:
#             downloadImage(folder, image)
#         print("Sleeping for 180 seconds.")
#         time.sleep(180)
# else:
#     print("Regular mode started.")
#     imageLinks = getImageLinksFromThread(thread)
#     for image in imageLinks:
#         downloadImage(folder, image)
