#! /usr/bin/env python3
from datetime import datetime, timedelta, timezone
import sys

from pprint import pprint
import cloudsigma

backup_retention_days = 7
cutoff_time = datetime.now(tz=timezone.utc) - timedelta(days=backup_retention_days)

client = cloudsigma.generic.GenericClient(login_method='session', otp=sys.argv[1])
drive = cloudsigma.resource.Drive()
drive.c = client
backups = cloudsigma.resource.RemoteSnapshots()
backups.c = client

pprint(drive.list())

drive_details = drive.list_detail()
drive_backups = []
for d in drive_details:
    if d['remote_snapshots']:
        drive_backups.append({
            'uuid': d['uuid'],
            'name': d['name'],
            'backups': d['remote_snapshots']
            })
pprint(drive_backups)

for backup in drive_backups:
    snapshot_uuids = backup['backups']
    for snap in snapshot_uuids:
        try:
            b = backups.get(uuid=snap['uuid'])
            b_timestamp = datetime.fromisoformat(b['timestamp'])
            if b_timestamp < cutoff_time:
                print(f"Removing disk backup for disk {backup['name']}, backup uuid {snap['uuid']}, created at {b_timestamp}")
                backups.delete(uuid=snap['uuid'])
        except cloudsigma.errors.ClientError as e:
            print(e)
            continue


