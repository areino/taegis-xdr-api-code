from taegis import XDR
import creds
import os
import datetime
import sys
import json
import googleapiclient.discovery
from oauth2client.service_account import ServiceAccountCredentials


## v0.1 - Initial version
## v0.2 - Change CSV to JSON


def log(s):
    print(datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M:%S") + '  ' + str(s))

def readUploaded():
    global already_uploaded

    if os.path.exists(creds.already_uploaded_file):
        with open(creds.already_uploaded_file, 'r') as f:
            for row in f:
                if row[:-2].strip() != "":
                    already_uploaded.append(row.strip().lower())

    already_uploaded = list(dict.fromkeys(already_uploaded))
    return(len(already_uploaded))

def noteUploaded(alertid):
    with open(creds.already_uploaded_file, 'a') as f:
        f.write(alertid + '\n')

def alreadyUploaded(alertid):
    global already_uploaded
    
    if (alertid) in already_uploaded:
        return(True)
    else:
        return(False)

def writeWorkingFile(event):
    with open(creds.working_file, 'a') as f:
        f.write(event + '\n')

    
#############################################################
#############################################################
## Main workflow

log("-- Initializing...")

already_uploaded = []
count = 0


# Initialize working file

if not os.path.exists(creds.working_file):
    with open(creds.working_file, "w") as f:
        f.write("\n")

# Open list of files already uploaded to Taegis XDR

log("-- Already uploaded: " + str(readUploaded()))

# Connect to Google Alert Center API 

log("-- Connecting to Google Alert Center API...")

credentials = ServiceAccountCredentials.from_json_keyfile_name('creds.json')
delegated_credentials = credentials.create_delegated('areino@ibium.eu').create_scoped('https://www.googleapis.com/auth/apps.alerts')
alertcli = googleapiclient.discovery.build('alertcenter', 'v1beta1', credentials=delegated_credentials, cache_discovery=False)

## Get alerts

response = alertcli.alerts().list().execute()

if creds.debug:
    with open(creds.working_file_json, 'w') as f:
        f.write(json.dumps(response, indent=4))

alerts = response.get("alerts")
if alerts:
    for alert in alerts:

        alertid = alert["alertId"]
        customerid = alert["customerId"]
        createtime = alert["createTime"]
        starttime = alert["startTime"]
        updatetime = alert["updateTime"]
        type = alert["type"]
        source = alert["source"]

        try:
            email = alert["data"]["email"]
        except:
            email = ""

        try:
            ipaddress = alert["data"]["loginDetails"]["ipAddress"]
        except:
            ipaddress = ""

        try:
            severity = alert["metadata"]["severity"]
        except:
            severity = ""

        if not alreadyUploaded(alertid):
            # Construct log
            log("-- Alert " + alertid)

            event = "GSUITE," + alertid + "," + customerid + "," 
            event = event + createtime  + "," + starttime + "," + updatetime + ","
            event = event + type  + "," + source  + "," + email  + "," + ipaddress  + "," + severity

            # Add to working file
            writeWorkingFile(event)

            # Note down the alertid to keep track of events already uploaded
            noteUploaded(alertid)

            count = count + 1

if count > 0:
    # Initialize API connection

    try:
        api = XDR(client_id=creds.xdrid, client_secret=creds.xdrsecret, tenant_id=creds.xdrtenant)
    except:
        log("-- ERROR: Not able to create Taegis XDR API session, possibly invalid credentials")
        sys.exit("Cannot connect to Taegis XDR API")
    log("-- Connected to Taegis XDR (tenant: " + str(creds.xdrtenant) + ")")


    # Prepare output file
    if os.path.exists(creds.working_file):

        # Check max size of compressed file
        if os.path.getsize(creds.working_file) > creds.max_compressed_bytes:
            log("-- Log file too large for upload")
        else:
            # Upload file
            if not creds.debug:
                log("-- Uploading...")
                ret = api.upload_file("GSUITE", creds.working_file)
                if ret == b'':
                    log("-- Uploaded telemetry to Taegis!")
                else:
                    log("-- Upload failed!")
                    print(ret)
        
            # Delete file after uploaded
            if not creds.debug:
                os.remove(creds.working_file)
                os.remove(creds.working_file_json)
                log("-- Deleted working files")
else:
    log("-- Nothing new to process")

log("-- End")
