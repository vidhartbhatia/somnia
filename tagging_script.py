# importing csv module 
import csv 
import datetime
import statistics
import os
import pprint
pp = pprint.PrettyPrinter()
pprint = pp.pprint
  
# csv file name 
dataFolder = "udit 5-9"
data_file_name = "50926"
ROW_LIMIT = None # set to none if want all
  
# initializing the titles and rows list 
# fields = [] 
rows = [] 

  
# reading csv file 
with open(f"Data{os.sep}{dataFolder}{os.sep}{data_file_name}.csv", 'r') as csvfile: 
    # creating a csv reader object 
    csvreader = csv.DictReader(csvfile)
      
    # # extracting field names through first row 
    fields = csvreader.fieldnames 

    rows = list(csvreader)[:ROW_LIMIT]
    if ROW_LIMIT!=None:
        rows = rows[:ROW_LIMIT]
    # get total number of rows 
    print(f"Total no. of rows: {len(rows)}")
  
# printing the field names 
# print('Field names are:' + ', '.join(field for field in fields)) 
  
# start_time_str = "4/20/2020  5:21 AM"
# start_time = datetime.datetime.strptime(start_time_str, '%m/%d/%Y  %I:%M %p')
# pprint(rows[:10])
start_time = datetime.datetime.fromtimestamp(int(rows[0]['time_stamp'])/1000)

print('Start time:', start_time)

sampling_rate = 10
num_minutes = len(rows) // int((sampling_rate * 60))
print(f"{num_minutes//60} hours and {num_minutes%60} minutes")

minutes = ['minutes']
curr_time = start_time
for i in range(num_minutes):
    minutes.append(curr_time.strftime('%I:%M %p'))
    curr_time += datetime.timedelta(seconds=60)

accXs1 = [[] for i in range(num_minutes-1)]
accYs1 = [[] for i in range(num_minutes-1)]
accZs1 = [[] for i in range(num_minutes-1)]

accXs5 = [[] for i in range(num_minutes-1)]
accYs5 = [[] for i in range(num_minutes-1)]
accZs5 = [[] for i in range(num_minutes-1)]

accXs10 = [[] for i in range(num_minutes-1)]
accYs10 = [[] for i in range(num_minutes-1)]
accZs10 = [[] for i in range(num_minutes-1)]

accXs20 = [[] for i in range(num_minutes-1)]
accYs20 = [[] for i in range(num_minutes-1)]
accZs20 = [[] for i in range(num_minutes-1)]

accXs30 = [[] for i in range(num_minutes-1)]
accYs30 = [[] for i in range(num_minutes-1)]
accZs30 = [[] for i in range(num_minutes-1)]

points_per_min = sampling_rate * 60

for j in range(1, num_minutes):
    # don't judge for this i am sleepy
    # 1
    for i in range(max(0, (j-1) * points_per_min), j * points_per_min):
        accXs1[j-1].append(float(rows[i]['accX']))
        accYs1[j-1].append(float(rows[i]['accY']))
        accZs1[j-1].append(float(rows[i]['accZ']))

    # 5
    for i in range(max(0, (j-5) * points_per_min), j * points_per_min):
        accXs5[j-1].append(float(rows[i]['accX']))
        accYs5[j-1].append(float(rows[i]['accY']))
        accZs5[j-1].append(float(rows[i]['accZ']))

    # 10
    for i in range(max(0, (j-10) * points_per_min), j * points_per_min):
        accXs10[j-1].append(float(rows[i]['accX']))
        accYs10[j-1].append(float(rows[i]['accY']))
        accZs10[j-1].append(float(rows[i]['accZ']))

     # 20
    for i in range(max(0, (j-20) * points_per_min), j * points_per_min):
        accXs20[j-1].append(float(rows[i]['accX']))
        accYs20[j-1].append(float(rows[i]['accY']))
        accZs20[j-1].append(float(rows[i]['accZ']))

     # 30
    for i in range(max(0, (j-30) * points_per_min), j * points_per_min):
        accXs30[j-1].append(float(rows[i]['accX']))
        accYs30[j-1].append(float(rows[i]['accY']))
        accZs30[j-1].append(float(rows[i]['accZ']))

# mean
accX_means1 = ['accX_means1'] + [statistics.mean(x) for x in accXs1]
accY_means1 = ['accY_means1'] + [statistics.mean(x) for x in accYs1]
accZ_means1 = ['accZ_means1'] + [statistics.mean(x) for x in accZs1]
accX_means5 = ['accX_means5'] + [statistics.mean(x) for x in accXs5]
accY_means5 = ['accY_means5'] + [statistics.mean(x) for x in accYs5]
accZ_means5 = ['accZ_means5'] + [statistics.mean(x) for x in accZs5]
accX_means10 = ['accX_means10'] + [statistics.mean(x) for x in accXs10]
accY_means10 = ['accY_means10'] + [statistics.mean(x) for x in accYs10]
accZ_means10 = ['accZ_means10'] + [statistics.mean(x) for x in accZs10]
accX_means20 = ['accX_means20'] + [statistics.mean(x) for x in accXs20]
accY_means20 = ['accY_means20'] + [statistics.mean(x) for x in accYs20]
accZ_means20 = ['accZ_means20'] + [statistics.mean(x) for x in accZs20]
accX_means30 = ['accX_means30'] + [statistics.mean(x) for x in accXs30]
accY_means30 = ['accY_means30'] + [statistics.mean(x) for x in accYs30]
accZ_means30 = ['accZ_means30'] + [statistics.mean(x) for x in accZs30]

# median
accX_medians1 = ['accX_medians1'] + [statistics.median(x) for x in accXs1]
accY_medians1 = ['accY_medians1'] + [statistics.median(x) for x in accYs1]
accZ_medians1 = ['accZ_medians1'] + [statistics.median(x) for x in accZs1]
accX_medians5 = ['accX_medians5'] + [statistics.median(x) for x in accXs5]
accY_medians5 = ['accY_medians5'] + [statistics.median(x) for x in accYs5]
accZ_medians5 = ['accZ_medians5'] + [statistics.median(x) for x in accZs5]
accX_medians10 = ['accX_medians10'] + [statistics.median(x) for x in accXs10]
accY_medians10 = ['accY_medians10'] + [statistics.median(x) for x in accYs10]
accZ_medians10 = ['accZ_medians10'] + [statistics.median(x) for x in accZs10]
accX_medians20 = ['accX_medians20'] + [statistics.median(x) for x in accXs20]
accY_medians20 = ['accY_medians20'] + [statistics.median(x) for x in accYs20]
accZ_medians20 = ['accZ_medians20'] + [statistics.median(x) for x in accZs20]
accX_medians30 = ['accX_medians30'] + [statistics.median(x) for x in accXs30]
accY_medians30 = ['accY_medians30'] + [statistics.median(x) for x in accYs30]
accZ_medians30 = ['accZ_medians30'] + [statistics.median(x) for x in accZs30]

# max
accX_maxes1 = ['accX_maxes1'] + [max(x) for x in accXs1]
accY_maxes1 = ['accY_maxes1'] + [max(x) for x in accYs1]
accZ_maxes1 = ['accZ_maxes1'] + [max(x) for x in accZs1]
accX_maxes5 = ['accX_maxes5'] + [max(x) for x in accXs5]
accY_maxes5 = ['accY_maxes5'] + [max(x) for x in accYs5]
accZ_maxes5 = ['accZ_maxes5'] + [max(x) for x in accZs5]
accX_maxes10 = ['accX_maxes10'] + [max(x) for x in accXs10]
accY_maxes10 = ['accY_maxes10'] + [max(x) for x in accYs10]
accZ_maxes10 = ['accZ_maxes10'] + [max(x) for x in accZs10]
accX_maxes20 = ['accX_maxes20'] + [max(x) for x in accXs20]
accY_maxes20 = ['accY_maxes20'] + [max(x) for x in accYs20]
accZ_maxes20 = ['accZ_maxes20'] + [max(x) for x in accZs20]
accX_maxes30 = ['accX_maxes30'] + [max(x) for x in accXs30]
accY_maxes30 = ['accY_maxes30'] + [max(x) for x in accYs30]
accZ_maxes30 = ['accZ_maxes30'] + [max(x) for x in accZs30]

# min
accX_mins1 = ['accX_mins1'] + [min(x) for x in accXs1]
accY_mins1 = ['accY_mins1'] + [min(x) for x in accYs1]
accZ_mins1 = ['accZ_mins1'] + [min(x) for x in accZs1]
accX_mins5 = ['accX_mins5'] + [min(x) for x in accXs5]
accY_mins5 = ['accY_mins5'] + [min(x) for x in accYs5]
accZ_mins5 = ['accZ_mins5'] + [min(x) for x in accZs5]
accX_mins10 = ['accX_mins10'] + [min(x) for x in accXs10]
accY_mins10 = ['accY_mins10'] + [min(x) for x in accYs10]
accZ_mins10 = ['accZ_mins10'] + [min(x) for x in accZs10]
accX_mins20 = ['accX_mins20'] + [min(x) for x in accXs20]
accY_mins20 = ['accY_mins20'] + [min(x) for x in accYs20]
accZ_mins20 = ['accZ_mins20'] + [min(x) for x in accZs20]
accX_mins30 = ['accX_mins30'] + [min(x) for x in accXs30]
accY_mins30 = ['accY_mins30'] + [min(x) for x in accYs30]
accZ_mins30 = ['accZ_mins30'] + [min(x) for x in accZs30]

# variance
accX_variances1 = ['accX_variances1'] + [statistics.variance(x) for x in accXs1]
accY_variances1 = ['accY_variances1'] + [statistics.variance(x) for x in accYs1]
accZ_variances1 = ['accZ_variances1'] + [statistics.variance(x) for x in accZs1]
accX_variances5 = ['accX_variances5'] + [statistics.variance(x) for x in accXs5]
accY_variances5 = ['accY_variances5'] + [statistics.variance(x) for x in accYs5]
accZ_variances5 = ['accZ_variances5'] + [statistics.variance(x) for x in accZs5]
accX_variances10 = ['accX_variances10'] + [statistics.variance(x) for x in accXs10]
accY_variances10 = ['accY_variances10'] + [statistics.variance(x) for x in accYs10]
accZ_variances10 = ['accZ_variances10'] + [statistics.variance(x) for x in accZs10]
accX_variances20 = ['accX_variances20'] + [statistics.variance(x) for x in accXs20]
accY_variances20 = ['accY_variances20'] + [statistics.variance(x) for x in accYs20]
accZ_variances20 = ['accZ_variances20'] + [statistics.variance(x) for x in accZs20]
accX_variances30 = ['accX_variances30'] + [statistics.variance(x) for x in accXs30]
accY_variances30 = ['accY_variances30'] + [statistics.variance(x) for x in accYs30]
accZ_variances30 = ['accZ_variances30'] + [statistics.variance(x) for x in accZs30]

tags = ['tags'] + ['' for i in range(num_minutes)]

rows = zip(minutes, tags, accX_means1, accY_means1, accZ_means1, accX_medians1, accY_medians1, accZ_medians1, accX_maxes1, accY_maxes1, \
    accZ_maxes1, accX_mins1, accY_mins1, accZ_mins1, accX_variances1, accY_variances1, accZ_variances1, \
    accX_means5, accY_means5, accZ_means5, accX_medians5, accY_medians5, accZ_medians5, accX_maxes5, accY_maxes5, \
    accZ_maxes5, accX_mins5, accY_mins5, accZ_mins5, accX_variances5, accY_variances5, accZ_variances5, \
    accX_means10, accY_means10, accZ_means10, accX_medians10, accY_medians10, accZ_medians10, accX_maxes10, accY_maxes10, \
    accZ_maxes10, accX_mins10, accY_mins10, accZ_mins10, accX_variances10, accY_variances10, accZ_variances10, \
    accX_means20, accY_means20, accZ_means20, accX_medians20, accY_medians20, accZ_medians20, accX_maxes20, accY_maxes20, \
    accZ_maxes20, accX_mins20, accY_mins20, accZ_mins20, accX_variances20, accY_variances20, accZ_variances20, \
    accX_means30, accY_means30, accZ_means30, accX_medians30, accY_medians30, accZ_medians30, accX_maxes30, accY_maxes30, \
    accZ_maxes30, accX_mins30, accY_mins30, accZ_mins30, accX_variances30, accY_variances30, accZ_variances30)

outFile = f"Tagging{os.sep}{dataFolder}{os.sep}{data_file_name}_final.csv"
os.makedirs(os.path.dirname(outFile), exist_ok=True)
with open(outFile, "w", newline ='') as f:
    writer = csv.writer(f)
    for row in rows:
        writer.writerow(row)

print("done")



