import boto3
from taegis import XDR
import creds
import os
import datetime
import time
import sys
from threading import Thread, Lock
import threading
import gzip


already_uploaded = []
count = 0
started = []

#############################################################
#############################################################
## Subroutines

def log(s):
    print(datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M:%S") + '  ' + str(s))



def format_timestamp(seconds):
    ts = datetime.datetime.fromtimestamp(seconds)
    return(ts.strftime('%Y-%m-%d %H:%M:%S'))

def readUploaded():
    global already_uploaded

    if os.path.exists(creds.already_uploaded_file):
        with open(creds.already_uploaded_file, 'r') as f:
            for row in f:
                if row[:-2].strip() != "":
                    already_uploaded.append(row.strip().lower())

    already_uploaded = list(dict.fromkeys(already_uploaded))
    return(len(already_uploaded))
                
def noteUploaded(filename):
    global already_lock

    already_lock.acquire()
    try:
        with open(creds.already_uploaded_file, 'a') as f:
            f.write(filename + '\n')
    finally:
        already_lock.release()

def alreadyUploaded(filename):
    global already_uploaded
    
    if (filename) in already_uploaded:
        return(True)
    else:
        return(False)

def gunzip(s3path, filename):
    global count
    global working_lock

    # Download file from S3
    try:
        bucket.download_file(s3path, filename)
    except:
        log("-- ERROR: Could not download " + s3path)
        return(False)
    else:
        # Uncompress and add to working file
        if os.path.exists(filename):
            
            fin = gzip.open(filename, 'rb')
            rows = fin.readlines()

            working_lock.acquire()
            try:
                fout = open(creds.working_file, 'ab')
                for row in rows:
                    fout.write(row)
            finally:
                fin.close()
                fout.close()
                working_lock.release()

            # Delete file after processed
            os.remove(filename)
            # Make note of files already processed
            log("--  Downloaded and uncompressed " + filename)
            noteUploaded(s3path)
            count = count + 1
            return(True)
        else:
            return(False)
       



#############################################################
#############################################################
## Main workflow


log("-- Initializing...")

working_lock = threading.Lock()
already_lock = threading.Lock()


# Open list of files already uploaded to Taegis XDR
log("-- Already uploaded: " + str(readUploaded()))

# Open S3 bucket

s3bucket = creds.s3datapath.split("/")[0]
s3folder = creds.s3datapath.split("/")[1]

log("-- Opening S3 bucket")
log("--   Bucket name: " + s3bucket)
log("--   Folder     : " + s3folder)

try:
    aws = boto3.Session(aws_access_key_id=creds.s3accesskey, aws_secret_access_key=creds.s3secretkey)
except:
    log("-- ERROR: Not able to create AWS session, possibly invalid credentials")
    sys.exit("Cannot connect to AWS")
log("-- Connected to AWS")

try:
    s3 = aws.resource('s3')
    bucket = s3.Bucket(s3bucket)
except:
    log("-- ERROR: Cannot open " + s3bucket + " bucket")
    sys.exit("Cannot open bucket")
log("-- Opened " + s3bucket + " bucket")

# Get contents 

try:
    s3files = bucket.objects.filter(Prefix = s3folder + "/")
except:
    log("-- ERROR: Cannot list contents of  " + s3folder)
    sys.exit("Cannot list contents")
log("-- Listing contents of " + s3folder + " folder")


# Initialize working file
if not os.path.exists(creds.working_file):
    with open(creds.working_file, "w") as f:
        f.write("\n")



# Initialize API connection

try:
    api = XDR(client_id=creds.xdrid, client_secret=creds.xdrsecret, tenant_id=creds.xdrtenant)
except:
    log("-- ERROR: Not able to create Taegis XDR API session, possibly invalid credentials")
    sys.exit("Cannot connect to Taegis XDR API")
log("-- Connected to Taegis XDR (tenant: " + str(creds.xdrtenant) + ")")


# Iterate contents

log("-- Maximum parallel threads = " + str(creds.max_threads))

for item in s3files: 

    # Check max size of working file
    if os.path.getsize(creds.working_file) > creds.max_uncompressed_bytes:
        log("-- Max uncompressed file reached, did not finish processing pending logs")
        break


    if threading.active_count() >= creds.max_threads + 1:
        ## Max threads reached, join as many as possible
        for thread in started:
            thread.join()
            started.remove(thread)

    item_path = item.key
    item_filename = item_path.split("/")[3].strip().lower()
    item_type = item_path.split("/")[1].strip().lower()

    if item_type == "dnslogs" or item_type == "auditlogs":
        if not alreadyUploaded(item_path):
            # Upload file to File Upload API
            if threading.active_count() < creds.max_threads + 1:
                started.append(Thread(target=gunzip, args=(item_path, item_filename)))
                started[-1].start()
                ## log("-- Started new thread, total " + str(threading.active_count()) + " active")
        #else:
        #    log("--  Skipping " + item_filename)

## Wait for threads to finish
while threading.active_count() > 1:
    log("-- Closing down parallel threads (remaining: " + str(threading.active_count()) + ")")
    time.sleep(2)

log("-- Number of files processed = " + str(count))

# Prepare output file
if os.path.exists(creds.working_file):

    # Compress file
    log("-- Compressing logs before uploading")
    with open(creds.working_file, 'rb') as f_in, gzip.open(creds.working_file + '.gz', 'wb') as f_out:
        f_out.writelines(f_in)


    # Check max size of compressed file
    if os.path.getsize(creds.working_file + '.gz') > creds.max_compressed_bytes:
        log("-- Compressed logs file too large for upload")
    else:
        # Upload file
        log("-- Uploading...")
        ret = api.upload_file("CISCO_UMBRELLA", creds.working_file + '.gz')
        if ret == b'':
            log("-- Uploaded telemetry to Taegis!")
        else:
            log("-- Upload failed!")
            print(ret)
    
    # Delete file after uploaded
    os.remove(creds.working_file)
    os.remove(creds.working_file + '.gz')
    log("-- Deleted working files")

    log("-- End")