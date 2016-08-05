"""
Copyright 2016 Ashok Kanagarsu

These are sample functions for the Cisco Fog Director REST API.
editing package_config.ini contenet on all the devices where the app is installed.
on GUI it is equivalent to -- editing the package_config.ini content from app config page .
which does on all the devices selected.

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

def edit_config(ip,token):
   deployed_app=raw_input("enter the name of the app installed on a device:")
   
   url = "https://%s/api/v1/appmgr/myapps?searchByName=%s" % (ip,deployed_app)
   headers = {'x-token-id':token,'content-type': 'application/json'}
   r=requests.get(url,headers=headers,verify=False)
   print("Status code of fethcing MYAPPID REST request %d") % r.status_code
   myappinfo=json.loads((json.dumps(r.json())))
   myappid=myappinfo['myappId']

   url2="https://%s/api/v1/appmgr/devices?limit=5&offset=0&searchByApp=%s&searchByStatus=STOPPED,DEPLOYED,RUNNING,STOP_FAILED,START_FAILED,UNDEPLOY_FAILED,UPGRADE_FAILED,CONFIGURATION_FAILED,RESOURCE_ALLOCATION_FAILED" % (ip,deployed_app)
   headers = {'x-token-id':token,'content-type': 'application/json'}
   r=requests.get(url2,headers=headers,verify=False)
   print("status code of fetching the device list on which the give app is deployed %d") % r.status_code
   devices=json.loads((json.dumps(r.json())))
   print("number of devices where the given app is deployed :%d") % len(devices['data'])
   
   devices_list = []
   for index in range(len(devices['data'])):
     device_id=devices['data'][index]['deviceId']
     ip_addr=devices['data'][index]['ipAddress']
     print(str(device_id))
     print(str(ip_addr))
     devices_list.append(device_id)

   url3="https://10.78.106.21/api/v1/appmgr/myapps/%s/action" % myappid
   data={'updateConfig':{'restart':'true','devices':devices_list,'config':{'default':{'abc':'newtext2'}}}}
   r = requests.post(url3,data=json.dumps(data),headers=headers,verify=False)
   print("Status code on updating the config on the all the devices where this app is deployed: %d") % r.status_code

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
print "editing package_config.ini contenet on all the devices where the app is installed"
edit_config(app_mgr_ip,token_id)
print "Logging out of Fog Director"
delete_token(app_mgr_ip, token_id)

