import pandas as pd
import requests
import json
import time

# start clock
time_start = time.clock()

path = 'Housing Resale Dataset.csv'
df = pd.read_csv(path, parse_dates=['Resale Date'])
#df = pd.read_csv(path, parse_dates=['month', 'lease_commence_date'])

for index, row in df.iterrows():

    addr = row['Full Address']
    #addr = row['town']

    # query
    url = f'https://developers.onemap.sg/commonapi/search?searchVal={str(addr)}&returnGeom=Y&getAddrDetails=Y&pageNum=1'


    try:

        # convert to json for extraction
        response = requests.get(url).json()

        # store data into pandas dataframe
        #df.loc[df.index[index], 'SearchVal'] = response['results'][0]['SEARCHVAL']
        #df.loc[df.index[index], 'Road Name'] = response['results'][0]['ROAD_NAME']
        #df.loc[df.index[index], 'Building'] = response['results'][0]['BUILDING']
        #df.loc[df.index[index], 'Address'] = response['results'][0]['ADDRESS']
        df.loc[df.index[index], 'Postal'] = response['results'][0]['POSTAL']
        df.loc[df.index[index], 'Latitude'] = response['results'][0]['LATITUDE']
        df.loc[df.index[index], 'Longitude'] = response['results'][0]['LONGITUDE']

    except:
        
        df.loc[df.index[index], 'SearchVal'] = -1
        print('Error Occurred.')
        pass

    else:
        print(f'Row {index + 1} Created')


'''
try:
    save_name = f"{path.split('/')[-1][:-4]} v2.csv"
except:
    save_name = "finished.csv"
'''

df.to_csv(path, index=False, header=True)

# calculate computational time
time_end = time.clock()
hours, rem = divmod(time_end - time_start, 3600)
minutes, seconds = divmod(rem, 60)
print(f'''\n\nProcess Time:
            \r{int(hours):0>2}:{int(minutes):0>2}:{seconds:05.2f}''')