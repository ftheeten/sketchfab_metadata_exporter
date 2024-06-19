#!/usr/bin/python3

"""Sample script for uploading to Sketchfab using the V3 API and the requests library."""

import json
from time import sleep

# import the requests library
# http://docs.python-requests.org/en/latest
# pip install requests
import requests, argparse, json
from requests.exceptions import RequestException

##
# Uploading a model to Sketchfab is a two step process
#
# 1. Upload a model. If the upload is successful, the API will return
#    the model's uid in the `Location` header, and the model will be placed in the processing queue
#
# 2. Poll for the processing status
#    You can use your model id (see 1.) to poll the model processing status
#    The processing status can be one of the following:
#    - PENDING: the model is in the processing queue
#    - PROCESSING: the model is being processed
#    - SUCCESSED: the model has being sucessfully processed and can be view on sketchfab.com
#    - FAILED: the processing has failed. An error message detailing the reason for the failure
#              will be returned with the response
#
# HINTS
# - limit the rate at which you poll for the status (once every few seconds is more than enough)
##


SERVICE_URL="https://sketchfab.com/v3/me/models"

SERVICE_URL_DOWNLOAD="https://sketchfab.com/v3/models"
DOWNLOAD_FOLDER="C:\\Users\\ftheeten\\Downloads\\DW_SKETCHFAB"
GLOBAL_CPT=1
RESULT=[]

def parse_detail(json):
    global RESULT
    i=0
    for record in json:
        line={}
        #print(record["name"])
        line["name"]=str(record["name"])
        line["uid"]=str(record["uid"])
        line["uri"]=str(record["uri"])
        categ=[]
        for item in record["categories"]:
            categ.append(str(item["name"]))
        line["categories"]=";".join(categ)
        line["description"]=str(record["description"])
        line["vertexCount"]=str(record["vertexCount"])
        line["faceCount"]=str(record["faceCount"])
        line["viewerUrl"]=str(record["viewerUrl"])
        line["viewCount"]=str(record["viewCount"])
        line["likeCount"]=str(record["likeCount"])
        line["isPrivate"]=str(record["isPrivate"])
        line["createdAt"]=str(record["createdAt"])
        line["publishedAt"]=str(record["publishedAt"])
        #print(line)
        line = {key: value.replace("\r","").replace("\n","") for key, value in line.items()}
        RESULT.append(line)
        i=i+1
        #if i>4:
        #    return

def parse(TOKEN, url , i):
    global GLOBAL_CPT
    headers = {'Authorization': f'Token {TOKEN}'}
    headers.update({'Content-Type': 'application/json', 'Accept-Charset':'utf-8'})
    data=requests.get(url, headers=headers)
    dict=json.loads(data.text) #.encode('utf8').decode('ascii', 'ignore'))
    #print(dict)
    print("page")
    next=dict["next"]
    print(next)
    print(GLOBAL_CPT)
    GLOBAL_CPT=GLOBAL_CPT+1
    parse_detail(dict["results"])
    if next: 
        
        i=i+1
        #if i>4:
        #    return
        parse(TOKEN, next, i)
        
        
def download(TOKEN, url):
    global GLOBAL_CPT
    global DOWNLOAD_FOLDER
    headers = {'Authorization': f'Token {TOKEN}'}
    headers.update({'Content-Type': 'application/json', 'Accept-Charset':'utf-8'})
    data=requests.get(url, headers=headers)
    print(data.text)
    dict=json.loads(data.text)
    returned=False
    if "source" in dict:
        if "url" in dict["source"]:
            download_link=dict["source"]["url"]
            print(download_link)
            if download_link.find('/'):
                name_file=download_link.rsplit('/', 1)[1]
                name_file=name_file.split("?")[0]
                
                returned=True
                r = requests.get(download_link)  
                target_location=DOWNLOAD_FOLDER+"\\"+name_file
                print(target_location)
                with open(target_location, 'wb') as f:
                    f.write(r.content)
    sleep(10)
    return returned
    #if next:
    #    parse(TOKEN, next, 0)

def create_file(token):
    global RESULT
    global SERVICE_URL_DOWNLOAD
    #print(RESULT)
    for line in RESULT:
        uuid=line["uid"]
        name=line["name"]
        print(name)
        download_uri=SERVICE_URL_DOWNLOAD+"/"+uuid+"/download"
        print(download_uri)
        dw=download(token, download_uri)
        if not dw:
            print(line)
    '''
    file=open(p_file, 'w', encoding="utf-8")
    i=0
    
    for line in RESULT:
        if i==0:
            file.write("\t".join(line.keys()))
        file.write("\n")
        file.write("\t".join(line.values()))
        i=i+1
    file.close()
    '''
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--token")
    #parser.add_argument("--output_file")
    args = parser.parse_args()
    parse(args.token, SERVICE_URL,0)
    create_file(args.token)