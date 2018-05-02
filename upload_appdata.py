"""
__copyright__ = "Copyright (c) 2018 by Cisco Systems, Inc.
All rights reserved."

April 2018

(This script is modified from the device_specific_events.py script)

These are sample functions for the Cisco Fog Director REST API.
For detailed information about the Cisco Fog Director REST-based API, see <FD IP Address>/swagger-ui/index.html
This script demonstrates how to upload appdata (files) for an app on both multiple devices and a single device.

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
# from functions import *
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

'''
Upload files on multiple devices.

This will upload two files on two devices.
The name of the first file will remain the same; but the name of the second file will change to  'abc_v2.txt'
First file will go under /data/appdata/foo and second file will go under /data/appdata
All the appdata will be deleted before these files are uploaded because 'deleteAllAppdata' flag is set to true.

This request will return a job id.
'''
def upload_appdata_on_multiple_devices(ip, token):
    # NOTE: app id and device id's are hardcoded here. Provide your own app id and device id's.
    # see sample codes for App Monitoring to see how the app id is fetched using app name.
    # see sample codes for Device Specific App Actions to see how the device id is fetched used device ip.
    app_id = "7219"
    url = "https://%s/api/v1/appmgr/myapps/%s/appdata" % (ip, app_id)
    print "url " + url

    headers = {
        'x-token-id': token
    }

    # NOTE: files are hardcoded. Provide your own files
    files = [('files', open('sample1.txt', 'rb')),
             ('files', open('sample2.txt', 'rb'))]

    payload = {
        'devices': ['3fa6fdcc-8e8b-463f-a54b-2ae446008e1e', '1872fbcb-5974-41c2-989c-2e3309e83982'],
       	'newfilenames': ['','abc_v2.txt'],
       	'filepaths': ['foo',''],
       	'deleteAllAppdata': 'true'
    }

    response = requests.request("POST", url, files=files, data=payload, headers=headers, verify=False)
    print "response: "
    print(response.text)


'''
Upload files on a single device. It will immediately respond with whether the file uploaded or not.

This will upload two files on a single device.
Both files will go under /data/appdata/foo/bar
Both of the files will retain their original names since no newfilenames are specified.
Existing appdata will not be deleted since deleteAllAppdata flag is not specified. By default that flag is false.

This request will return a message to indicate whether file upload was success or not.
'''
def upload_appdata_on_single_device(ip, token):
    # NOTE: app id and device id's are hardcoded here. Provide your own app id and device id's.
    # see sample codes for App Monitoring to see how the app id is fetched using app name.
    # see sample codes for Device Specific App Actions to see how the device id is fetched used device ip.
    device_id = "1872fbcb-5974-41c2-989c-2e3309e83982"
    app_id = "7219"
    url = "https://%s/api/v1/appmgr/devices/%s/apps/%s/appdata" % (ip, device_id, app_id)
    print "url " + url

    headers = {
        'x-token-id': token
    }

    # NOTE: files are hardcoded. Provide your own files.
    files = [('files', open('sample1.txt', 'rb')),
             ('files', open('sample2.txt', 'rb'))]

    payload = {
        'filepaths': ['foo/bar', 'foo/bar']
    }

    response = requests.request("POST", url, files=files, data=payload, headers=headers, verify=False)
    print "response: "
    print(response.text)


def delete_token(ip, token):
    url = "https://%s/api/v1/appmgr/tokenservice/%s" % (ip, token)

    headers = {'x-token-id': token, 'content-type': 'application/json'}

    r = requests.delete(url, headers=headers, verify=False)

    if r.status_code == 200:
        print(r.json())
    else:
        print("ERROR")
        print "Status code is " + str(r.status_code)
        print r.text


app_mgr_ip = raw_input("Enter app manager ip address: ")
username = raw_input("enter the username of your FD: ")
password = raw_input("enter the password of your FD: ")
print("loging to FD and fetch an TOKEN")
token_id = get_token(app_mgr_ip, username, password)
print(token_id)
upload_appdata_on_multiple_devices(app_mgr_ip, token_id)
upload_appdata_on_single_device(app_mgr_ip, token_id)
print("Logging out of Fog Director")
delete_token(app_mgr_ip, token_id)
