# importing csv module 
import csv 
import datetime
import statistics
  
# csv file name 
filename = "50658"
  
# initializing the titles and rows list 
fields = [] 
rows = [] 
  
# reading csv file 
with open("Data/vids 5-6/" + filename + ".csv", 'r') as csvfile: 
    # creating a csv reader object 
    csvreader = csv.reader(csvfile) 
      
    # extracting field names through first row 
    fields = next(csvreader) 
  
    # extracting each data row one by one 
    for row in csvreader: 
        rows.append(row) 
  
    # get total number of rows 
    print("Total no. of rows: %d"%(csvreader.line_num)) 
  
# printing the field names 
# print('Field names are:' + ', '.join(field for field in fields)) 
  
# start_time_str = "4/20/2020  5:21 AM"
# start_time = datetime.datetime.strptime(start_time_str, '%m/%d/%Y  %I:%M %p')
start_time = datetime.datetime.fromtimestamp(int(1588755530618)/1000)

print('Start time:', start_time)

sampling_rate = 10
num_minutes = len(rows) // int((sampling_rate * 60))
print(num_minutes)

minutes = ['minutes']
curr_time = start_time
for i in range(num_minutes):
    minutes.append(curr_time.strftime('%I:%M %p'))
    curr_time += datetime.timedelta(seconds=60)

accXs1 = [[] for i in range(num_minutes-1)]
accYs1 = [[] for i in range(num_minutes-1)]
accZs1 = [[] for i in range(num_minutes-1)]
gyroXs1 = [[] for i in range(num_minutes-1)]
gyroYs1 = [[] for i in range(num_minutes-1)]
gyroZs1 = [[] for i in range(num_minutes-1)]
gravXs1 = [[] for i in range(num_minutes-1)]
gravYs1 = [[] for i in range(num_minutes-1)]
gravZs1 = [[] for i in range(num_minutes-1)]
magXs1 = [[] for i in range(num_minutes-1)]
magYs1 = [[] for i in range(num_minutes-1)]
magZs1 = [[] for i in range(num_minutes-1)]

accXs5 = [[] for i in range(num_minutes-1)]
accYs5 = [[] for i in range(num_minutes-1)]
accZs5 = [[] for i in range(num_minutes-1)]
gyroXs5 = [[] for i in range(num_minutes-1)]
gyroYs5 = [[] for i in range(num_minutes-1)]
gyroZs5 = [[] for i in range(num_minutes-1)]
gravXs5 = [[] for i in range(num_minutes-1)]
gravYs5 = [[] for i in range(num_minutes-1)]
gravZs5 = [[] for i in range(num_minutes-1)]
magXs5 = [[] for i in range(num_minutes-1)]
magYs5 = [[] for i in range(num_minutes-1)]
magZs5 = [[] for i in range(num_minutes-1)]

accXs10 = [[] for i in range(num_minutes-1)]
accYs10 = [[] for i in range(num_minutes-1)]
accZs10 = [[] for i in range(num_minutes-1)]
gyroXs10 = [[] for i in range(num_minutes-1)]
gyroYs10 = [[] for i in range(num_minutes-1)]
gyroZs10 = [[] for i in range(num_minutes-1)]
gravXs10 = [[] for i in range(num_minutes-1)]
gravYs10 = [[] for i in range(num_minutes-1)]
gravZs10 = [[] for i in range(num_minutes-1)]
magXs10 = [[] for i in range(num_minutes-1)]
magYs10 = [[] for i in range(num_minutes-1)]
magZs10 = [[] for i in range(num_minutes-1)]

accXs20 = [[] for i in range(num_minutes-1)]
accYs20 = [[] for i in range(num_minutes-1)]
accZs20 = [[] for i in range(num_minutes-1)]
gyroXs20 = [[] for i in range(num_minutes-1)]
gyroYs20 = [[] for i in range(num_minutes-1)]
gyroZs20 = [[] for i in range(num_minutes-1)]
gravXs20 = [[] for i in range(num_minutes-1)]
gravYs20 = [[] for i in range(num_minutes-1)]
gravZs20 = [[] for i in range(num_minutes-1)]
magXs20 = [[] for i in range(num_minutes-1)]
magYs20 = [[] for i in range(num_minutes-1)]
magZs20 = [[] for i in range(num_minutes-1)]

accXs30 = [[] for i in range(num_minutes-1)]
accYs30 = [[] for i in range(num_minutes-1)]
accZs30 = [[] for i in range(num_minutes-1)]
gyroXs30 = [[] for i in range(num_minutes-1)]
gyroYs30 = [[] for i in range(num_minutes-1)]
gyroZs30 = [[] for i in range(num_minutes-1)]
gravXs30 = [[] for i in range(num_minutes-1)]
gravYs30 = [[] for i in range(num_minutes-1)]
gravZs30 = [[] for i in range(num_minutes-1)]
magXs30 = [[] for i in range(num_minutes-1)]
magYs30 = [[] for i in range(num_minutes-1)]
magZs30 = [[] for i in range(num_minutes-1)]

points_per_min = sampling_rate * 60

for j in range(1, num_minutes):
    # don't judge for this i am sleepy
    # 1
    for i in range(max(0, (j-1) * points_per_min), j * points_per_min):
        accXs1[j-1].append(float(rows[i][2]))
        accYs1[j-1].append(float(rows[i][3]))
        accZs1[j-1].append(float(rows[i][4]))
        gyroXs1[j-1].append(float(rows[i][5]))
        gyroYs1[j-1].append(float(rows[i][6]))
        gyroZs1[j-1].append(float(rows[i][7]))
        gravXs1[j-1].append(float(rows[i][8]))
        gravYs1[j-1].append(float(rows[i][9]))
        gravZs1[j-1].append(float(rows[i][10]))
        magXs1[j-1].append(float(rows[i][11]))
        magYs1[j-1].append(float(rows[i][12]))
        magZs1[j-1].append(float(rows[i][13]))

    # 5
    for i in range(max(0, (j-5) * points_per_min), j * points_per_min):
        accXs5[j-1].append(float(rows[i][2]))
        accYs5[j-1].append(float(rows[i][3]))
        accZs5[j-1].append(float(rows[i][4]))
        gyroXs5[j-1].append(float(rows[i][5]))
        gyroYs5[j-1].append(float(rows[i][6]))
        gyroZs5[j-1].append(float(rows[i][7]))
        gravXs5[j-1].append(float(rows[i][8]))
        gravYs5[j-1].append(float(rows[i][9]))
        gravZs5[j-1].append(float(rows[i][10]))
        magXs5[j-1].append(float(rows[i][11]))
        magYs5[j-1].append(float(rows[i][12]))
        magZs5[j-1].append(float(rows[i][13]))

    # 10
    for i in range(max(0, (j-10) * points_per_min), j * points_per_min):
        accXs10[j-1].append(float(rows[i][2]))
        accYs10[j-1].append(float(rows[i][3]))
        accZs10[j-1].append(float(rows[i][4]))
        gyroXs10[j-1].append(float(rows[i][5]))
        gyroYs10[j-1].append(float(rows[i][6]))
        gyroZs10[j-1].append(float(rows[i][7]))
        gravXs10[j-1].append(float(rows[i][8]))
        gravYs10[j-1].append(float(rows[i][9]))
        gravZs10[j-1].append(float(rows[i][10]))
        magXs10[j-1].append(float(rows[i][11]))
        magYs10[j-1].append(float(rows[i][12]))
        magZs10[j-1].append(float(rows[i][13]))

     # 20
    for i in range(max(0, (j-20) * points_per_min), j * points_per_min):
        accXs20[j-1].append(float(rows[i][2]))
        accYs20[j-1].append(float(rows[i][3]))
        accZs20[j-1].append(float(rows[i][4]))
        gyroXs20[j-1].append(float(rows[i][5]))
        gyroYs20[j-1].append(float(rows[i][6]))
        gyroZs20[j-1].append(float(rows[i][7]))
        gravXs20[j-1].append(float(rows[i][8]))
        gravYs20[j-1].append(float(rows[i][9]))
        gravZs20[j-1].append(float(rows[i][10]))
        magXs20[j-1].append(float(rows[i][11]))
        magYs20[j-1].append(float(rows[i][12]))
        magZs20[j-1].append(float(rows[i][13]))

     # 30
    for i in range(max(0, (j-30) * points_per_min), j * points_per_min):
        accXs30[j-1].append(float(rows[i][2]))
        accYs30[j-1].append(float(rows[i][3]))
        accZs30[j-1].append(float(rows[i][4]))
        gyroXs30[j-1].append(float(rows[i][5]))
        gyroYs30[j-1].append(float(rows[i][6]))
        gyroZs30[j-1].append(float(rows[i][7]))
        gravXs30[j-1].append(float(rows[i][8]))
        gravYs30[j-1].append(float(rows[i][9]))
        gravZs30[j-1].append(float(rows[i][10]))
        magXs30[j-1].append(float(rows[i][11]))
        magYs30[j-1].append(float(rows[i][12]))
        magZs30[j-1].append(float(rows[i][13]))

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
# gyroX_means = ['gyroX_means'] + [statistics.mean(x) for x in gyroXs]
# gyroY_means = ['gyroY_means'] + [statistics.mean(x) for x in gyroYs]
# gyroZ_means = ['gyroZ_means'] + [statistics.mean(x) for x in gyroZs]
# gravX_means = ['gravX_means'] + [statistics.mean(x) for x in gravXs]
# gravY_means = ['gravY_means'] + [statistics.mean(x) for x in gravYs]
# gravZ_means = ['gravZ_means'] + [statistics.mean(x) for x in gravZs]
# magX_means = ['magX_means'] + [statistics.mean(x) for x in magXs]
# magY_means = ['magY_means'] + [statistics.mean(x) for x in magYs]
# magZ_means = ['magZ_means'] + [statistics.mean(x) for x in magZs]

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
# gyroX_medians = ['gyroX_medians'] + [statistics.median(x) for x in gyroXs]
# gyroY_medians = ['gyroY_medians'] + [statistics.median(x) for x in gyroYs]
# gyroZ_medians = ['gyroZ_medians'] + [statistics.median(x) for x in gyroZs]
# gravX_medians = ['gravX_medians'] + [statistics.median(x) for x in gravXs]
# gravY_medians = ['gravY_medians'] + [statistics.median(x) for x in gravYs]
# gravZ_medians = ['gravZ_medians'] + [statistics.median(x) for x in gravZs]
# magX_medians = ['magX_medians'] + [statistics.median(x) for x in magXs]
# magY_medians = ['magY_medians'] + [statistics.median(x) for x in magYs]
# magZ_medians = ['magZ_medians'] + [statistics.median(x) for x in magZs]

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
# gyroX_maxes = ['gyroX_maxes'] + [max(x) for x in gyroXs]
# gyroY_maxes = ['gyroY_maxes'] + [max(x) for x in gyroYs]
# gyroZ_maxes = ['gyroZ_maxes'] + [max(x) for x in gyroZs]
# gravX_maxes = ['gravX_maxes'] + [max(x) for x in gravXs]
# gravY_maxes = ['gravY_maxes'] + [max(x) for x in gravYs]
# gravZ_maxes = ['gravZ_maxes'] + [max(x) for x in gravZs]
# magX_maxes = ['magX_maxes'] + [max(x) for x in magXs]
# magY_maxes = ['magY_maxes'] + [max(x) for x in magYs]
# magZ_maxes = ['magZ_maxes'] + [max(x) for x in magZs]

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
# gyroX_mins = ['gyroX_mins'] + [min(x) for x in gyroXs]
# gyroY_mins = ['gyroY_mins'] + [min(x) for x in gyroYs]
# gyroZ_mins = ['gyroZ_mins'] + [min(x) for x in gyroZs]
# gravX_mins = ['gravX_mins'] + [min(x) for x in gravXs]
# gravY_mins = ['gravY_mins'] + [min(x) for x in gravYs]
# gravZ_mins = ['gravZ_mins'] + [min(x) for x in gravZs]
# magX_mins = ['magX_mins'] + [min(x) for x in magXs]
# magY_mins = ['magY_mins'] + [min(x) for x in magYs]
# magZ_mins = ['magZ_mins'] + [min(x) for x in magZs]

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
# gyroX_variances = ['gyroX_variances'] + [statistics.variance(x) for x in gyroXs]
# gyroY_variances = ['gyroY_variances'] + [statistics.variance(x) for x in gyroYs]
# gyroZ_variances = ['gyroZ_variances'] + [statistics.variance(x) for x in gyroZs]
# gravX_variances = ['gravX_variances'] + [statistics.variance(x) for x in gravXs]
# gravY_variances = ['gravY_variances'] + [statistics.variance(x) for x in gravYs]
# gravZ_variances = ['gravZ_variances'] + [statistics.variance(x) for x in gravZs]
# magX_variances = ['magX_variances'] + [statistics.variance(x) for x in magXs]
# magY_variances = ['magY_variances'] + [statistics.variance(x) for x in magYs]
# magZ_variances = ['magZ_variances'] + [statistics.variance(x) for x in magZs]

tags = ['tags'] + ['' for i in range(num_minutes)]

# print(len(tags))

# rows = zip(minutes, tags, accX_means, accY_means, accZ_means, gyroX_means, gyroY_means, gyroZ_means, gravX_means, gravY_means, gravZ_means, \
# magX_means, magY_means, magZ_means, accX_medians, accY_medians, accZ_medians, gyroX_medians, gyroY_medians, gyroZ_medians, gravX_medians, \
# gravY_medians, gravZ_medians, magX_medians, magY_medians, magZ_medians, accX_maxes, accY_maxes, accZ_maxes, gyroX_maxes, gyroY_maxes, \
# gyroZ_maxes, gravX_maxes, gravY_maxes, gravZ_maxes, magX_maxes, magY_maxes, magZ_maxes, accX_mins, accY_mins, accZ_mins, gyroX_mins, \
# gyroY_mins, gyroZ_mins, gravX_mins, gravY_mins, gravZ_mins, magX_mins, magY_mins, magZ_mins, accX_variances, accY_variances, accZ_variances, \
# gyroX_variances, gyroY_variances, gyroZ_variances, gravX_variances, gravY_variances, gravZ_variances, magX_variances, magY_variances, \
# magZ_variances)

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

with open("Tagging/" + filename + "_final.csv", "w", newline ='') as f:
    writer = csv.writer(f)
    for row in rows:
        writer.writerow(row)

print("done")



