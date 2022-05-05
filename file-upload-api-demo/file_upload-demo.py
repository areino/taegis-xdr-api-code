import creds
from taegis.taegis import XDR

api = XDR(client_id=creds.id, client_secret=creds.secret, tenant_id=creds.tenant)
data = api.upload_file("CustomAppLog", "testfile3.txt")
print(data)
