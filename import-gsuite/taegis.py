from fileinput import filename
from oauthlib.oauth2 import BackendApplicationClient
from requests_oauthlib import OAuth2Session
import json
import requests
import os
import sys
import time
import datetime


##
## Taegis XDR Python API Module v0.61
## By Alfredo Reino
##
## v0.3 - Added support for the File Upload API
## v0.4 - Added xdr_ti_url to translate CTP URLs returned by the TI API to Taegis XDR format
## v0.5 - Added multi region support
## v0.6 - Added caching of bearer token and robust error handling
## v0.61 - Fix bug related to cached tokens
##



class XDR():

    def __init__(self, client_id, client_secret, tenant_id, region = "US1", cache_filename = "bearer_token.txt", cache_duration = 28800, sleep_between_uploads = 10):

        # Initialize
        self.client_id = client_id
        self.client_secret = client_secret
        self.tenant_id = tenant_id

        if region.upper() == "EU":
            self.endpoint = 'https://api.echo.taegis.secureworks.com'
        elif region.upper() == "US1":
            self.endpoint = 'https://api.ctpx.secureworks.com'
        elif region.upper() == "US2":
            self.endpoint = 'https://api.delta.taegis.secureworks.com'
        else:
            self.endpoint = 'https://api.ctpx.secureworks.com'

        self.token = ""

        # Authenticate and get session token

        token_filename = cache_filename
        max_duration = cache_duration # default 8 hours
        self.wait_time_between_uploads = sleep_between_uploads

        # Check if there is cached token and its age

        needsToken = False

        if os.path.exists(token_filename):
            mod_time = os.path.getmtime(token_filename)
            now_time = int(time.time())
            delta = int(now_time - mod_time)
            print(datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M:%S") + '  ' + "-- Cached token found (" + str(delta) + " seconds old, max is " + str(max_duration) + ")")    

            if delta < max_duration:

                # Get cached token from file

                print(datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M:%S") + '  ' + "-- Reusing cached token")    
                f = open(token_filename, 'r')
                self.token = f.read()
                f.close()
            else:
                needsToken = True  
        else:
            needsToken = True

        # Need to get new or refreshed token

        if needsToken:
            print(datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M:%S") + '  ' + "-- Fetching new token from API")    
        
            client = BackendApplicationClient(client_id = self.client_id)
            oauth_client = OAuth2Session(client = client)
            url = self.endpoint + '/auth/api/v2/auth/token'
            
            token = oauth_client.fetch_token(token_url = url, client_id = self.client_id, client_secret = self.client_secret)
            self.token = token['access_token']

            f = open(token_filename, "w")
            f.write(self.token)
            f.close()
            print(datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M:%S") + '  ' + "-- Token refreshed")    
     
        # Construct header for requests

        self.headers = {
                        'Accept': 'application/json', 
                        'Content-type': 'application/json', 
                        'Authorization': 'Bearer ' + self.token, 
                        'X-Tenant-Context': str(tenant_id)
                        }


    def installed():
            return(True)


    def xdr_ti_url(object_refs):
    
        url = "https://ctpx.secureworks.com/threat-intelligence-publications?id="
        object_refs = object_refs.lower()
        space = object_refs.rfind("/") + 1
        article_id = object_refs[space:]

        if space == 0 and object_refs[:5] == "tips-":
            ## CTU TIPS new
            url = url + article_id.replace("tips-", "scwx-")
        elif object_refs.find("/tip/"):
            ## CTU TIPS
            url = url + "scwx-TIPS%20" + article_id
        elif object_refs.find("/threat/"):
            ## CTU Threat Aanalysis
            url = url + "scwx-TA " + article_id
        else:
            url = ""
        
        return(url)


    def execute_query(self, querystring, variablesstring = None):

        data = { 'query': querystring, 'variables': variablesstring }
        try:
            response = requests.request(method = "POST", url = self.endpoint + '/graphql', data = json.dumps(data), headers = self.headers)
            return(response.json())
        except:
            return(False)



    def upload_file(self, sensorid, filename):
        
        ## Wait time/rate limit
        ## time.sleep(self.wait_time_between_uploads)

        ## Check if file exists, open it and get file size
        if os.path.exists(filename):
            content_length = os.path.getsize(filename)
            try:
                files = open(filename, 'rb')
            except OSError as err:
                print("OS error: {0}".format(err))
                sys.exit(2)
        else:
            print("The file does not exist") 
            sys.exit(2)

        ## Request presigned URL and headers
        s3url = self.endpoint + "/s3-signer/v1/signed-s3url?file_name=" + filename + \
            "&content_length=" + str(content_length) + \
            "&target_tenant=" + str(self.tenant_id) + \
            "&sensor_id=" + sensorid
        
        headers = {
                        'Accept': 'application/json', 
                        'Authorization': 'Bearer ' + self.token, 
                        'X-Tenant-Context': str(self.tenant_id)
                        }

        response = requests.request(method = "GET", url = s3url, headers = headers)
        res = json.loads(response.content)

        try:
            url = res['location']
        except:
            print(res)
            sys.exit(2)
        

        ## Send file to S3
        putheaders = { "Content-Length": str(content_length) }
        response = requests.put(url, data=files, headers=putheaders)

        return(response.content)