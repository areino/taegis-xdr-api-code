from distutils.log import error
import json
import datetime
import time
import os
import smtplib
from threading import Thread, Lock
import threading
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from taegis import XDR

## v1.0 - Initial version
## v2.0 - Fixed some errors caused by API not returning data, and added timestamp_api column to output CSV
## v2.1 - Fixed issue on 11th feb.
## v3.0 - Multithreaded
## v3.1 - Fixed issues with data corruption, waits for threads to finish before sending report by email
## v3.2 - Added debug log
## v3.3 - Added field in output CSV to indicate success of health info fetching
## v4.0 - Added second pass for invalid health assets


assets_with_errors = []


def log(s):
    print(datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M:%S") + '  ' + str(s))


def sendReport():
    with open(filename, "r") as myfile:
        reporthtml = myfile.read()

    msg = MIMEMultipart()
    msg['Subject'] = "Agent health report for tenant " + str(tenant_id) + " [" + datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M") + "]"
    msg['From'] = email_sender
    msg['To'] = email_receiver

    with open(filename, 'rb') as fp:
        msg2 = MIMEBase('application', 'octet-stream')
        msg2.set_payload(fp.read())
        encoders.encode_base64(msg2)
        msg2.add_header('Content-Disposition', 'attachment', filename=os.path.basename(filename))
        msg.attach(msg2)

    try:
        server = smtplib.SMTP(smtp_hostname, smtp_port)
        server.ehlo()
        server.starttls()
        server.ehlo()
        if smtp_username != "":
            server.login(smtp_username, smtp_password)
        server.sendmail(email_sender, email_receiver, msg.as_string())
        server.close()
    except Exception as e:
        log("-- Error sending report by email: " + str(e))
    else:
        log("-- Email sent!")



def report(filename, string, mode="a"):
    with open(filename, mode) as myfile:
        myfile.write(string + "\n")



def format_timestamp(seconds):
    ts = datetime.datetime.fromtimestamp(seconds)
    return(ts.strftime('%Y-%m-%d %H:%M:%S'))

def health(colour):
    if colour is None or colour == "":
        return("Unhealthy")
    elif colour.lower() == "green" or colour.lower() == "yellow":
        return("Healthy")
    else:
        return("Unhealthy")

def fix(string, default):
    if string is None:
        return(str(default))
    else:
        return(str(string))

def fixtime(timestring):
    ## <Time 2021-10-20T12:05:50.159754>
    if timestring is None or timestring == "":
        return("")
    else:
        return(timestring[5:-1])

def unroll(array):
    a = ""
    if array is None:
        a = ""
    else:
        for e in array:
            a = a + e + ';'
        if len(a) > 0:
            a = a[:-1]
    return(a)

def unrolld(dictionary, element):
    a = ""
    if dictionary is None:
        a = ""
    else:
        for e in dictionary:
            a = a + e[element] + ';'
        if len(a) > 0:
            a = a[:-1]
    return(a)

def isEnabled(i):
    r = "FALSE"
    if i is None:
        r = "FALSE"
    else:
        if i == 'None':
            r = "FALSE"
        else:
            if i:
                r = "TRUE"
            else:
                r = "FALSE"
    return(r)

def valid_response(data):
    valid = False
    
    if data != False:
        if data is not None:
            try:
                data_json = json.loads(json.dumps(data))
                valid = True
            except ValueError as e:
                valid = False
                if debug_mode: 
                    log("-- Returned data is not JSON")
                    print(data)
        else:
            if debug_mode: 
                log("-- Returned data is None")
    else:
        if debug_mode:
            log("-- Returned data is False")

    return(valid)




def fetchHealth(asset, lock):
    global assets_with_errors

    ## Prepare data
    row = ""
    row = row + asset['id'] + ","
    row = row + unrolld(asset['hostnames'], "hostname") + ","
    row = row + asset['sensorVersion'] + ","
    row = row + asset['osVersion'] + ","
    row = row + asset['architecture'] + ","
    row = row + unrolld(asset['hostnames'], "hostname") + ","
    row = row + asset['osRelease'] + ","
    row = row + asset['biosSerial'] + ","
    row = row + asset['firstDiskSerial'] + ","
    row = row + asset['systemVolumeSerial'] + ","
    row = row + unrolld(asset['ethernetAddresses'], "mac") + ","
    row = row + unrolld(asset['ipAddresses'], "ip") + ","
    row = row + unrolld(asset['users'], "username") + ","
    row = row + asset['sensorVersion'] + ","
    row = row + asset['systemType'] + ","

    row = row + "FALSE,UNKNOWN,,,,,,,,,,FALSE,0,,,,"

    row = row + asset['endpointType'] + ","
    row = row + "PLATFORM_WINDOWS,"
    row = row + asset['endpointType'] + ","
    row = row + "PLATFORM_WINDOWS,"


    query2 = '''
        query endpointinfo($id: ID!) {
            assetEndpointInfo(id: $id){
                    actualIsolationStatus
                    color
                    actualIsolationStatus 
                    desiredIsolationStatus
                    lastConnectTime
                    lastConnectServer
                    lastConnectAddress
                    lastModuleStatusTime
                    lastCrashCheck
                    firstConnectTime
                    moduleHealth { enabled lastPredicateTime lastRunningTime moduleColor moduleDisplayName }
                    notableEventCount
                    ignitionDetails { isEndpointConfigExist  requestStatus }
                    
            }
        }    
    '''
    log("-- Fetching health data for asset " + asset['id'])

    variables = { "id": asset['id'] }
    data2 = api.execute_query(query2, variables)
    if valid_response(data2):
        try:
            results2 = data2['data'].get('assetEndpointInfo', [])
        except:
            results2 = False
            if debug_mode:
                XDR.debuglog("Error querying asset " + asset["id"] + "\n" + str(data2))

        if results2:
            row = row + "," ## vendor_version

            row = row + fix(results2['color'], "UNKNOWN") + ","
            row = row + unrolld(asset['tags'], "tag") + ","
            row = row + "UNKNOWN,"  ## Safe mode
            row = row + fix(results2['lastConnectTime'], "") + ","
            row = row + fix(results2['lastConnectServer'], "") + ","
            row = row + fix(results2['lastConnectAddress'], "") + ","
            row = row + fix(results2['lastCrashCheck'], "") + ","
            row = row + fix(results2['firstConnectTime'], "") + ","


            ignition_enabled = "FALSE"
            ignition_last_predicate_time = ""
            ignition_last_running_time = ""
            ignition_color = "UNKNOWN"

            for mod in results2['moduleHealth']:
                if mod['moduleDisplayName'] == "Procwall":
                    procwall_enabled = isEnabled(mod['enabled'])
                    procwall_last_predicate_time = mod['lastPredicateTime'] or ""
                    procwall_last_running_time = mod['lastRunningTime'] or ""
                    procwall_color = mod['moduleColor']
                elif mod['moduleDisplayName'] == "Cyclorama":
                    cyclorama_enabled = isEnabled(mod['enabled'])
                    cyclorama_last_predicate_time = mod['lastPredicateTime'] or ""
                    cyclorama_last_running_time = mod['lastRunningTime'] or ""
                    cyclorama_color = mod['moduleColor']
                elif mod['moduleDisplayName'] == "Groundling":
                    groundling_enabled = isEnabled(mod['enabled'])
                    groundling_last_predicate_time = mod['lastPredicateTime'] or ""
                    groundling_last_running_time = mod['lastRunningTime'] or ""
                    groundling_color = mod['moduleColor']
                elif mod['moduleDisplayName'] == "Inspector Result":
                    inspector_result_enabled = isEnabled(mod['enabled'])
                    inspector_result_last_predicate_time = mod['lastPredicateTime'] or ""
                    inspector_result_last_running_time = mod['lastRunningTime'] or ""
                    inspector_result_color = mod['moduleColor']
                elif mod['moduleDisplayName'] == "Inspector Control":
                    inspector_control_enabled = isEnabled(mod['enabled'])
                    inspector_control_last_predicate_time = mod['lastPredicateTime'] or ""
                    inspector_control_last_running_time = mod['lastRunningTime'] or ""
                    inspector_control_color = mod['moduleColor']
                elif mod['moduleDisplayName'] == "Lacuna":
                    lacuna_enabled = isEnabled(mod['enabled'])
                    lacuna_last_predicate_time = mod['lastPredicateTime'] or ""
                    lacuna_last_running_time = mod['lastRunningTime'] or ""
                    lacuna_color = mod['moduleColor']
                elif mod['moduleDisplayName'] == "Authtap":
                    authtap_enabled = isEnabled(mod['enabled'])
                    authtap_last_predicate_time = mod['lastPredicateTime'] or ""
                    authtap_last_running_time = mod['lastRunningTime'] or ""
                    authtap_color = mod['moduleColor']
                elif mod['moduleDisplayName'] == "Mukluk":
                    mukluk_enabled = isEnabled(mod['enabled'])
                    mukluk_last_predicate_time = mod['lastPredicateTime'] or ""
                    mukluk_last_running_time = mod['lastRunningTime'] or ""
                    mukluk_color = mod['moduleColor']
                elif mod['moduleDisplayName'] == "FCM":
                    fcm_enabled = isEnabled(mod['enabled'])
                    fcm_last_predicate_time = mod['lastPredicateTime'] or ""
                    fcm_last_running_time = mod['lastRunningTime'] or ""
                    fcm_color = mod['moduleColor']
                elif mod['moduleDisplayName'] == "Entwine":
                    entwine_enabled = isEnabled(mod['enabled'])
                    entwine_last_predicate_time = mod['lastPredicateTime'] or ""
                    entwine_last_running_time = mod['lastRunningTime'] or ""
                    entwine_color = mod['moduleColor']
                elif mod['moduleDisplayName'] == "Hostel":
                    hostel_enabled = isEnabled(mod['enabled'])
                    hostel_last_predicate_time = mod['lastPredicateTime'] or ""
                    hostel_last_running_time = mod['lastRunningTime'] or ""
                    hostel_color = mod['moduleColor']
                elif mod['moduleDisplayName'] == "Ignition":
                    ignition_enabled = isEnabled(mod['enabled'])
                    ignition_last_predicate_time = mod['lastPredicateTime'] or ""
                    ignition_last_running_time = mod['lastRunningTime'] or ""
                    ignition_color = mod['moduleColor']

            row = row + procwall_enabled + "," + procwall_color + "," + procwall_last_predicate_time + "," + procwall_last_running_time + ","
            row = row + cyclorama_enabled + "," + cyclorama_color + "," + cyclorama_last_predicate_time + "," + cyclorama_last_running_time + ","
            row = row + groundling_enabled + "," + groundling_color + "," + groundling_last_predicate_time + "," + groundling_last_running_time + ","
            row = row + inspector_result_enabled + "," + inspector_control_color + "," + inspector_result_last_predicate_time + "," + inspector_result_last_running_time + ","
            row = row + inspector_control_enabled + "," + inspector_control_color + "," + inspector_control_last_predicate_time + "," + inspector_control_last_running_time + ","
            row = row + lacuna_enabled + "," + lacuna_color + "," + lacuna_last_predicate_time + "," + lacuna_last_running_time + ","
            row = row + authtap_enabled + "," + authtap_color + "," + authtap_last_predicate_time + "," + authtap_last_running_time + ","
            row = row + mukluk_enabled + "," + mukluk_color + "," + mukluk_last_predicate_time + "," + mukluk_last_running_time + ","
            row = row + fcm_enabled + "," + fcm_color + "," + fcm_last_predicate_time + "," + fcm_last_running_time + ","
            row = row + entwine_enabled + "," + entwine_color + "," + entwine_last_predicate_time + "," + entwine_last_running_time + ","
            row = row + hostel_enabled + "," + hostel_color + "," + hostel_last_predicate_time + "," + hostel_last_running_time + ","
            row = row + ignition_enabled + "," + ignition_color + "," + ignition_last_predicate_time + "," + ignition_last_running_time + ","

            row = row + fix(results2['desiredIsolationStatus'], "UNKNOWN") + ","
            row = row + fix(results2['actualIsolationStatus'], "UNKNOWN") + ","
            row = row + "UNKNOWN" + "," ## whitelisted for isolation
            row = row + str(results2['notableEventCount']) + ","

            if results2['ignitionDetails'] is not None:
                row = row + fix(results2['ignitionDetails']['requestStatus'], "") + ","
                row = row +",," ## ignition_details.setup_request_id	ignition_details.job_id
                row = row + isEnabled(results2['ignitionDetails']['isEndpointConfigExist']) + ","
            else:
                row = row + ","
                row = row +",," ## ignition_details.setup_request_id	ignition_details.job_id
                row = row + "FALSE,"
            row = row +",,FALSE,,,," ## ignition_details.last_setup_message	ignition_details.from_version	ignition_details.retry_required	crowdstrike_agent.cid	crowdstrike_agent.aid	crowdstrike_agent.rc_agent_id

            row = row + asset['sensorVersion'] + ","
            row = row + "" + "," ## last_predicate_process_disruption
            row = row + fix(results2['lastModuleStatusTime'], "") + ","
            row = row + ",,," ## last_safe_mode_update_time	timestamp allowed_domain

            row = row + entwine_last_predicate_time + ","
            row = row + fcm_last_predicate_time + ","
            row = row + hostel_last_predicate_time + ","
            row = row + inspector_control_last_predicate_time + ","
            row = row + ",," ## last_predicate_periodicscan_control last_predicate_periodicscan_result
            row = row + lacuna_last_predicate_time + ","
            row = row + authtap_last_predicate_time + ","
            row = row + cyclorama_last_predicate_time + ","
            row = row + "," ## last_predicate_fcm_change_event
            row = row + groundling_last_predicate_time + ","
            row = row + ignition_last_predicate_time + "," 
            row = row + mukluk_last_predicate_time + ","
            row = row + procwall_last_predicate_time + ","
            row = row + "," ## last_predicate_system_information
            row = row + health(results2['color'])
            row = row + "," + datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%S")
            row = row + ",SUCCESS"
    else:
        failed_asset = [asset, asset['id']]
        row = ""
        # row = row + ("," * 93) + datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%S")
        # row = row + ",INVALID RESPONSE"
        assets_with_errors.append(failed_asset)
        if debug_mode:
            XDR.debuglog("Invalid response querying asset " + asset["id"] + "\n" + str(data2))


    if row.count(",") < 40:
        failed_asset = [asset, asset['id']]
        row = ""
        # row = row + ("," * 93) + datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%S")
        # row = row + ",INVALID RESPONSE"
        assets_with_errors.append(failed_asset)
        if debug_mode:
            XDR.debuglog("Incomplete data querying asset " + asset["id"] + "\n" + str(data2))

    ## Write to CSV in a thread-safe way
    if len(row) > 0:
        lock.acquire()
        report(filename, row, "a")
        lock.release()

    return()



    
def fetch_assets(api, tenant_id):
    ## Import assets
    query = '''
        query {
          allAssets(
            filter_asset_state: Active 
            limit: 10000
          )
          {
            totalResults
            assets {
              id
              hostnames { hostname }
              sensorVersion
              architecture
              osVersion
              osRelease
              osCodename
              biosSerial
              firstDiskSerial
              systemVolumeSerial
              ethernetAddresses { mac }
              ipAddresses { ip }
              users { username }
              systemType
              osFamily
              kernelRelease
              kernelVersion
              endpointType
              endpointPlatform
              tags { tag }
            }
          }
        }
    '''

    ## Query API
    log("-- Querying API for assets")
    data = api.execute_query(query)
    if data == False:
        log("-- Problem querying API, quitting")
    
    i = 0

    if valid_response(data):
        results = data['data']['allAssets'].get("assets", [])
        max = len(results)

        log("-- " + str(max) + " assets returned")
        log("-- Maximum parallel threads = " + str(max_threads))

        if results:
            
            ## Lock for multi threaded write to CSV report
            lock = Lock()
            started = []

            for asset in results:

                if threading.active_count() >= max_threads + 1:
                    ## Max threads reached, join as many as possible
                    for thread in started:
                        thread.join()
                        started.remove(thread)

                ## Start as many threads as allowed
                if threading.active_count() < max_threads + 1:
                    if asset['id'] in done:
                        log("-- Skipping asset " + str(asset['id']))
                    else:                    
                        started.append(Thread(target=fetchHealth, args=(asset, lock)))
                        started[-1].start()
                        i = i + 1 

    else:
        log("-- No assets returned")
    
    return(i)
    



############################################

log("Starting...")

## Configuration
tenant_id =         96072
tenant_api_id =     "9EnbHC1ZB9ceRkhA6yXImXDE4tLPKTKS"
tenant_api_secret = "6trWUHRkBtwVjqciqPil2LDFPMg98_Oi3xg49ZSsqZaKhZrQaiFKqJ4kn2i2zKSt"


tenant_id =         96842
tenant_api_id =     "WXB3jYqrQS0NFQOgsDU4VeBrmqQLzbAw"
tenant_api_secret = "Fa_Hgdvqu7T-Nslh2qKtlgTkSY49_RUtRuDzvyXK8zjOaGENavxjtAqppdIEH01r"


email_sender =      ""
email_sendername =  "Agent Health Report"
email_receiver =    ""

smtp_hostname =     ""
smtp_port =         587
smtp_username =     ""
smtp_password =     ""


max_threads =       20
debug_mode =        True

############################################

filename = "report.csv"
assets_with_errors = []
done = []


if os.path.exists(filename):
    log("-- Report file exists, resuming collection")
    ## Load IDs into list
    file = open(filename, "r")
    lines = file.readlines()
    count = 0
    for line in lines:
        done.append(line.split(",")[0])
        count = count + 1
    file.close()
    log("-- Report file contains " + str(count) + " records...")    

else:
    ## New report
    ## Create file and header
    log("-- Report file does not exist, creating new one")

    header = "id,name,version,system_information.version,"
    header = header + "system_information.architecture,system_information.hostname,system_information.service_pack,system_information.bios_serial,"
    header = header + "system_information.first_disk_serial,system_information.system_volume_serial,system_information.ethernet_address,system_information.ip_address,"
    header = header + "system_information.logon_user,system_information.redcloak_version,system_information.product_type,system_information.is_server_r2_for_2003_and_2008,"
    header = header + "system_information.linux_lsb_distributor_id,system_information.linux_lsb_distributor_name,system_information.linux_lsb_release,"
    header = header + "system_information.linux_lsb_code_name,system_information.uname_name,system_information.uname_release,system_information.uname_version,"
    header = header + "system_information.uname_machine,system_information.uname_processor,system_information.uname_os,system_information.update_info.is_out_of_date,"
    header = header + "system_information.update_info.available_latest_version,system_information.update_info.agent_config_set_id,system_information.vendor_version,"
    header = header + "system_information.ipv6_address,system_information.endpoint_type,system_information.endpoint_platform,endpoint_type,endpoint_platform,"
    header = header + "vendor_version,color,tag,safe_mode,last_connect_time,last_connect_server,last_connect_address,last_crash_check,first_connect_time,"
    header = header + "module_health.Procwall.enabled,module_health.Procwall.module_color,module_health.Procwall.last_predicate_time,module_health.Procwall.last_running_time,"
    header = header + "module_health.Cyclorama.enabled,module_health.Cyclorama.module_color,module_health.Cyclorama.last_predicate_time,module_health.Cyclorama.last_running_time,"
    header = header + "module_health.Groundling.enabled,module_health.Groundling.module_color,module_health.Groundling.last_predicate_time,module_health.Groundling.last_running_time,"
    header = header + "module_health.Inspector Result.enabled,module_health.Inspector Result.module_color,module_health.Inspector Result.last_predicate_time,module_health.Inspector Result.last_running_time,"
    header = header + "module_health.Inspector Control.enabled,module_health.Inspector Control.module_color,module_health.Inspector Control.last_predicate_time,module_health.Inspector Control.last_running_time,"
    header = header + "module_health.Lacuna.enabled,module_health.Lacuna.module_color,module_health.Lacuna.last_predicate_time,module_health.Lacuna.last_running_time,"
    header = header + "module_health.Authtap.enabled,module_health.Authtap.module_color,module_health.Authtap.last_predicate_time,module_health.Authtap.last_running_time,"
    header = header + "module_health.Mukluk.enabled,module_health.Mukluk.module_color,module_health.Mukluk.last_predicate_time,module_health.Mukluk.last_running_time,"
    header = header + "module_health.FCM.enabled,module_health.FCM.module_color,module_health.FCM.last_predicate_time,module_health.FCM.last_running_time,"
    header = header + "module_health.Entwine.enabled,module_health.Entwine.module_color,module_health.Entwine.last_predicate_time,module_health.Entwine.last_running_time,"
    header = header + "module_health.Hostel.enabled,module_health.Hostel.module_color,module_health.Hostel.last_predicate_time,module_health.Hostel.last_running_time,"
    header = header + "module_health.Ignition.enabled,module_health.Ignition.module_color,module_health.Ignition.last_predicate_time,module_health.Ignition.last_running_time,"
    header = header + "desired_isolation_status,actual_isolation_status,whitelisted_for_isolation,notable_event_count,"
    header = header + "ignition_details.request_status,ignition_details.setup_request_id,ignition_details.job_id,ignition_details.is_endpoint_config_exist,"
    header = header + "ignition_details.last_setup_message,ignition_details.from_version,ignition_details.retry_required,"
    header = header + "crowdstrike_agent.cid,crowdstrike_agent.aid,crowdstrike_agent.rc_agent_id,"
    header = header + "ignition_version,last_predicate_process_disruption,last_module_status_time,last_safe_mode_update_time,timestamp,allowed_domain,last_predicate_entwine,"
    header = header + "last_predicate_fcm_control,last_predicate_hostel,last_predicate_inspector,last_predicate_periodicscan_control,last_predicate_periodicscan_result,"
    header = header + "last_predicate_lacuna,last_predicate_authtap,last_predicate_cyclorama,last_predicate_fcm_change_event,last_predicate_groundling,last_predicate_ignition,"
    header = header + "last_predicate_mukluk,last_predicate_procwall,last_predicate_system_information,health,"
    header = header + "timestamp_api"
    report(filename, header, "w")


## Get data
log("Initializing API client for tenant")
api = XDR(client_id=tenant_api_id, client_secret=tenant_api_secret, tenant_id=tenant_id)
count_assets = fetch_assets(api, tenant_id)
log("Finished getting health info for " + str(count_assets) + " assets")

## Wait for threads to finish
while threading.active_count() > 1:
    log("-- Closing down parallel threads (remaining: " + str(threading.active_count()) + ")")
    time.sleep(2)

log("Assets with incomplete health data: " + str(len(assets_with_errors)))
## Retry assets with incomplete health data

lock = Lock()
for failed_asset in assets_with_errors:
    log("-- Retrying " + failed_asset[1])
    fetchHealth(failed_asset[0], lock)


## Send file
log("Sending report by email")
sendReport()

log("End")
log("")