"""
Copyright 2016 Ashok Kanagarasu

These are sample functions for the Cisco Fog Director REST API.
Adding tag to set of devices

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
import requests
import json
import base64
#from functions import *

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

def tag_all_devices(ip,token):
    print("=====================")
    print("step1:creating a tag first")
    print("====================")
    tag_url="https://%s/api/v1/appmgr/tags" % ip
    headers = {'x-token-id':token,'content-type': 'application/json'}
    data = {'name':'withtag'}
    r = requests.post(tag_url,data=json.dumps(data),headers=headers,verify=False)
    tags=json.loads((json.dumps(r.json())))
    print(tags)
    print(r.status_code)
    tagid=tags['tagId']
    print("=================")
    print("step2:tag all devices with the above created tag")
    print("=================")
    device_url = "https://%s/api/v1/appmgr/devices?offset=0&limit=10000" % ip
    headers = {'x-token-id':token,'content-type': 'application/json'}
    r=requests.get(device_url,headers=headers,verify=False)
    print(r.status_code)
    print("devices which are added in your FD")
    devices=json.loads((json.dumps(r.json())))
    #print(json.dumps(r.json()))
    print("number of devices added to FD:%d",len(devices['data']))
    for index in range(len(devices['data'])):
        deviceid=devices['data'][index]['deviceId']
        print(deviceid)
        tag_device_url="https://%s/api/v1/appmgr/tags/%s/devices" % (ip,str(tagid))
        headers = {'x-token-id':token,'content-type': 'application/json'}
        data = {'devices':[deviceid]}
        r = requests.post(tag_device_url,data=json.dumps(data),headers=headers,verify=False)
        print(r.status_code)
        
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
print(token_id)
print("Adding tag to set of devices")
tag_all_devices(app_mgr_ip,token_id)
print "Logging out of Fog Director"
delete_token(app_mgr_ip, token_id)
