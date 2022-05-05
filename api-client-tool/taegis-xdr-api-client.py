## Client manager for Taegis XDR API

import os
import sys
import argparse
import requests
import json

## Config variables

version = '1.3'

us1_api_endpoint = "api.ctpx.secureworks.com"
us2_api_endpoint = "api.delta.taegis.secureworks.com"
eu_api_endpoint  = "api.echo.taegis.secureworks.com"

## Select region
api_endpoint = us1_api_endpoint



## CHANGELOG
## 
## v1.0 - May 10th, 2021 - Initial release
## v1.1 - May 17th, 2021 - Functionality to drop credentials file to be directly used by scripts
## v1.2 - Jan 17th, 2022 - Add multi-region support
## 

bearer_token_file = 'bearer_token.txt'
creds_file = 'creds.py'


## Initialize arguments parser

parser = argparse.ArgumentParser(description='Manage Taegis XDR API clients, version v' + version)
parser.add_argument('action', help='action to perform (GET|LIST|CREATE|DELETE|DELETEALL|ROTATE)')
parser.add_argument('client', default='', nargs='?', help='name of API client (to CREATE) or id (to GET, DELETE or ROTATE)')
args = parser.parse_args()

action = args.action.strip().lower()
client = args.client.strip().lower()


## Get access token. If file exists containing the token, we use that. 
## If not the user is asked and the token is written to the file.

fullpath = os.getcwd() + '/' + bearer_token_file
if os.path.exists(fullpath):
    ## Retrieve access token from file
    
    f = open(fullpath, 'r')
    access_token = f.read()
    f.close()

    print()
    print('Fetching access token from ' + fullpath)
    print()

    access_token = access_token.strip()
else:
    ## Get access token from user input and store in file
    
    print("Please enter the access token from a Taegis XDR open session")
    access_token = input('Token: ')
    access_token = access_token.replace('Bearer ', '')
    access_token = access_token.strip()
    
    ## Save to file
    
    print()
    print('Writing access token to ' + fullpath)
    print()
    
    f = open(fullpath, 'w')
    f.write(access_token)
    f.close()

## Initialize request headers

myheaders = {'Content-type': 'application/json', 'Authorization': 'Bearer ' + access_token}


## Check if client name or id is specified when actions are GET/DELETE/CREATE/ROTATE.
## Name/id parameter not needed for LIST.
## The action DELETEALL requires a parameter of "yes".

if client == '' and (action == 'create' or action == 'get' or action == 'delete' or action == 'rotate'):
    print('ERROR - You must specify a client name (for creating) or id (for getting, deleting or rotating)!')
    exit()

## CREATE (requires client_name as parameter)
if action == 'create':
    url =  "https://" + api_endpoint + "/clients/v1/clients"
    payload = {'name': client}
    jsonpayload = json.dumps(payload)
    
    r = requests.post(url, data = jsonpayload, headers = myheaders)
    res = json.loads(r.content)
    print(res)
    if 'error' in res:
        print('API ERROR - ' + str(res['error']))
    elif 'errors' in res:
        print('API ERROR - ' + str(res['errors']))
    else:
        print()
        print('API Endpoint:  ' + api_endpoint)
        print()
        print('ID:            ' + res['id'])
        print('Client Name:   ' + res['name'])
        print('Client Roles:  ' + res['roles'])
        print('Client Tenant: ' + res['tenant_id'])
        print()
        print('Client ID:     ' + res['client_id'])
        print('Client Secret: ' + res['client_secret'])
        print()
        print("Save ID safely, you will need it for revoking the client or rotating the secret.")
        print("Save Client ID and Client Secret safely, you will need them to access the API.")

        ## Create creds file
        print()
        create_file = input("Do you want to create a credentials file with the details? [Y|n] ") or "Y"
        if create_file.lower()[:1] == "y":
            filename = input("Enter filename for credentials file [" + creds_file + "]: ") or creds_file
            f = open(filename, "w")
            f.write('tenant=' + res['tenant_id'] + "\n")
            f.write('id=\"' + res['client_id'] + '\"\n')
            f.write('secret=\"' + res['client_secret'] + '\"\n')
            f.close()
            print("File " + filename + " written")

        quit()

## GET (requires ID as parameter)
elif action == 'get':
    url =  "https://" + api_endpoint + "/clients/v1/clients/" + client
    
    r = requests.get(url, headers = myheaders)
    res = json.loads(r.content)
    if 'error' in res:
        print('API ERROR - ' + str(res['error']))
    elif 'errors' in res:
        print('API ERROR - ' + str(res['errors']))
    else:
        print()
        print('API Endpoint:  ' + api_endpoint)
        print()
        print('ID:            ' + res['id'])
        print('Client Name:   ' + res['name'])
        print('Client Roles:  ' + res['roles'])
        print('Client Tenant: ' + res['tenant_id'])
        print('Client ID:     ' + res['client_id'])
        print('Created at:    ' + res['created_at'])
        print('Updated at:    ' + res['updated_at'])
        print()
        print("The Client Secret is not returned by the API, sorry.")
        quit()

## DELETE (requires ID as parameter)
elif action == 'delete':
    url =  "https://" + api_endpoint + "/clients/v1/clients/" + client
    
    r = requests.get(url, headers = myheaders)
    res = json.loads(r.content)
    if 'error' in res:
        print('API ERROR - ' + str(res['error']))
    elif 'errors' in res:
        print('API ERROR - ' + str(res['errors']))
    else:
        print()
        print('API Endpoint:  ' + api_endpoint)
        print()
        print('ID:            ' + res['id'])
        print('Client Name:   ' + res['name'])
        print('Client Roles:  ' + res['roles'])
        print('Client Tenant: ' + res['tenant_id'])
        print('Client ID:     ' + res['client_id'])
        print('Created at:    ' + res['created_at'])
        print('Updated at:    ' + res['updated_at'])

        url =  'https://" + api_endpoint + "/clients/v1/clients/' + client
        r = requests.delete(url, headers = myheaders)
        res = json.loads(r.content)
        if 'error' in res:
            print('API ERROR - ' + str(res['error']))
        elif 'errors' in res:
            print('API ERROR - ' + str(res['errors']))
        else:
            print("The client has been deleted.")
            quit()

## ROTATE (requires ID as parameter)
elif action == 'rotate':
    url =  "https://" + api_endpoint + "/clients/v1/clients/rotate-secret/" + client
    
    r = requests.post(url, headers = myheaders)
    res = json.loads(r.content)
    if 'error' in res:
        print('API ERROR - ' + str(res['error']))
    elif 'errors' in res:
        print('API ERROR - ' + str(res['errors']))
    else:
        print()
        print('API Endpoint:  ' + api_endpoint)
        print()
        print('ID:            ' + res['id'])
        print('Client Name:   ' + res['name'])
        print('Client Tenant: ' + res['tenant_id'])
        print()
        print('Client ID:     ' + res['client_id'])
        print('Client Secret: ' + res['client_secret'])
        print()
        print("Save Client ID and Client Secret safely, you will need them to access the API.")
        quit()

## LIST (no parameter required)
elif action == 'list':
    url =  "https://" + api_endpoint + "/clients/v1/clients/list"
    
    r = requests.post(url, headers = myheaders)
    res = json.loads(r.content)
    if 'error' in res:
        print('API ERROR - ' + str(res['error']))
    elif 'errors' in res:
        print('API ERROR - ' + str(res['errors']))
    else:
        hasResults = False
        print()
        print('API Endpoint:  ' + api_endpoint)
        for cli in res:
            hasResults = True
            print()
            print('ID:            ' + cli['id'])
            print('Client Name:   ' + cli['name'])
            print('Client Tenant: ' + cli['tenant_id'])
            print('Created at:    ' + cli['created_at'])
            print('Updated at:    ' + cli['updated_at'])
            print('Client ID:     ' + cli['client_id'])
        if not hasResults:
            print("No clients found!")
    quit()

## DELETEALL (requires a second parameter of YES)
elif action == 'deleteall' and client == 'yes':
    url =  "https://" + api_endpoint + "/clients/v1/clients/list"
    
    r = requests.post(url, headers = myheaders)
    res = json.loads(r.content)
    if 'error' in res:
        print('API ERROR - ' + str(res['error']))
    elif 'errors' in res:
        print('API ERROR - ' + str(res['errors']))
    else:
        hasResults = False
        print()
        print('API Endpoint:  ' + api_endpoint)
        for cli in res:
            hasResults = True
            print()
            print('ID:            ' + cli['id'])
            print('Client Name:   ' + cli['name'])
            print('Client Tenant: ' + cli['tenant_id'])
            print('Created at:    ' + cli['created_at'])
            print('Updated at:    ' + cli['updated_at'])
            print('Client ID:     ' + cli['client_id'])

            url =  "https://" + api_endpoint + "/clients/v1/clients/" + cli['id']
            r = requests.delete(url, headers = myheaders)
            res = json.loads(r.content)
            if 'error' in res:
                print('API ERROR - ' + str(res['error']))
            elif 'errors' in res:
                print('API ERROR - ' + str(res['errors']))
            else:
                print("The client has been deleted.")
        if not hasResults:
            print("No clients found!")
    quit()
elif action == 'deleteall' and client != 'yes':
    print('ERROR - If you want to DELETE ALL clients, add \'yes\' to the command')
    quit()
    
## Wrong action
else:
    print('ERROR - Action must be GET, LIST, CREATE, DELETE, DELETEALL or ROTATE!')
    quit()
    

