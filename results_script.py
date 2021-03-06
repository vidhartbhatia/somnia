# importing csv module 
import csv 
import datetime
import time
import statistics
import os
import pprint
import numpy as np
pp = pprint.PrettyPrinter()
pprint = pp.pprint
  
folder_name = "Test_var_agg"
file_name = "meds 5-12/51234"
ROW_LIMIT = None # set to none if want all
  
# initializing the titles and rows list 
# fields = [] 
rows = [] 

T = time.time()
# reading csv file 
with open(f"{folder_name}{os.sep}{file_name}_results.csv", 'r') as csvfile: 
    # creating a csv reader object 
    csvreader = csv.DictReader(csvfile)
      
    # # extracting field names through first row 
    fields = csvreader.fieldnames 

    rows = list(csvreader)[:ROW_LIMIT]
    if ROW_LIMIT!=None:
        rows = rows[:ROW_LIMIT]
    # get total number of rows 
    print(f"Total no. of rows: {len(rows)}")

print(rows[0]['predicted'][-1])

predicted = ['predicted']

for i in range(len(rows)):
    predicted.append(rows[i]['predicted'][-1])

rows = zip(predicted)

outFile = f"{folder_name}{os.sep}{file_name}_results.csv"
os.makedirs(os.path.dirname(outFile), exist_ok=True)
with open(outFile, "w", newline ='') as f:
    writer = csv.writer(f)
    for row in rows:
        writer.writerow(row)
  