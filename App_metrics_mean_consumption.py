"""
Copyright 2016 Ashok Kanagarasu

These are sample functions for the Cisco Fog Director REST API.
get all the devices added into FD 

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

def Aggregated_metrics_of_app(ip,token,appname):
	#get deployed app's myapp id 	
	url = "https://%s/api/v1/appmgr/myapps?searchByName=%s" % (ip,appname)
	headers = {'x-token-id':token,'content-type': 'application/json'}
	r=requests.get(url,headers=headers,verify=False)
	print("Status code of fethcing MYAPPID REST request %d") % r.status_code
	myappinfo=json.loads((json.dumps(r.json())))
	myappid=myappinfo['myappId']

	#fetching mean app consumption metrics for the given myappid - day . same URL can be modified to get "WEEK" data using duration=week and "month" as duration=month
	#in the below URL 
	url2="https://%s/api/v1/appmgr/myapps/%s/metrics?detail=false&duration=d" % (ip,myappid)
	headers = {'x-token-id':token,'content-type': 'application/json'}
	r=requests.get(url2,headers=headers,verify=False)
	print("Status code of fethcing DAY aggregated metrics for the myappid %d") % r.status_code
	if r.status_code==200:
		metrics=json.loads((json.dumps(r.json())))
		print("mean CPU metrics for a day \n")
		print(metrics['cpu'])
		print("mean Memory metrics for a day \n")
		print(metrics['memory'])
		print("mean Disk metrics for a day \n")
		print(metrics['disk'])
		print("mean Network consumption for a day \n")
		print(metrics['network'])
	else:
		print("Mean metrics REST request failed")

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
appname=raw_input("enter the name of the deployed app for which the aggregated metrics is needed")
print("loging to FD and fetch an TOKEN")
token_id=get_token(app_mgr_ip,username,password)
print(token_id)
print("Aggregated metrics of an App")
Aggregated_metrics_of_app(app_mgr_ip,token_id,appname)
print("Logging out of Fog Director")
delete_token(app_mgr_ip, token_id)