import json
import creds
import psycopg2
import datetime
from taegis.taegis import XDR

def format_timestamp(seconds):
    ts = datetime.datetime.fromtimestamp(seconds)
    return(ts.strftime('%Y-%m-%d %H:%M:%S'))

def log(s):
    print(datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M:%S") + '  ' + str(s))

def unroll(array):
    a = ""
    if array is None:
        a = ""
    else:
        for e in array:
            a = a + e + ','
        if len(a) > 0:
            a = a[:-1]
    return(a)

def unrolld(dictionary, element):
    a = ""
    if dictionary is None:
        a = ""
    else:
        for e in dictionary:
            a = a + e[element] + ','
        if len(a) > 0:
            a = a[:-1]
    return(a)

def isEnabled(i):
    r = 0
    if i is None:
        r = 0
    else:
        if i == 'None':
            r = 0
        else:
            if i:
                r = 1
            else:
                r = 0
    return(r)

def fetch_rc_health(api, asset_id):
    ## Query
    query = '''
        query endpointinfo($id: ID!) {
            assetEndpointInfo(id: $id){
                actualIsolationStatus
                    color
                    desiredIsolationStatus
                    firstConnectTime
                    lastConnectAddress
                    lastConnectServer
                    lastConnectTime
                    lastCrashCheck
                    lastModuleStatusTime
                    moduleHealth { enabled lastPredicateTime lastRunningTime moduleColor moduleDisplayName }
            }
        }    
    '''
    log("-- Fetching health data for asset " + asset_id)
    
    variables = { "id": asset_id }
    data = api.execute_query(query, variables)

    if 'assetEndpointInfo' in data:
        results = data['data']['assetEndpointInfo']

        #print(results)

        color = results['color'] or "UNKNOWN"
        actual_isolation_status = results['actualIsolationStatus'] or 0
        desired_isolation_status = results['desiredIsolationStatus'] or 0
        first_connect_time = results['firstConnectTime'] or ""
        last_connect_address = results['lastConnectAddress'] or ""
        last_connect_server = results['lastConnectServer'] or ""
        last_connect_time = results['lastConnectTime'] or ""
        last_crash_check = results['lastCrashCheck'] or ""
        last_module_status_time = results['lastModuleStatusTime'] or ""

        ignition_enabled = 0
        ignition_last_predicate_time = ""
        ignition_last_running_time = ""
        ignition_color = "UNKNOWN"

        for mod in results['moduleHealth']:
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


        ## Update table
        c.execute("DELETE FROM asset_health WHERE id = \'" + asset_id + "\'")

        insert = """
            INSERT INTO asset_health (id, color, actual_isolation_status, desired_isolation_status, last_module_status_time, 
                first_connect_time, last_connect_address, last_connect_server, last_connect_time, last_crash_check,
                procwall_enabled, procwall_last_predicate_time, procwall_last_running_time, procwall_color, 
                cyclorama_enabled, cyclorama_last_predicate_time, cyclorama_last_running_time, cyclorama_color, 
                groundling_enabled, groundling_last_predicate_time, groundling_last_running_time, groundling_color, 
                inspector_result_enabled, inspector_result_last_predicate_time, inspector_result_last_running_time, inspector_result_color, 
                inspector_control_enabled, inspector_control_last_predicate_time, inspector_control_last_running_time, inspector_control_color, 
                lacuna_enabled, lacuna_last_predicate_time, lacuna_last_running_time, lacuna_color, 
                authtap_enabled, authtap_last_predicate_time, authtap_last_running_time, authtap_color, 
                mukluk_enabled, mukluk_last_predicate_time, mukluk_last_running_time, mukluk_color, 
                fcm_enabled, fcm_last_predicate_time, fcm_last_running_time, fcm_color, 
                entwine_enabled, entwine_last_predicate_time, entwine_last_running_time, entwine_color, 
                hostel_enabled, hostel_last_predicate_time, hostel_last_running_time, hostel_color, 
                ignition_enabled, ignition_last_predicate_time, ignition_last_running_time, ignition_color )
            VALUES('%s', '%s', %s, %s, '%s', '%s', '%s', '%s', '%s', '%s', 
                %s, '%s', '%s', '%s', 
                %s, '%s', '%s', '%s', 
                %s, '%s', '%s', '%s', 
                %s, '%s', '%s', '%s', 
                %s, '%s', '%s', '%s', 
                %s, '%s', '%s', '%s', 
                %s, '%s', '%s', '%s', 
                %s, '%s', '%s', '%s', 
                %s, '%s', '%s', '%s', 
                %s, '%s', '%s', '%s', 
                %s, '%s', '%s', '%s', 
                %s, '%s', '%s', '%s') 
            """ % (asset_id, color, actual_isolation_status, desired_isolation_status, last_module_status_time, 
                first_connect_time, last_connect_address, last_connect_server, last_connect_time, last_crash_check,
                procwall_enabled, procwall_last_predicate_time, procwall_last_running_time, procwall_color, 
                cyclorama_enabled, cyclorama_last_predicate_time, cyclorama_last_running_time, cyclorama_color, 
                groundling_enabled, groundling_last_predicate_time, groundling_last_running_time, groundling_color, 
                inspector_result_enabled, inspector_result_last_predicate_time, inspector_result_last_running_time, inspector_result_color, 
                inspector_control_enabled, inspector_control_last_predicate_time, inspector_control_last_running_time, inspector_control_color, 
                lacuna_enabled, lacuna_last_predicate_time, lacuna_last_running_time, lacuna_color, 
                authtap_enabled, authtap_last_predicate_time, authtap_last_running_time, authtap_color, 
                mukluk_enabled, mukluk_last_predicate_time, mukluk_last_running_time, mukluk_color, 
                fcm_enabled, fcm_last_predicate_time, fcm_last_running_time, fcm_color, 
                entwine_enabled, entwine_last_predicate_time, entwine_last_running_time, entwine_color, 
                hostel_enabled, hostel_last_predicate_time, hostel_last_running_time, hostel_color, 
                ignition_enabled, ignition_last_predicate_time, ignition_last_running_time, ignition_color)
        c.execute(insert)

    
def fetch_assets(api, tenant_id):
    ## Import assets
    query = '''
        query {
          allAssets(
            filter_asset_state: All
          )
          {
            totalResults
            assets {
              id
              hostId
              tenantId
              sensorTenant
              sensorId
              ingestTime
              createdAt
              updatedAt
              deletedAt
              sensorVersion
              endpointType
              endpointPlatform
              osFamily
              osVersion
              osRelease
              architecture
              systemType
              osCodename
              kernelRelease
              kernelVersion
              tags { tag }
              hostnames { hostname }
              ipAddresses { ip }
              users { username }
            }
          }
        }
    '''

    ## Query API
    log("-- Querying API for assets")
    data = api.execute_query(query)
    results = data['data']['allAssets']
    
    ## Start transaction
    c = db.cursor()

    ## clean db
    log("-- Cleaning up current asset information")
    c.execute("DELETE FROM asset WHERE tenant_id = " + str(tenant_id) + ";")
    i = 0
    if results is not None:
        for asset in results['assets']:
            i = i + 1
            ## Prepare data
            
            id = asset['id']
#            tenant_id = asset['tenantId']
            
            created_at = asset['createdAt'] or "1970-01-01 08:00:00+08"
            updated_at = asset['updatedAt'] or "1970-01-01 08:00:00+08"
            deleted_at = asset['deletedAt'] or "1970-01-01 08:00:00+08"
            
            architecture = asset['architecture']
            endpoint_platform = asset['endpointPlatform']
            endpoint_type = asset['endpointType']
            system_type = asset['systemType']
            host_id = asset['hostId']

            hostnames = unrolld(asset['hostnames'], 'hostname')
            users = unrolld(asset['users'], 'username')
            ip_addresses = unrolld(asset['ipAddresses'], 'ip')
            
            tags = unrolld(asset['tags'], 'tag')

            ingest_time = asset['ingestTime']
            kernel_release = asset['kernelRelease']
            kernel_version = asset['kernelVersion']
            os_codename = asset['osCodename']
            os_family = asset['osFamily']
            os_release = asset['osRelease']
            os_version = asset['osVersion']
            sensor_id = asset['sensorId']
            sensor_tenant = asset['sensorTenant']
            sensor_version = asset['sensorVersion']

            ## Insert into database
            
            insert = """
                INSERT INTO asset (id, tenant_id, architecture, created_at, updated_at, deleted_at,
                    endpoint_platform, endpoint_type, host_id, hostnames, users, ip_addresses, ingest_time,
                    kernel_release, kernel_version, os_codename, os_family, os_release, os_version,
                    sensor_id, sensor_tenant, sensor_version, tags)
                VALUES('%s', %s, '%s', '%s', '%s', '%s', 
                       '%s', '%s', '%s', '%s', '%s', '%s', '%s', 
                       '%s', '%s', '%s', '%s', '%s', '%s', 
                       '%s', '%s', '%s', '%s') ON CONFLICT DO NOTHING;
                """ % (id, tenant_id, architecture, created_at, updated_at, deleted_at,
                        endpoint_platform, endpoint_type, host_id, hostnames, users, ip_addresses, ingest_time,
                        kernel_release, kernel_version, os_codename, os_family, os_release, os_version,
                        sensor_id, sensor_tenant, sensor_version, tags)
            c.execute(insert)
            
            fetch_rc_health(api, id)
            
        ## Commit transaction
        db.commit()
        log("-- Inserted " + str(i) + " assets into database")
    else:
        log("-- No assets returned")
    
    return(i)
    
    

def fetch_investigations(api, tenant_id):
    ## Import investigations
    query = """
        query {
          allInvestigations(perPage: 10000){
            id
            tenant_id
            genesis_alerts { id }
            alerts { id }
            assets  { id }
            description
            created_at
            updated_at
            notified_at
            created_by
            status
            contributors
            latest_activity
            transition_state { 
              handed_off_at_least_once 
              initial_handoff_time 
              acknowledged_at_least_once
              initial_acknowledge_time
              resolved_at_least_once
              initial_resolution_time
              handed_off
              handoff_time
              acknowledged
              acknowledge_time
              resolved
              resolution_time
            }
            deleted_at
            created_by_scwx
            priority
            type
            genesis_alerts_count
            genesis_events_count
            alerts_count
            events_count
            assets_count
          }
        }
    """
    ## Query API

    log("-- Querying API for investigations")
    data = api.execute_query(query)
    results = data['data']['allInvestigations']

    ## Start transaction
    c = db.cursor()

    log("-- Cleaning up investigations table")
    c.execute("DELETE FROM investigation WHERE tenant_id = " + str(tenant_id) + ";")
    c.execute("DELETE FROM alert_investigation WHERE tenant_id = " + str(tenant_id) + ";")
    c.execute("DELETE FROM asset_investigation WHERE tenant_id = " + str(tenant_id) + ";")
    
    i = 0
    if results is not None:
        for inv in results:
            i = i + 1
            ## Prepare data
            
            id = inv['id']
            description = inv['description'].replace("'", "''")
            ##latest_activity = inv['latest_activity']
            latest_activity = ""
            priority = inv['priority'] or 0
            status = inv['status']
            # tenant_id = inv['tenant_id']
            type = inv['type']
            

            alerts_count = inv['alerts_count']
            assets_count = inv['assets_count']
            events_count = inv['events_count']
            genesis_alerts_count = inv['genesis_alerts_count']
            genesis_events_count = inv['genesis_events_count']
            
#            if inv['assignee'] is not None:
#                assignee_email = inv['assignee']['email']
#                assignee_roles = unroll(inv['assignee']['roles'])
#            else:
            assignee_email = ""
            assignee_roles = ""
                

            created_at = inv['created_at'] or "1970-01-01 08:00:00+08"
            created_by_scwx = inv['created_by_scwx']
            notified_at = inv['notified_at'] or "1970-01-01 08:00:00+08"
            updated_at = inv['updated_at'] or "1970-01-01 08:00:00+08"
            deleted_at = inv['deleted_at'] or "1970-01-01 08:00:00+08"
            
            acknowledged = inv['transition_state']['acknowledged']
            acknowledge_time = inv['transition_state']['acknowledge_time'] or "1970-01-01 08:00:00+08"
            initial_acknowledge_time = inv['transition_state']['initial_acknowledge_time'] or "1970-01-01 08:00:00+08"
            acknowledged_at_least_once = inv['transition_state']['acknowledged_at_least_once']

            handoff_time = inv['transition_state']['handoff_time'] or "1970-01-01 08:00:00+08"
            initial_handoff_time = inv['transition_state']['initial_handoff_time'] or "1970-01-01 08:00:00+08"
            handed_off = inv['transition_state']['handed_off']
            handed_off_at_least_once = inv['transition_state']['handed_off_at_least_once']

            resolved = inv['transition_state']['resolved']
            resolution_time = inv['transition_state']['resolution_time'] or "1970-01-01 08:00:00+08"
            initial_resolution_time = inv['transition_state']['initial_resolution_time'] or "1970-01-01 08:00:00+08"
            resolved_at_least_once = inv['transition_state']['resolved_at_least_once']
            
            ## Insert investigation into table
            
            insert = """
                    INSERT INTO investigation (id, description, latest_activity, priority, status, type,
                        tenant_id, alerts_count, assets_count, events_count, genesis_alerts_count, genesis_events_count,
                        assignee_email, assignee_roles, created_at, created_by_scwx, notified_at, updated_at, deleted_at,
                        acknowledged, acknowledge_time, initial_acknowledge_time, acknowledged_at_least_once,
                        handed_off, handoff_time, initial_handoff_time, handed_off_at_least_once,
                        resolved, resolution_time, initial_resolution_time, resolved_at_least_once)
                    VALUES ('%s', '%s', '%s', %s, '%s', '%s', 
                            %s, %s, %s, %s, %s, %s,
                            '%s', '%s', '%s', '%s', '%s', '%s', '%s', 
                            '%s', '%s', '%s', '%s', 
                            '%s', '%s', '%s', '%s', 
                            '%s', '%s', '%s', '%s'
                            )  ON CONFLICT (id) DO NOTHING;
                    """ % (id, description, latest_activity, priority, status, type,
                           tenant_id, alerts_count, assets_count, events_count, genesis_alerts_count, genesis_events_count,
                           assignee_email, assignee_roles, created_at, created_by_scwx, notified_at, updated_at, deleted_at,
                           acknowledged, acknowledge_time, initial_acknowledge_time, acknowledged_at_least_once,
                           handed_off, handoff_time, initial_handoff_time, handed_off_at_least_once,
                           resolved, resolution_time, initial_resolution_time, resolved_at_least_once)
            c.execute(insert)
    
            ## Insert alerts into alert_investigation table
            
            for alert in inv['alerts']:
                alert_id = alert['id']
                if len(alert_id) == 36 and alert_id.find(" ") == -1:
                    insert = "INSERT INTO alert_investigation(alert_id, investigation_id, tenant_id) VALUES (\'" +  alert_id + "\', \'" +  id + "\', " +  str(tenant_id) + ");"
                    c.execute(insert)

            ## Insert assets into asset_investigation table
            
            for asset in inv['assets']:
                asset_id = asset['id']
                if len(asset_id) == 36 and asset_id.find(" ") == -1:
                    insert = "INSERT INTO asset_investigation(asset_id, investigation_id, tenant_id) VALUES (\'" +  asset_id + "\', \'" +  id + "\', " +  str(tenant_id) + ");"
                    c.execute(insert)

            
        ## Commit transaction
        db.commit()
        log("-- Inserted " + str(i) + " investigations into database")
    else:
        log("-- No investigations returned")

    return(i)


def getAssetFromEntities(entities, dbcursor):
    asset_id = None

    for entity in entities:
        entity_name = entity.split(":")[0]
        entity_value = entity[len(entity_name)+1:]
        if entity_name == "sensorId":
            ## Get asset id from sensor id
            sql = "SELECT id FROM asset WHERE LOWER(sensor_id) = '%s';" % (entity_value)
            dbcursor.execute(sql)
            for t in dbcursor.fetchall():
                asset_id = t[0]
    return(asset_id)
    
        


def fetch_alerts(api, tenant_id):
    ## Import alerts
    query = """
      query alerts($after: Time!, $before: Time!) {
        alertsByDate(after: $after, before: $before, dateFilter: CREATED, page_size: 10000){
          edges {
            id
            alert_type
            confidence
            severity
            creator
            tenant_id
            message
            attack_categories
            related_entities
            data {
              domain
              domain_registration_date { seconds }
              username
              password
              source_ip
              source_port
              destination_ip
              destination_port
              blacklist_name
              blacklist_reason
            }
            investigations
            insert_timestamp { seconds }
            timestamp { seconds }
          }
        }
      }
    """
    ## Query API

    timestamp_now = datetime.datetime.now(datetime.timezone.utc)
    timestamp_yesterday = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours = -24)

    timestamp_to = timestamp_now.strftime("%Y-%m-%dT%H:%M:%SZ")
    timestamp_from = timestamp_yesterday.strftime("%Y-%m-%dT%H:%M:%SZ")

    log("-- Querying API for new alerts between " + timestamp_from + " and " + timestamp_to)

    variables = { "before": timestamp_to, "after": timestamp_from }
    data = api.execute_query(query, variables)
    results = data['data']['alertsByDate']

    ## Start transaction
    c = db.cursor()

    ## clean db
    ## log("Truncating the alerts table - REMOVE AFTER TESTING")
    ## c.execute("TRUNCATE TABLE alert;")

    i = 0
    if results['edges'] is not None:
        for alert in results['edges']:
            i = i + 1
            ## Prepare data
            alert_type = alert['alert_type'].split(":")[0]
            id = alert['id']
            confidence = alert['confidence'] or 0
            severity = alert['severity'] or 0
            creator = alert['creator']

            if alert['related_entities'] is not None:       
                asset_id = getAssetFromEntities(alert['related_entities'], c)

#            tenant_id = alert['tenant_id'][0]
            message = alert['message'].replace("'", r"\'")
            insert_timestamp = format_timestamp(alert['insert_timestamp']['seconds'])
            timestamp = format_timestamp(alert['timestamp']['seconds'])
            domain_registration_date = "1970-01-01 08:00:00+08"
            username = ""
            source_ip = ""
            destination_ip = ""
            source_port = 0
            destination_port = 0
            blacklist_name = ""
            blacklist_reason = ""
            domain = ""
            
            if alert['data'] is not None:
                username = alert['data'][0]['username'] or ""
                source_ip = alert['data'][0]['source_ip'] or ""
                destination_ip = alert['data'][0]['destination_ip'] or ""
                source_port = alert['data'][0]['source_port'] or 0
                destination_port = alert['data'][0]['destination_port'] or 0
                blacklist_name = alert['data'][0]['blacklist_name'] or ""
                blacklist_reason = alert['data'][0]['blacklist_reason'] or ""
                domain = alert['data'][0]['domain'] or ""

                if alert['data'][0]['domain_registration_date']:
                    domain_registration_date = format_timestamp(alert['data'][0]['domain_registration_date']['seconds'])
                else:
                    domain_registration_date = "1970-01-01 08:00:00+08"
                    username = ""
                    source_ip = ""
                    destination_ip = ""
                    source_port = 0
                    destination_port = 0
                    blacklist_name = ""
                    blacklist_reason = ""
                    domain = ""
                
            attack_categories = unroll(alert['attack_categories'])
            
            ## Insert into database
            insert = """
                    INSERT INTO alert(id, alert_type, confidence, severity, creator, tenant_id, message, 
                        insert_timestamp, timestamp, domain_registration_date, username, source_ip, destination_ip, 
                        source_port, destination_port, blacklist_name, blacklist_reason, domain, attack_categories)
                    VALUES ('%s', '%s', %s, %s, '%s', %s, '%s', '%s', '%s', '%s', '%s', '%s', '%s', %s, %s, '%s', '%s', '%s', '%s') ON CONFLICT (id) DO NOTHING;
                    """  % (id, alert_type, confidence, severity, creator, tenant_id, message, insert_timestamp, timestamp, 
                            domain_registration_date, username, source_ip, destination_ip, source_port, destination_port,
                            blacklist_name, blacklist_reason, domain, attack_categories)
            c.execute(insert)

            if asset_id is not None:
                insert = """
                        INSERT INTO alert_asset(alert_id, asset_id, tenant_id)
                        VALUES ('%s', '%s', %s) ON CONFLICT DO NOTHING;
                        """  % (id, asset_id, tenant_id)
                c.execute(insert)               
            
        ## Commit transaction
        db.commit()
        log("-- Inserted " + str(i) + " alerts into database")
    else:
        log("-- No alerts returned")

    return(i)

def parse_tags(api, tenant_id):
    c = db.cursor()

    ## Clean tags tables
    c.execute("DELETE FROM asset_tag;")

    log("-- Extracting asset tags...")

    ## Get assets from database, split tags field (CSV) and put into tags table
    c.execute("SELECT id, tenant_id, tags FROM asset;")
    for asset in c.fetchall():
        asset_id = asset[0]
        tenant_id = asset[1]
        tags = asset[2].strip()

        for tag in tags.split(","):
            if not tag == "":
                sql = """
                    INSERT INTO asset_tag(asset_id, tag, tenant_id) VALUES ('%s', '%s', %i) ON CONFLICT DO NOTHING;
                """ % (asset_id, tag, tenant_id)
                c.execute(sql)
    
    
    
    db.commit()



def update_history(tenant_id, count_assets, count_investigations, count_alerts):
    ## Create update record
    c = db.cursor()
    c.execute("""INSERT INTO history(tenant_id, asset_count, alert_count, investigation_count) 
                VALUES (%i, %i, %i, %i)""" % (tenant_id, count_assets, count_alerts, count_investigations))
    db.commit()
    log("-- Updated history record for tenant")
    


############################################

log("Starting...")

## Initialize connections to database
##db = pymysql.connect(host=creds.db_host, user=creds.db_user, database=creds.db_name, passwd=creds.db_passwd)
db = psycopg2.connect(host=creds.db_host, user=creds.db_user, database=creds.db_name, password=creds.db_passwd)
log("Initialized connections to database")

log("Fetching list of tenants")

sql = "SELECT id, name, api_client_id, api_client_secret, enabled FROM tenant WHERE enabled = 1;"
c = db.cursor()
c.execute(sql)

for t in c.fetchall():
    tenant_name = t[1]
    tenant_id = t[0]
    api_id = t[2]
    api_secret = t[3]
    tenant_enabled = t[4]

    if tenant_enabled:
        log("Fetching data for tenant \'" + tenant_name + "\' [" + str(tenant_id) + "]")
        
        log("-- Initializing API client for tenant " + str(tenant_id))
        api = XDR(client_id=api_id, client_secret=api_secret, tenant_id=tenant_id)
        
        count_assets = fetch_assets(api, tenant_id)
        count_investigations = fetch_investigations(api, tenant_id)
        count_alerts = fetch_alerts(api, tenant_id)


        parse_tags(api, tenant_id)

        
        update_history(tenant_id, count_assets, count_investigations, count_alerts)

log("Closing connection to database...")
db.close()
log("End")
log("")
