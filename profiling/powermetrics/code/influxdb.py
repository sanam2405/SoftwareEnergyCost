from datetime import datetime
import signal
import sys
import subprocess

from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS

token = "<API_KEY>"
org = "CERN"
bucket = "baler"

client = InfluxDBClient(url="http://localhost:8086", token=token, org=org)
write_api = client.write_api(write_options=SYNCHRONOUS)

process = subprocess.Popen("/usr/bin/powermetrics -i 300 --samplers cpu_power -a --hide-cpu-duty-cycle", shell=True, stdout=subprocess.PIPE, bufsize=3)
while True:
    out = process.stdout.readline().decode()
    if out == '' and process.poll() != None:
        break
    if out != '':
        if ' Power: ' in out:
            metrics = out.split(' Power: ')
            point = Point(metrics[0]) \
                .tag("host", "host1") \
                .field("power", int(metrics[1].replace('mW', ''))) \
                .time(datetime.utcnow(), WritePrecision.NS)

            write_api.write(bucket, org, point)
            sys.stdout.flush()


with subprocess.Popen("/usr/bin/powermetrics -i 300 --samplers cpu_power -a --hide-cpu-duty-cycle | grep -B 2 'GPU Power'", shell=True, stdout=subprocess.PIPE, bufsize=3) as p:
    for c in iter(lambda: p.stdout.readline(), b''):
        sys.stdout.write(c)
    for line in p.stdout.read():
        metrics = line.split(' Power: ')
        print(line)