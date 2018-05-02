"""
__copyright__ = "Copyright (c) 2018 by Cisco Systems, Inc.
All rights reserved."

April 2018

These are sample functions for the Cisco Fog Director REST API.
For detailed information about the Cisco Fog Director REST-based API, see <FD IP Address>/swagger-ui/index.html

Previously, /api/v1/appmgr/localapps/{localAppId:version} and /api/v1/appmgr/myapps/{myAppId} APIs
were used for the app workflow.
Now, some of those APIs have been merged to /api/vi/appmgr/apps/{localAppId:version}. Some of these new APIs combine
two actions in a single API. All these new APIs will require the localAppId and version. If no version is provided,
then by default the latest version is used.
Below code is to
    1. Upload and publish the app (in one step)
    2. Install the app
    3. Upgrade the app package (upload and publish in one step)
    4. Upgrade the app on the devices
    5. Uninstall the app
    6. Unpublish and delete the app (in one step)

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
import time

local_app_id = '' #global variable to store the [local] app id
app_version = '' #global variable to store the app version


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

    r = requests.delete(url, headers=headers, verify=False)

    if r.status_code == 200:
        print(r.json())
    else:
        print("ERROR")
        print "Status code is " + str(r.status_code)
        print r.text


'''
Upload and publish an app in Fog Director in one step:
In the header, set 'x-publish-on-upload' to true. Default for this header is true.

Response will include information related to app; such as the localAppId, app version, memory usage, network info, etc...
'''
def upload_and_publish_app(ip, token):
    url = "https://%s/api/v1/appmgr/apps" % ip
    print "POST " + url

    headers = {'x-token-id': token,
               'x-publish-on-upload': 'true'}

    # NOTE: file name is hardcoded
    r = requests.post(url, headers=headers, files={'file': open('nt02-c_simple_ir800-lxc.tar', 'rb')}, verify=False)

    if r.status_code == 201:
        print "Response: "
        response = r.json()
        print response
        global local_app_id
        local_app_id = response['localAppId']
        global app_version
        app_version = response['version']
        print "############# App uploaded and published #############"
        print "App ID: %s      " % local_app_id
        print "App Version: %s" % app_version
    else:
        print("ERROR")
        print "Status code is " + str(r.status_code)
        print r.text

'''
Install the app
[Local] App Id and app version (separated by semicolon) are specified in the url parameter

If no app verison is specified, default is the latest published version
If my app is not there (i.e. app is not published), it will be created.
Header 'x-tag-with-app-name' will create a tag with app name if not there and tag all FD managed(non-readonly) devices
with it. Default value for this header is true.

'deploy' payload indicates that this action is to install the app

Response will return a job id.
'''
def install_app(ip, token):
    url = "https://%s/api/v1/appmgr/apps/%s:%s/action" % (ip, local_app_id, app_version)
    print "POST " + url

    headers = {'x-token-id': token, 'content-type': 'application/json'}

    # NOTE: deviceId's are hardcoded
    data = {"deploy": {"config": {}, "metricsPollingFrequency": "3600000", "startApp": True, "devices": [
        {"deviceId": "65c14a34-514b-489f-bcc6-b3c47469be2a", "resourceAsk":
            {"resources": {"profile": "c1.tiny", "cpu": 100, "memory": 32, "network": [
            {"interface-name": "eth0", "network-name": "iox-bridge0"}]}}},
        {"deviceId": "836ee6f9-c390-4229-84a3-9034639e4c44", "resourceAsk":
            {"resources": {"profile": "c1.tiny", "cpu": 100, "memory": 32, "network": [
            {"interface-name": "eth0", "network-name": "iox-bridge0"}]}}}]}}

    r = requests.post(url, data=json.dumps(data), headers=headers, verify=False)

    if r.status_code == 200:
        print "Response: "
        response = r.json()
        print response
        print "############# App installed #############"
        print "App ID: %s" % local_app_id
        print "App Version: %s" % app_version
    else:
        print("ERROR")
        print "Status code is " + str(r.status_code)
        print r.text


'''
Upload a newer version of an app and publish it
In the url, provide the [local] app id and the app version of the app whose package is being upgraded
Header 'x-publish-on-upload' is set to true. By default, it is true.

Response will include information related to app; such as the localAppId, app version, memory usage, network info, etc...
'''
def upgrade_and_publish_app_package(ip, token):
    url = "https://%s/api/v1/appmgr/apps/%s:%s/packages" % (ip, local_app_id, app_version)
    print "POST " + url

    headers = {'x-token-id': token,
               'x-publish-on-upload': 'true'}

    # NOTE: file name is hardcoded
    r = requests.post(url, headers=headers, files={'file': open('nt02-c_simple_ir800-lxc_v2.tar', 'rb')}, verify=False)

    if r.status_code == 201:
        print "Response: "
        response = r.json()
        print response
        global local_app_id
        local_app_id = response['localAppId']
        global app_version
        app_version = response['version']
        print "############# App package upgraded and published #############"
        print "App ID: %s      " % local_app_id
        print "New App Version: %s" % app_version
    else:
        print("ERROR")
        print "Status code is " + str(r.status_code)
        print r.text


'''
Upgrade the app
[Local] App Id and app version (separated by semicolon) are specified in the url parameter

If no app verison is specified, default is the latest published version
If my app is not there (i.e. app is not published), it will be created.
Header 'x-tag-with-app-name' will create a tag with app name if not there and tag all FD managed(non-readonly) devices
with it. Default value for this header is true.

'update' payload indicates this action is to upgrade the app on the specified devices. AppData and older config
will be persisted.

Response will return a job id.
'''
def upgrade_app(ip, token):
    url = "https://%s/api/v1/appmgr/apps/%s:%s/action" % (ip, local_app_id, app_version)
    print "POST " + url

    headers = {'x-token-id': token, 'content-type': 'application/json'}

    # NOTE: device IDs are hardcoded
    data = {"update": {"config": {}, "metricsPollingFrequency": "3600000", "restart": True,
            "preserveAppData": True, "persistOlderConfig": True,
          "devices": ["65c14a34-514b-489f-bcc6-b3c47469be2a", "836ee6f9-c390-4229-84a3-9034639e4c44"]}}

    r = requests.post(url, data=json.dumps(data), headers=headers, verify=False)

    if r.status_code == 200:
        print "Response: "
        response = r.json()
        print response
        print "############# App upgraded #############"
        print "App ID: %s" % local_app_id
        print "App Version: %s" % app_version
    else:
        print("ERROR")
        print "Status code is " + str(r.status_code)
        print r.text


'''
Uninstall app

Same headers and url parameters as the other api/v1/appmgr/apps/{appId:version}/action APIs

'undeploy' payload indicates that this action is to uninstall the app on the specified device(s)
Since no version is specified in the url, the latest version will be uninstalled.

Response will return a job id.
'''
def uninstall_app(ip, token):
    url = "https://%s/api/v1/appmgr/apps/%s/action" % (ip, local_app_id)
    print "POST " + url

    headers = {'x-token-id': token, 'content-type': 'application/json'}

    # NOTE: device IDs are hardcoded
    data = {"undeploy": {"devices": ["65c14a34-514b-489f-bcc6-b3c47469be2a", "836ee6f9-c390-4229-84a3-9034639e4c44"]}}

    r = requests.post(url, data=json.dumps(data), headers=headers, verify=False)

    if r.status_code == 200:
        print ("############# App uninstalled #############")
        print "App ID: %s" % local_app_id
        print "App version: %s" % app_version
    else:
        print("ERROR")
        print "Status code is " + str(r.status_code)
        print r.text


'''
Unpublish and remove an app from Fog Director in one step.
Only specifying the [local] app id in the URL. By default the latest version will be used if no version specified.

header 'x-unpublish-on-delete' indicates whether to unpublish the app before removing. Default value is true.
If the header is not present then the default is to unpublish the app before removing.

Success delete operation will return status code of 200.
'''
def unpublish_and_remove_app(ip, token):
    url = "https://%s/api/v1/appmgr/apps/%s" % (ip, local_app_id)
    print "DELETE " + url

    headers = {'x-token-id': token, 'x-unpublish-on-delete': 'true'}

    r = requests.delete(url, headers=headers, verify=False)

    if r.status_code == 200:
        print ("############# App unpublished and removed #############")
        print ("App ID: %s") % local_app_id
    else:
        print("ERROR")
        print "Status code is " + str(r.status_code)
        print r.text





app_mgr_ip = raw_input("Enter app manager ip address: ")
username = raw_input("Enter the username of your FD: ")
password = raw_input("Enter the password of your FD: ")


# Login to Fog Director
print "Login to Fog Director"
token_id = get_token(app_mgr_ip, username, password)
print(token_id)

print "######## Adding app 'nt02-c_simple' to Fog Director ########"
upload_and_publish_app(app_mgr_ip, token_id)

print "######## Installing app 'nt02-c_simple' on devices ########"
install_app(app_mgr_ip, token_id)

time.sleep(60) # wait 1 minute for the installation to complete
print "######## Upgrading app package 'nt02-c_simple' to a newer version and publishing it ########"
upgrade_and_publish_app_package(app_mgr_ip, token_id)

time.sleep(30) # wait 30 seconds for package to be upgraded
print "######## Upgrading app 'nt02-c_simple' on devices ########"
upgrade_app(app_mgr_ip, token_id)

time.sleep(60) # wait 1 minute for the upgrade to complete
print "######## Uninstalling app 'nt02-c_simple' on devices ########"
uninstall_app(app_mgr_ip, token_id)

time.sleep(60) # wait 1 minute for the uninstall to complete

print "######## Deleting app 'nt02-c_simple' from Fog Director ########"
unpublish_and_remove_app(app_mgr_ip, token_id)

print "Logging out of Fog Director"
delete_token(app_mgr_ip, token_id)