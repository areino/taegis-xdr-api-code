from taegis import XDR
import creds
import os
import datetime
import sys
import requests



## v0.1 - Initial version


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

def key_value(set, key_name, default_value):
    try:
        ret = set[key_name]
    except:
        ret = default_value
    
    return(str(ret))


def format_timestamp(seconds):
    ts = datetime.datetime.fromtimestamp(seconds)
    return(ts.strftime('%Y-%m-%d %H:%M:%S'))
    
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

log("-- Connecting to Netskope API for tenant [" + creds.netskope_tenant + "]...")

api_url = "https://" + creds.netskope_tenant + ".goskope.com/api/v1/alerts"
api_parameters = "token=" + creds.netskope_token + "&timeperiod=" + str(creds.netskope_timeperiod) + "&limit" + str(creds.netskope_limit) + "&unsorted=true"

#print(api_url + "?" + api_parameters)

## Get alerts

response = requests.get(api_url + "?" + api_parameters)

json_response = response.json()

#if creds.debug:
#    with open(creds.working_file_json, 'w') as f:
#        f.write(json.dumps(json_response))


for alert in json_response["data"]:

    ## Only selected fields are parsed for the POC 
    ## Complete list here https://docs.netskope.com/en/rest-api-events-and-alerts-response-descriptions.html

    alert_timestamp = format_timestamp(int(key_value(alert, "timestamp", "")))
    alert_name = key_value(alert, "alert_name", "")
    alert_type = key_value(alert, "alert_type", "")

    alert_severity = key_value(alert, "severity", "")

    alert_access_method = key_value(alert, "access_method", "")
    alert_traffic_type = key_value(alert, "traffic_type", "")
    alert_action = key_value(alert, "action", "")

    alert_tunnel_id = key_value(alert, "tunnel_id", "")
    alert_request_id = key_value(alert, "request_id", "")
    alert_transaction_id = key_value(alert, "transaction_id", "")
    alert_connection_id = key_value(alert, "connection_id", "")

    alert_insertion_timestamp = format_timestamp(int(key_value(alert, "_insertion_epoch_timestamp", "")))
    alert_id = key_value(alert, "_id", "")

    if not alreadyUploaded(alert_id):
        # Construct event log

        event = "NETSKOPE," + alert_timestamp + "," + alert_name + "," + alert_type + "," + alert_severity + "," 
        event = event + alert_access_method + "," + alert_traffic_type + "," + alert_action + ","
        event = event + alert_tunnel_id + "," + alert_request_id + "," + alert_transaction_id + "," + alert_connection_id + ","
        event = event + alert_insertion_timestamp + "," + alert_id


        # Add to working file
        writeWorkingFile(event)

        # Note down the alertid to keep track of events already uploaded
        noteUploaded(alert_id)

        count = count + 1
        if (count/100) == int(count/100):
            log("-- " + str(count) + " alerts fetched")

if count > 0:
    log("-- " + str(count) + " alerts retrieved")

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
            if creds.upload:
                log("-- Uploading...")
                ret = api.upload_file("NETSKOPE", creds.working_file)
                if ret == b'':
                    log("-- Uploaded telemetry to Taegis!")
                else:
                    log("-- Upload failed!")
                    print(ret)
        
            # Delete file after uploaded
            if not creds.debug:
                os.remove(creds.working_file)
                log("-- Deleted working files")
else:
    log("-- Nothing new to process")

log("-- End")
