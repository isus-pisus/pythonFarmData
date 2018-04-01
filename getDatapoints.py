from dotenv import load_dotenv
from os.path import join, dirname
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime
from bson.objectid import ObjectId
from sys import argv
import numpy as np
import argparse
import requests
import json
import bson
import time
import pytz
import os


parser = argparse.ArgumentParser(description='Process data from farm API.')
parser.add_argument('month', metavar='M', type=int, help='Numerical value of the month to query')
parser.add_argument('day', metavar='D', type=int, help='Numerical value of the day to query')
parser.add_argument('year', metavar='YYYY', type=int, help='Year to query')
args = parser.parse_args()

dotenvPath = join(dirname(__file__), '.env')
load_dotenv(dotenvPath)

url = "http://"+str(os.environ.get("IP"))+":3000/points"
query = argv[1]
temperature_array = []
time_array = []
hourly_temp = []
every_hour = []
index_array = []
offset_time = 60*60*5

# make call to API and format data


def processRawData():
    raw_response = requests.get(url+"/"+str(proc_unix_time(args.month, args.day, args.year)))

    if (raw_response.ok):
        raw_data = json.loads(raw_response.content)
        raw_data = raw_data['data']
        # print(raw_data)
        for data_points in range(len(raw_data)):
            temperature_data = raw_data[data_points]['temp']
            temperature_array.append(temperature_data)
            hour_data = proc_avg_temp(raw_data[data_points]['_id'])
            time_array.append(hour_data)
        max_hour = time_array[-1]+1

        for hour in range(time_array[0], max_hour):
            try:
                list_of_index = time_array.index(hour)
                index_array.append(list_of_index)
            except ValueError:
                pass

        for index_amount in range(0, len(index_array)):

            lower_limit = index_amount
            upper_limit = index_amount+1
            hour = time_array[index_array[lower_limit]]
            every_hour.append(hour)
            # print(every_hour)

            try:
                """average the temperature"""
                average_temp = np.average(
                    temperature_array[index_array[lower_limit]:index_array[upper_limit]])
                hourly_temp.append(round(average_temp, 2))

            except IndexError:
                """Index out of range, average all the data at index 23"""
                average_temp = np.average(
                    temperature_array[index_array[lower_limit]:])
                hourly_temp.append(round(average_temp, 2))
                break

        # print(hourly_temp)
        # print(every_hour)
        plt.plot(every_hour, hourly_temp)
        plt.ylabel('Hourly temp')
        plt.ylim(ymin=28, ymax=40)
        plt.show()

    return [
        hourly_temp,
        every_hour
    ]
# format UTC to get the hour the data was logged


def proc_avg_temp(timestamp):
    date_from_ObjectId = ObjectId(timestamp).generation_time.astimezone(
        pytz.timezone("America/Jamaica")).timetuple()
    return int(date_from_ObjectId.tm_hour)


def proc_unix_time(MM, D, YYYY):
    unix_timestamp = time.mktime(datetime(int(YYYY), int(MM), int(D)).timetuple())
    return round(unix_timestamp)


if __name__ == "__main__":
    processRawData()
