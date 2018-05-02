"""
__copyright__ = "Copyright (c) 2018 by Cisco Systems, Inc.
All rights reserved."

April 2018

(This script is modified from the install_start_stop_app_in_fd.py)
These are sample functions for the Cisco Fog Director REST API.
For detailed information about the Cisco Fog Director REST-based API, see <FD IP Address>/swagger-ui/index.html

Below code is to
    1. Store appdata (files) locally in FD (these files will be specified in deploy payload to be uploaded on the app)
	2. Install a published app in FD onto a device
	   As part of the deploy payload, under the appDataInfo section, specify the file(s) which are to be
	   uploaded to the app after the app is activated. These files should first have been stored locally in FD using step #1
	3. Stop the app
	4. Start the app
	5. Uninstall the app installed above from the device

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


def get_token(ip, username, password):
    # print(ip)
    url = "https://%s/api/v1/appmgr/tokenservice" % ip
    print(url)

    r = requests.post(url, auth=(username, password), verify=False)
    token = ''
    if r.status_code == 202:
        print(r.json())
        token = r.json()['token']
        # print(token)
    else:
        print("ERROR")
        print "Status code is " + str(r.status_code)
        print r.text
    return (token)


def delete_token(ip, token):
    url = "https://%s/api/v1/appmgr/tokenservice/%s" % (ip, token)

    headers = {'x-token-id': token, 'content-type': 'application/json'}

    r = requests.get(url, headers=headers, verify=False)

    if r.status_code == 200:
        print(r.json())
    else:
        print("ERROR")
        print "Status code is " + str(r.status_code)
        print r.text


def is_myapp_present(ip, token, myapp_name):
    url = "https://%s/api/v1/appmgr/myapps?searchByName=%s" % (ip, myapp_name)
    headers = {'x-token-id': token, 'content-type': 'application/json'}
    r = requests.get(url, headers=headers, verify=False)
    print(r.status_code)
    print r.text
    if r.text == '{}':
        return False
    else:
        return True


def get_app_details(ip, token, appname):
    url = "https://%s/api/v1/appmgr/localapps?limit=100" % ip
    headers = {'x-token-id': token, 'content-type': 'application/json'}
    r = requests.get(url, headers=headers, verify=False)
    print(r.status_code)

    apps = json.loads((json.dumps(r.json())))

    for index in range(len(apps['data'])):
        if (appname == apps['data'][index]['name']):
            return apps['data'][index]

    return None


def get_myapp_details(ip, token, myapp_name):
    url = "https://%s/api/v1/appmgr/myapps?searchByName=%s" % (ip, myapp_name)
    headers = {'x-token-id': token, 'content-type': 'application/json'}
    r = requests.get(url, headers=headers, verify=False)
    print(r.status_code)
    return json.loads((json.dumps(r.json())))


def get_device_details(ip, token, deviceip):
    url = "https://%s/api/v1/appmgr/devices" % ip
    headers = {'x-token-id': token, 'content-type': 'application/json'}
    r = requests.get(url, headers=headers, verify=False)
    print(r.status_code)

    devices = json.loads((json.dumps(r.json())))

    for index in range(len(devices['data'])):
        if (deviceip == devices['data'][index]['ipAddress']):
            return devices['data'][index]


def create_myapp(ip, token, appname):
    url = "https://%s/api/v1/appmgr/myapps" % ip
    headers = {'x-token-id': token, 'content-type': 'application/json'}

    app_details = get_app_details(ip, token, appname)

    data = {"name": appname, "sourceAppName": "c36d727c-e9c5-46ed-bc7e-cbdd5cf49786:1.0", "version": "1.0",
            "appSourceType": "LOCAL_APPSTORE"}
    data["name"] = appname
    data["sourceAppName"] = app_details["localAppId"] + ":" + app_details["version"]
    data["version"] = app_details["version"]

    print "data is "
    print json.dumps(data)
    r = requests.post(url, data=json.dumps(data), headers=headers, verify=False)
    print "create_myapp response"
    print r.text

'''
Upload the appdata (files) locally in FD
Later on, these files will be uploaded to the app after app is deployed and activated on the device

Two files are stored locally. They have been given new file names: abc_v1.txt and abc_v2.txt
'''
def upload_appdata_locally(ip, token, localappid):
    print "Storing appdata file locally in FD"
    url = "https://%s/api/v1/appmgr/localapps/%s/localAppdata" % (ip, localappid)
    print "url " + url

    headers = {
        'x-token-id': token
    }


    # NOTE: files are hardcoded. Provide your own files.
    files = [('files', open('sample1.txt', 'rb')),
             ('files', open('sample2.txt', 'rb'))]

    payload = {
        'newfilenames': ['abc_v1.txt', 'abc_v2.txt']
    }

    response = requests.request("POST", url, files=files, data=payload, headers=headers, verify=False)
    print "response: "
    print(response.text)

'''
Install the app.

As part of the deploy payload, include appDataInfo section.
appDataInfo section will include the names of the files to be uploaded.
Those files first should have been stored locally inside FD.

After the app is deployed and activated:
first file (abc_v1.txt) will be stored under /data/appdata/
second file (abc_v2.txt) will be stored under /data/appdata/foo/bar
'''
def install_app(ip, token, appname, deviceip):
    print "Check whether myapp present in FD"
    myapp_present = is_myapp_present(ip, token, appname)

    if myapp_present != True:
        print "Creating myapp"
        create_myapp(ip, token, appname)

    myapp_details = get_myapp_details(ip, token, appname)
    device_details = get_device_details(ip, token, deviceip)

    url = "https://%s/api/v1/appmgr/myapps/%s/action" % (ip, myapp_details['myappId'])
    print "url " + url
    headers = {'x-token-id': token, 'content-type': 'application/json'}

    data = {"deploy": {"config": {}, "metricsPollingFrequency": "3600000", "startApp": True, "devices": [
        {"deviceId": "7", "resourceAsk": {"resources": {"profile": "c1.tiny", "cpu": 100, "memory": 32, "network": [
            {"interface-name": "eth0", "network-name": "iox-bridge0"}]}}}],
             "appDataInfo":{"filePaths":["", "foo/bar"], "fileNames":["abc_v1.txt", "abc_v2.txt"]}}}
    data["deploy"]["devices"][0]["deviceId"] = device_details['deviceId']

    r = requests.post(url, data=json.dumps(data), headers=headers, verify=False)
    print "response"
    print r.text


def uninstall_app(ip, token, appname, deviceip):
    myapp_details = get_myapp_details(ip, token, appname)
    device_details = get_device_details(ip, token, deviceip)

    url = "https://%s/api/v1/appmgr/myapps/%s/action" % (ip, myapp_details['myappId'])
    print "url " + url
    headers = {'x-token-id': token, 'content-type': 'application/json'}

    data = {"undeploy": {"devices": [9]}}
    data["undeploy"]["devices"][0] = device_details['deviceId']

    print "uninstall data"
    print json.dumps(data)
    r = requests.post(url, data=json.dumps(data), headers=headers, verify=False)
    print "response"
    print r.text


def stop_app(ip, token, appname):
    myapp_details = get_myapp_details(ip, token, appname)

    url = "https://%s/api/v1/appmgr/myapps/%s/action" % (ip, myapp_details['myappId'])
    print "url " + url
    headers = {'x-token-id': token, 'content-type': 'application/json'}

    data = {"stop": {}}

    print "Stop data"
    print json.dumps(data)
    r = requests.post(url, data=json.dumps(data), headers=headers, verify=False)
    print "response"
    print r.text


def start_app(ip, token, appname):
    myapp_details = get_myapp_details(ip, token, appname)

    url = "https://%s/api/v1/appmgr/myapps/%s/action" % (ip, myapp_details['myappId'])
    print "url " + url
    headers = {'x-token-id': token, 'content-type': 'application/json'}

    data = {"start": {}}

    print "Start data"
    print json.dumps(data)
    r = requests.post(url, data=json.dumps(data), headers=headers, verify=False)
    print "response"
    print r.text


app_mgr_ip = raw_input("Enter app manager ip address: ")
username = raw_input("Enter the username of your FD: ")
password = raw_input("Enter the password of your FD: ")
appname = raw_input("Enter the published LXC App Name in your FD: ")
local_app_id = raw_input("Enter localapp id in the format {appId:version}: ")
deviceip = raw_input("Enter the device ip to install App: ")

# Login to Fog Director
print "Login to Fog Director"
token_id = get_token(app_mgr_ip, username, password)
print(token_id)

upload_appdata_locally(app_mgr_ip, token_id, local_app_id)
install_app(app_mgr_ip, token_id, appname, deviceip)
stop_app(app_mgr_ip, token_id, appname)
start_app(app_mgr_ip, token_id, appname)
uninstall_app(app_mgr_ip, token_id, appname, deviceip)

print "Logging out of Fog Director"
delete_token(app_mgr_ip, token_id)