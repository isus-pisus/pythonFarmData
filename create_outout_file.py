from dotenv import load_dotenv
from os.path import join, dirname
from datetime import datetime
from bson.objectid import ObjectId
from sys import argv
import argparse
import requests
import json
import bson
import time
import pytz
import os, csv


parser = argparse.ArgumentParser(description='Save data to a csv file')
parser.add_argument('--start', metavar='start', type=str, help='Y-mm-d')
parser.add_argument('--end', metavar='end', type=str, help='Y-mm-d')
parser.add_argument('--output', metavar='output', type=str, help='Name of output file')

args = parser.parse_args()

dotenvPath = join(dirname(__file__), '.env')
load_dotenv(dotenvPath)

url = "http://"+str(os.environ.get("IP"))+":3000/points"
query = argv[1]
temperature_array = []
time_array = []
hourly_temp = []


#if no output file name is specified the fame of the file is set to the current time

if args.output == None:
    filename = datetime.today()
else:
    filename = args.output


# make call to API and format data
def processRawData():
    start = str(proc_unix_time(args.start))
    end = str(proc_unix_time(args.end))

    raw_response = requests.get(url+"/?start="+start+"&end="+end)
    if (raw_response.ok):
        raw_data = json.loads(raw_response.content)
        raw_data = raw_data['data']
        # print(raw_data)
        for data_points in range(len(raw_data)):
            temperature_data = raw_data[data_points]['temp']
            temperature_array.append(temperature_data)
            hour_data = proc_avg_temp(raw_data[data_points]['_id'])
            time_array.append(hour_data)

        with open('{}.csv'.format(filename), 'w',) as csvfile:
            fieldnames = ['Index', 'Time', 'Temperature']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames, quotechar=' ',)
            writer.writeheader()
            for x in range(0, len(raw_data)):
                writer.writerow({'Index': x ,'Time': time_array[x], 'Temperature' : temperature_array[x]})


# format UTC to get the hour the data was logged
def proc_avg_temp(timestamp):
    date_from_ObjectId = ObjectId(timestamp).generation_time.astimezone(
        pytz.timezone("America/Jamaica"))
    return date_from_ObjectId


def proc_unix_time(timestamp):
    unix_time = datetime.strptime(timestamp, "%Y-%m-%d").timetuple()
    unix_timestamp = time.mktime(datetime(unix_time.tm_year, unix_time.tm_mon, unix_time.tm_mday).timetuple())
    return round(unix_timestamp)


if __name__ == "__main__":
    processRawData()
