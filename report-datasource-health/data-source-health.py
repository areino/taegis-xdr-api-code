from taegis import XDR
import creds
import os
import datetime
import socket

no_alert = []
recent_alerts = []

stat_sources = 0
stat_green = 0
stat_red = 0
stat_yellow = 0
stat_skipped = 0
stat_sent = 0

FACILITY = {
    'kern': 0, 'user': 1, 'mail': 2, 'daemon': 3,
    'auth': 4, 'syslog': 5, 'lpr': 6, 'news': 7,
    'uucp': 8, 'cron': 9, 'authpriv': 10, 'ftp': 11,
    'local0': 16, 'local1': 17, 'local2': 18, 'local3': 19,
    'local4': 20, 'local5': 21, 'local6': 22, 'local7': 23,
}

LEVEL = {
    'emerg': 0, 'alert':1, 'crit': 2, 'err': 3,
    'warning': 4, 'notice': 5, 'info': 6, 'debug': 7
}




def syslog(message, level=LEVEL['notice'], facility=FACILITY['local7'], host='localhost', port=514):
    
    # Send syslog UDP packet to given host and port.

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    data = '<%d>%s' % (level + facility*8, message)
    sock.sendto(data.encode(), (host, port))
    sock.close()


def log(s):
    print(datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M:%S") + '  ' + str(s))

def format_timestamp(seconds):
    ts = datetime.datetime.fromtimestamp(seconds)
    return(ts.strftime('%Y-%m-%d %H:%M:%S'))



#############################################################
#############################################################

def getNoAlertList():
    filename = creds.no_alert_list_filename
    if os.path.exists(filename):
        # Load no-alert list into array
        log("-- Loading no-alert list from " + filename)
        with open(filename, 'r') as f:
            for row in f:
                if row != "":
                    no_alert.append(row.strip().lower())
    else:
        log("-- No no-alert list exists")


def getRecentAlerts():
    filename = creds.recent_alerts_filename
    if os.path.exists(filename):
        # Load list into array
        log("-- Loading recent alert list from " + filename)
        with open(filename, 'r') as f:
            for row in f:
                if row.strip() != "":
                    recent_alerts.append(row.strip().lower())
    else:
        log("-- No recent alert list exists")

def writeRecentAlerts():
    filename = creds.recent_alerts_filename
    log("-- Updating recent alert list to " + filename)
    with open(filename, 'w') as f:
        for line in recent_alerts:
            f.write(line + '\n')


def purgeRecentAlerts():
    now = int(datetime.datetime.now().timestamp())
    for alert in recent_alerts:
        source = alert.strip().lower().split(',')[0]
        health = alert.strip().lower().split(',')[1]
        sec = alert.strip().lower().split(',')[2]

        days = int((now - int(sec))/(24*60*60))
        if days >= creds.purge_alerts_after_days:
            recent_alerts.remove(alert)


def addRecentAlert(source, health):
    recent_alerts.append(source.strip().lower() + "," + health.strip().lower() + "," + str(int(datetime.datetime.now().timestamp())))

def isRecentAlert(source, health):
    recent = False
    for alert in recent_alerts:
        recentsource = alert.strip().lower().split(',')[0]
        recenthealth = alert.strip().lower().split(',')[1]
        if source.strip().lower() == recentsource and health.strip().lower() == recenthealth:
            recent = True
    return(recent)

def alert(source, health, message):

    global stat_green
    global stat_red
    global stat_yellow
    global stat_skipped
    global stat_sent

    status = ""
    level = 0


    # LogLastSeenMetric contains all of the relevant metadata to identify a log source as well as a 'lastSeen' timestamp which stores the last time that this log source 
    # was seen. A health status is also determined based on the recent ingest rate from this log source and how it compares to its historical ingest rate. 
    # 1 standard deviation away from the historical average is considered to be 'HEALTHY'. Anything greater than 1 but less than 2 standard deviations away is considered 
    # 'DEGRADED'. Anything greater than 2 standard deviations is considered 'UNHEALTHY'. If a health status cannot be determined due to an error or insufficient data then 
    # the returned health status will be 'UNKNOWN'.

    # Determine criticality
    if health == "HEALTHY":
        level = 7
        stat_green += 1
    elif health == "WARNING" or health == "DEGRADED":
        level = 4
        stat_yellow += 1
    elif health == "UNHEALTHY":
        level = 3
        stat_red += 1
    elif health == "UNKNOWN" or health == "NODATA":
        level = 5
        stat_yellow += 1
    else:
        level = 6
        stat_yellow += 1


    if source.strip().lower() in no_alert:
        status = "[no-alert list, skipping]"
        stat_skipped += 1
    else:
        if isRecentAlert(source, health):
            status = "[recent alert, skipping]"
            stat_skipped += 1
        else:
            # Send syslog
            if level < 7:
                status = "[alert, level=" + str(level) + "]"
                syslog(message, level=level, facility=FACILITY['local7'], host=creds.syslog_ip, port=creds.syslog_port)
                stat_sent += 1
            
                # Add to recent alerts
                addRecentAlert(source.strip().lower(), health.strip().lower())

    if level < 7:  
        log("-- " + message + " " + status)
                


def getCollectors():
    a = []

    # query { getCollectorMetrics ( timeRange: LASTHOUR ) { lastSeen } }
    # - Call getCollectorMetrics and iterate on averageRate.metric.collector IDs

    query = 'query { getCollectorMetrics ( timeRange: LASTHOUR ) { lastSeen } }'
    data = api.execute_query(query)
    for c in data['data']['getCollectorMetrics']['lastSeen']:
        a.append(c['metric']['collector'])
    
    return(a)


def getSourcesForCollector(collector_id):

    # query { getLogLastSeenMetrics ( clusterID: "366e3799-89ed-4349-bcd3-b33f76a7486a" ) { logMetrics { sourceID clusterName service sensorType lastSeen health } } }

    query = '''
        query getlogmetrics($id: ID!)
        { 
            getLogLastSeenMetrics ( clusterID: $id ) 
            { 
                logMetrics { sourceID clusterName service sensorType lastSeen health } 
            } 
        }
    '''    
    variables = { "id": collector_id }
    data = api.execute_query(query, variables)

    return(data['data']['getLogLastSeenMetrics']['logMetrics'])




#############################################################
#############################################################
## Main workflow

red_alerts = 0
yellow_alerts = 0
log_sources = 0

# Initialize API connection
log("-- Initializing API client for tenant")
api = XDR(client_id=creds.tenant_api_id, client_secret=creds.tenant_api_secret, tenant_id=creds.tenant_id)


# Get no-alert whitelist
getNoAlertList()

# Get recent alerts and purge those over configured number of days
getRecentAlerts()
purgeRecentAlerts()


# Get XDR data collectors and get log sources for each

log("-- Querying API for XDR collectors")
for col in getCollectors():

    log("-- Getting log sources for XDR Collector " + col)
    sources = getSourcesForCollector(col)

    # Iterate log sources

    for source in sources:
        sourceID = source['sourceID']
        health = source['health']
        lastSeen = source['lastSeen']
        sensorType = source['sensorType']
        service = source['service']
        
        stat_sources += 1

        message = sourceID + " of type " +  sensorType + " (" + service + "), last seen at " + lastSeen + ", is considered " + health

        # Create alert if needed
        alert(sourceID, health, message)

writeRecentAlerts()

log("-- " + str(stat_sources) + " log sources")
log("-- " + str(stat_green) + " green, " + str(stat_yellow) + " yellow, " + str(stat_red) + " red")
log("-- " + str(stat_sent) + " alerts sent, " + str(stat_skipped) + " skipped")
log("-- End")
log("")
