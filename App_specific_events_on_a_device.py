"""
Copyright 2016 Ashok Kanagarasu

These are sample functions for the Cisco Fog Director REST API.
fetching app specific event on a particular device .
on GUI it is equivalent to APP down time chart on the device details page under each app section. 

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

def app_specific_events_on_a_device(ip,token,device_ip):
	#get the myapp_id of the app 
	deployed_app=raw_input("enter the name of the app installed on this device:")
	url1 = "https://%s/api/v1/appmgr/myapps?searchByName=%s" % (ip,deployed_app)
	headers = {'x-token-id':token,'content-type': 'application/json'}
	r=requests.get(url1,headers=headers,verify=False)
	print("Status code of fethcing MYAPPID REST request %d") % r.status_code
	myappinfo=json.loads((json.dumps(r.json())))
	myappid=myappinfo['myappId']

	#get device id using the device ip address . search by device ip and get the device id of it 
	url2 = "https://%s/api/v1/appmgr/devices?limit=10000&offset=0&searchByIp=%s" % (ip,device_ip)
	headers = {'x-token-id':token,'content-type': 'application/json'}
	r=requests.get(url2,headers=headers,verify=False)
	print(r.status_code)
	print("devices which are matching the ip address on your  FD")
	devices=json.loads((json.dumps(r.json())))
	for index in range(len(devices['data'])):
	    device_id=devices['data'][index]['deviceId']
	    ip_addr=devices['data'][index]['ipAddress']
	    print(str(device_id))
	    print(str(ip_addr))
	    if ip_addr==device_ip:
			url3="https://%s/api/v1/appmgr/devices/%s/events/%s?duration=m" % (ip,str(device_id),str(myappid))
			headers = {'x-token-id':token,'content-type': 'application/json'}
			r=requests.get(url3,headers=headers,verify=False)
			print("Status code of fetching app specific events on this device %s REST request %d") % (str(device_id),r.status_code)
			if r.status_code==200:
				events_list=json.loads((json.dumps(r.json())))
				if(len(events_list['detailed_events'])==0):
					print "no data available"
				else:
					for index in range(len(events_list['detailed_events'])):
						print "Message:%s EventType:%s" % (str(events_list['detailed_events'][index]['message']),str(events_list['detailed_events'][index]['eventType']))

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
device_ip=raw_input("enter the ip address of the device")
print("loging to FD and fetch an TOKEN")
token_id=get_token(app_mgr_ip,username,password)
print(token_id)
print("App secific events on a device")
app_specific_events_on_a_device(app_mgr_ip,token_id,device_ip)
print("Logging out of Fog Director")
delete_token(app_mgr_ip, token_id)