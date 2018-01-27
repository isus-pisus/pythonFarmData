import matplotlib.pyplot as plt
from datetime import datetime
from sys import argv
import requests
import iso8601
import json
import time

url = "http://96.43.172.104:3000/points"
query = argv[1]
temperature_array = []
time_array = []
hourly_temp=[]
every_hour=[]
index_array= []
offset_time = 60*60*5

def get_raw_data():
    raw_response = requests.get(url+"/"+argv[1]+ " " +argv[2]+", 2018")

    if (raw_response.ok):
        raw_data = json.loads(raw_response.content)
        raw_data = raw_data['data']

        for data_points in range(len(raw_data)):
            temperature_data = raw_data[data_points]['temp']
            temperature_array.append(temperature_data)
            hour_data = proc_avg_temp(raw_data[data_points]['createdAt'])
            time_array.append(hour_data)
        max_hour=time_array[-1]+1

        for hour in range(time_array[0], max_hour):
            list_of_index=time_array.index(hour)
            index_array.append(list_of_index)

        for index_amount in range(0, len(index_array)):
            lower_limit=index_amount
            upper_limit=index_amount+1

            if lower_limit == len(index_array)-1:
                last_max=len(temperature_array)
                average_temp = temperature_array[index_array[lower_limit]:last_max]
                total_avg = (sum(float(total) for total in average_temp[0:len(average_temp)]))/len(average_temp)
                hourly_temp.append(round(total_avg, 2))
                hour = time_array[index_array[lower_limit]:last_max][0]
                every_hour.append(hour)

                plt.plot(every_hour, hourly_temp)
                plt.ylabel('Hourly temp')
                # plt.ylim()
                plt.ylim(ymin=28)
                plt.ylim(ymin=28, ymax=40)
                plt.show()

                break

            average_temp = temperature_array[index_array[lower_limit]:index_array[upper_limit]]
            total_avg = (sum(float(total) for total in average_temp[0:len(average_temp)]))/len(average_temp)
            hourly_temp.append(round(total_avg, 2))
            average_hour = time_array[index_array[lower_limit]:index_array[upper_limit]]
            hour = time_array[index_array[lower_limit]:index_array[upper_limit]][0]
            every_hour.append(hour)

def proc_avg_temp(timestamp):
    return int(datetime.fromtimestamp(int(timestamp)).strftime('%H'))

if __name__ == "__main__":
    get_raw_data()
