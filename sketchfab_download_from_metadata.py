#!/usr/bin/python3

import json
from time import sleep
import datetime
# import the requests library
# http://docs.python-requests.org/en/latest
# pip install requests
import requests, argparse, json
from requests.exceptions import RequestException
import pandas as pnd


GLOBAL_I = None
SERVICE_URL_DOWNLOAD="https://sketchfab.com/v3/models"

def download(p_token, url, p_download_folder):
    global GLOBAL_CPT
    headers = {'Authorization': f'Token {p_token}'}
    headers.update({'Content-Type': 'application/json', 'Accept-Charset':'utf-8'})
    data=requests.get(url, headers=headers)
    print(data.text)
    dict=json.loads(data.text)
    returned=False
    name_file=""
    if "source" in dict:
        if "url" in dict["source"]:
            download_link=dict["source"]["url"]
            print(download_link)
            if download_link.find('/'):
                name_file=download_link.rsplit('/', 1)[1]
                name_file=name_file.split("?")[0]
                
                returned=True
                r = requests.get(download_link)  
                target_location=p_download_folder+"\\"+name_file
                print(target_location)
                with open(target_location, 'wb') as f:
                    f.write(r.content)
    return returned, name_file

def read_metadata_and_download(p_token, p_input_file, p_output_file, p_download_folder):
    global GLOBAL_I
    global SERVICE_URL_DOWNLOAD
    GLOBAL_I=0
    pnd_source=pnd.read_csv(p_input_file, sep='\t', lineterminator='\r')
    print(pnd_source)
    pnd_source
    pnd_source['isDownloadable'] = pnd_source['isDownloadable'].replace({True: 'true', False: 'false'})
    #pnd_source['isDownloadable'] = pnd_source['isDownloadable'].str.lower()
    pnd_source=pnd_source.loc[pnd_source['isDownloadable'] == "true"]
    for i, row in pnd_source.iterrows():
        uuid=row["uid"]
        print(uuid)
        download_uri=SERVICE_URL_DOWNLOAD+"/"+uuid+"/download"
        
        f = open(p_output_file, "a")
        
        flag_dw, name_file=download(p_token, download_uri, p_download_folder)
        now = datetime.datetime.now()
        time_str=now.strftime("%Y-%m-%d %H:%M:%S")
        if flag_dw:
            print("true")
            f.write("\n"+"\t".join([str(uuid), "true",name_file, time_str]))
        else:
            print("false")
            f.write("\n"+"\t".join([str(uuid), "false",name_file, time_str]))
        f.close() 
        if GLOBAL_I%200==0 and GLOBAL_I >0:
            sleep(120)
        else:
            sleep(10)
        GLOBAL_I=GLOBAL_I+1

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--token")
    parser.add_argument("--input_file")
    parser.add_argument("--output_file")
    parser.add_argument("--download_folder")
    args = parser.parse_args()
    f = open(args.output_file, "w")   # 'r' for reading and 'w' for writing
    f.write("uuid\tdownloaded\tfile\tdate")
    f.close()                          
    read_metadata_and_download(args.token, args.input_file,args.output_file, args.download_folder )
