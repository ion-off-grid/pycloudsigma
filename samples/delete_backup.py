#! /usr/bin/env python3
import argparse
from datetime import datetime, timedelta, timezone
import sys

from pprint import pprint
import cloudsigma

parser = argparse.ArgumentParser()
parser.add_argument('--days_old', default=0, help='The number of days after which the backups can be removed')
parser.add_argument('--drive_uuid', help='UUID of the Cloudsigma drive')
parser.add_argument('otp', help='OTP for Cloudsigma connection')
args = parser.parse_args()
cutoff_time = datetime.now(tz=timezone.utc) - timedelta(days=args.days_old)

client = cloudsigma.generic.GenericClient(login_method='session', otp=args.otp)
drive = cloudsigma.resource.Drive()
drive.c = client
backups = cloudsigma.resource.RemoteSnapshots()
backups.c = client

pprint(drive.list())


drive_details = drive.list_detail()
drive_backups = []
for d in drive_details:
    if d['remote_snapshots']:
        if args.drive_uuid is None or (args.drive_uuid and d['uuid'] == args.drive_uuid):
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
                # backups.delete(uuid=snap['uuid'])
        except cloudsigma.errors.ClientError as e:
            print(e)
            continue


