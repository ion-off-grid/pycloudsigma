#! /usr/bin/env python3
import argparse
from datetime import datetime, timedelta, timezone
import sys

from pprint import pprint
import cloudsigma

parser = argparse.ArgumentParser()
parser.add_argument('otp', help='OTP for Cloudsigma connection')
args = parser.parse_args()

client = cloudsigma.generic.GenericClient(login_method='session', otp=args.otp)
backups = cloudsigma.resource.RemoteSnapshots()
backups.c = client

drive_backups = backups.list()
for backup in drive_backups:
    if not backup['drive']:
        print(f"Removing orphaned disk backup for disk {backup['drive_meta']}, backup uuid {backup['uuid']}, created at {backup['timestamp']}")
        try:
            backups.delete(uuid=backup['uuid'])
        except cloudsigma.errors.ClientError as e:
            print(e)
            continue
