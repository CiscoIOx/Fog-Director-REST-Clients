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
def refresh_devices_discovered_with_error(ip,token):
    url = "https://%s/api/v1/appmgr/devices?offset=0&limit=10000" % ip
    headers = {'x-token-id':token,'content-type': 'application/json'}
    r=requests.get(url,headers=headers,verify=False)
    print(r.status_code)
    devices=json.loads((json.dumps(r.json())))
    print("number of devices available in FD:%d",len(devices['data']))
    for index in range(len(devices['data'])):
        device_id=devices['data'][index]['deviceId']
        if devices['data'][index]['status']=='DISCOVERED_WITH_ERROR':
            ip_addr=devices['data'][index]['ipAddress']
            print(str(device_id))
            print(str(ip_addr))
            url1 = "https://%s/api/v1/appmgr/devices/%s/action" % (ip, str(device_id))
            r=requests.post(url1,headers=headers,verify=False,data=json.dumps({"actionType": "RefreshInventory"}))
            print(r.status_code)
        else:
            print("Refreshed inventory for device_id %s ") % str(device_id)

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
print "refresh devices discovered with errors"
refresh_devices_discovered_with_error(app_mgr_ip,token_id)
print "Logging out of Fog Director"
delete_token(app_mgr_ip, token_id)