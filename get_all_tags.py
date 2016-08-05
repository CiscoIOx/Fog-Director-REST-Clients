"""
Copyright 2016 Ashok Kanagarsu

These are sample functions for the Cisco Fog Director REST API.


See: 

http://www.cisco.com/c/en/us/td/docs/routers/access/800/software/guides/iox/fog-director/reference-guide/1-0/fog_director_ref_guide.html

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

"""
#from functions import *
import requests
import json
import base64
def get_token(ip,username,password):
    #print(ip)
    url = "https://%s/api/v1/appmgr/tokenservice" % ip
    print(url)

    r = requests.post(url,auth=(username,password),verify=False)
    token=''
    if  r.status_code == 202:
        print(r.json())
        token = r.json()['token']
        #print(token)
    else:
        print("ERROR")
        print "Status code is "+str(r.status_code)
        print r.text
    return(token)

def get_all_tags(ip,token):
    url="https://%s/api/v1/appmgr/tags/" % ip
    headers = {'x-token-id':token,'content-type': 'application/json'}
    r=requests.get(url,headers=headers,verify=False)
    print(r.status_code)
    tags=json.loads((json.dumps(r.json())))
    for index in range(len(tags['data'])):
        tag_id=tags['data'][index]['tagId']
        tag_name=tags['data'][index]['name']
        print(str(tag_id))
        print(str(tag_name))

def delete_token(ip, token):
    url = "https://%s/api/v1/appmgr/tokenservice/%s" % (ip, token)
  
    headers = {'x-token-id':token,'content-type': 'application/json'}
    
    r = requests.delete(url,headers=headers,verify=False)

    if  r.status_code == 200:
        print(r.json())
    else:
        print("ERROR")
        print "Status code is "+str(r.status_code)
        print r.text
        
app_mgr_ip=raw_input("Enter app manager ip address")
username=raw_input("enter the username of your FD:")
password=raw_input("enter the password of your FD:")
print "loging to FD and fetch an TOKEN"
token_id=get_token(app_mgr_ip,username,password)
print "get all the TAG available on your FD"
get_all_tags(app_mgr_ip,token_id)
print "Logging out of Fog Director"
delete_token(app_mgr_ip, token_id)