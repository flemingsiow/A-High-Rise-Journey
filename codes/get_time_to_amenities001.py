import pandas as pd
import requests
import json
import time
from datetime import date, datetime

# start clock
time_start = time.clock()

path = 'Random.csv'
path_mrt = 'MRT Stations Dataset v2.csv'
path_sm = 'Shopping Mall Dataset v2.csv'
email = 'flemingsiow@gmail.com'
password = 'MysticalSquirt03!'


# calling onemap rest api
credentials = {"email": email, "password": password}
req_url = f"https://developers.onemap.sg/privateapi/auth/post/getToken"
req = requests.post(req_url, data = credentials)

if req.status_code == 200:
    results = req.json() 
    token = results["access_token"]

# reading from datasets
df = pd.read_csv(path, parse_dates=['Resale Date'])
df_mrt = pd.read_csv(path_mrt, parse_dates=['Opening Date'])
df_sm = pd.read_csv(path_sm, parse_dates=['Opening Date'])


# iterate through every house
for index, row in df.iterrows():

    print(index)

    house_y = row['Latitude']
    house_x = row['Longitude']

    # query for SM time taken
    try:
        nearest_sm = row['Nearest SM Name']
        sm_y = df_sm.loc[df_sm['Shopping Mall Name'] == nearest_sm, 'Latitude'].iloc[0]
        sm_x = df_sm.loc[df_sm['Shopping Mall Name'] == nearest_sm, 'Longitude'].iloc[0]
        type_sm = 'walk'
        url_sm = f'''https://developers.onemap.sg/privateapi/routingsvc/route?start={house_y},{house_x}&end={sm_y},{sm_x}&routeType=walk&token={token}'''

        res_sm = requests.get(url_sm).json()
        df.loc[df.index[index], 'Time to SM'] = res_sm['route_summary']['total_time']

    except:
        df.loc[df.index[index], 'Time to SM'] = -1
        pass


    # query for MRT time taken
    try:
        nearest_mrt = row['Nearest MRT Name']
        mrt_y = df_mrt.loc[df_mrt['Station Address'] == nearest_mrt, 'Latitude'].iloc[0]
        mrt_x = df_mrt.loc[df_mrt['Station Address'] == nearest_mrt, 'Longitude'].iloc[0]
        type_mrt = 'walk'
        url_mrt = f'''https://developers.onemap.sg/privateapi/routingsvc/route?start={house_y},{house_x}&end={mrt_y},{mrt_x}&routeType=walk&token={token}'''
    
        res_mrt = requests.get(url_mrt).json()
        df.loc[df.index[index], 'Time to MRT'] = res_mrt['route_summary']['total_time']

    except:
        df.loc[df.index[index], 'Time to MRT'] = -1
        pass


    # query for CBD time taken
    try:
        type_cbd = 'pt'
        mode = 'TRANSIT'
        today = date.today() # get date
        now = datetime.now() # get time
        url_cbd = f'''https://developers.onemap.sg/privateapi/routingsvc/route?start={mrt_y},{mrt_x}&end=1.283881,103.851533&routeType={type_cbd}&token={token}&date={today.strftime("%Y-%m-%d")}&time={now.strftime("%H:%M:%S")}&mode={mode}'''

        res_cbd = requests.get(url_cbd).json()
        df.loc[df.index[index], 'Time to CBD'] = res_cbd['plan']['itineraries'][1]['duration']

    except:
        df.loc[df.index[index], 'Time to CBD'] = -1
        pass

    
    if index % 10000 == 0:
        df.to_csv(path, index=False, header=True)


df.to_csv(path, index=False, header=True)

# calculate computational time
time_end = time.clock()
hours, rem = divmod(time_end - time_start, 3600)
minutes, seconds = divmod(rem, 60)
print(f'''\n\nProcess Time:
            \r{int(hours):0>2}:{int(minutes):0>2}:{seconds:05.2f}''')