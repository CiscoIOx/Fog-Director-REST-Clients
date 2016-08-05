"""
Copyright 2016 Ashok Kanagarasu

For this example code is for fetching the app down time chart . 
Pre-req : App should be deployed on an device  

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

def app_down_time_chart(ip,token,appname):
	#get deployed app's myapp id 	
	url = "https://%s/api/v1/appmgr/myapps?searchByName=%s" % (ip,appname)
	headers = {'x-token-id':token,'content-type': 'application/json'}
	r=requests.get(url,headers=headers,verify=False)
	print("Status code of fethcing MYAPPID REST request %d") % r.status_code
	myappinfo=json.loads((json.dumps(r.json())))
	myappid=myappinfo['myappId']

	#same URL can be modified to get "WEEK" data using duration=week and "month" as duration=month
	url2="https://%s/api/v1/appmgr/myapps/%s/events?detail=false&duration=day" % (ip,myappid)
	headers = {'x-token-id':token,'content-type': 'application/json'}
	r=requests.get(url2,headers=headers,verify=False)
	print("Status code of fethcing downtime chart for the myappid %d") % r.status_code
	if r.status_code==200:
		downtime=json.loads((json.dumps(r.json())))
		print(len(downtime['events']))
		if(len(downtime['events'])==0):
			print("App downtime data not available for last day")
		else:
			for index in range(len(downtime['events'])):
				epoch_time=downtime['events'][index]['epochTime']
				devicesUpCount=downtime['events'][index]['devicesUpCount']
				devicesDownCount=downtime['events'][index]['devicesDownCount']
				print "For Epoch_time %s  Device_up are %s and Device_down are %s" %(epoch_time,devicesUpCount,devicesDownCount)
	else:
		print"App down time chart REST request FAiled\n"    
	
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
appname=raw_input("enter the name of the deployed app:")
print("loging to FD and fetch an TOKEN")
token_id=get_token(app_mgr_ip,username,password)
print(token_id)
print("Aggregated metrics of an App")
app_down_time_chart(app_mgr_ip,token_id,appname)
print("Logging out of Fog Director")
delete_token(app_mgr_ip, token_id)