"""
Copyright 2016 Ashok Kanagarasu

These are sample functions for the Cisco Fog Director REST API.
For adding set of devices into FD without tag. 
Follwing script will add 4 devices 192.168.1.1-192.168.1.4 
if you wanted to change the range of the ip address . please change in add_device function on line 
ip_range = ipRange("192.168.1.1", "192.168.1.4")

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

def ipRange(start_ip, end_ip):
   start = list(map(int, start_ip.split(".")))
   end = list(map(int, end_ip.split(".")))
   temp = start
   ip_range = []

   ip_range.append(start_ip)
   while temp != end:
      start[3] += 1
      for i in (3, 2, 1):
         if temp[i] == 256:
            temp[i] = 0
            temp[i-1] += 1
      ip_range.append(".".join(map(str, temp)))

   return ip_range

def add_device(ip,token):
    print("add devices")
    ip_range = ipRange("192.168.1.1", "192.168.1.4")
    print(ip_range)
    for device_ip in ip_range:
        #print("inside for")
        url = "https://%s/api/v1/appmgr/devices" % ip
        headers = {'x-token-id':token,'content-type': 'application/json'}
        data = {'port':'8888','ipAddress':device_ip,'username':'t','password':'t'}
        r = requests.post(url,data=json.dumps(data),headers=headers,verify=False)
        print(r.status_code)
        if r.status_code==201:
           print("Device added successfully")
        else:
           r.raise_for_status()

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
print("Adding the set of devices into FD")
add_device(app_mgr_ip,token_id)
print "Logging out of Fog Director"
delete_token(app_mgr_ip, token_id)
