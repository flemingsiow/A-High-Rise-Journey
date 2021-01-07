import pandas as pd
import requests
import json
import time
from datetime import date, datetime

# start clock
time_start = time.perf_counter()

# extract data
path_house = '../datasets/Housing Resale Dataset/Housing Resale Dataset_003.csv'
path_mrt = '../datasets/MRT Station Dataset/MRT Stations Dataset_003.csv'
path_sm = '../datasets/Shopping Mall Dataset/Shopping Mall Dataset_003.csv'
df_house = pd.read_csv(path_house, parse_dates=['Resale Date'])
df_mrt = pd.read_csv(path_mrt, parse_dates=['Opening Date'])
df_sm = pd.read_csv(path_sm, parse_dates=['Opening Date'])


# request apikey
'''
    NOTE: You may register for an account Here: https://developers.onemap.sg/signup/
'''
email = 'ENTER_YOUR_EMAIL_HERE'
password = 'ENTER_YOUR_PASSWORD_HERE'
credentials = { "email": email, "password": password }

req_url = f"https://developers.onemap.sg/privateapi/auth/post/getToken"
req = requests.post(req_url, data = credentials)

if req.status_code == 200:
    results = req.json() 
    token = results["access_token"]


def calc_time_between_points(x1, y1, x2, y2, m, t):
    '''
        calculates the time needed to travel between two sets of geopoints, with mode of transportation specified
    '''

    url = f'https://developers.onemap.sg/privateapi/routingsvc/route?start={y1},{x1}&end={y2},{x2}&routeType={m}&token={t}'

    return requests.get(url).json()


def calc_time_to_CBD(x, y, t, today, now):
    '''
        calculates time taken to travel from one mrt location to raffles place mrt station (CBD)
    '''

    url = f'https://developers.onemap.sg/privateapi/routingsvc/route?start={y},{x}&end=1.283881,103.851533' + \
          f'&routeType=pt&token={t}&date={today.strftime("%Y-%m-%d")}&time={now.strftime("%H:%M:%S")}&mode=TRANSIT'

    return requests.get(url).json()


def main():
    global count
    global fno
    '''
        Retrieve Lat and Lngs of Buildings, MRTs and SMs from df.
        Then, call OneMap API to find the time taken to walk to nearest MRT and SM, and also to CBD through transit
        Lastly, append data into df and save as CSV File
    '''

    # iterate through every house
    for i, row in df_house.iterrows():

        # retrieve Lats and Lngs of Building
        house_y = row['Latitude']
        house_x = row['Longitude']


        # query for SM time taken
        try:
            ## retrieve Lats and Lngs of SM
            nearest_sm = row['Nearest SM Name']
            sm_y = df_sm.loc[df_sm['Shopping Mall Name'] == nearest_sm, 'Latitude'].iloc[0]
            sm_x = df_sm.loc[df_sm['Shopping Mall Name'] == nearest_sm, 'Longitude'].iloc[0]

            ## calc time
            res_sm = calc_time_between_points(house_x, house_y, sm_x, sm_y, 'walk', token)

            ## append to df
            tt_sm = res_sm['route_summary']['total_time']
            df_house.loc[df_house.index[i], 'Time to SM'] = tt_sm

        except:
            tt_sm = -1
            df_house.loc[df_house.index[i], 'Time to SM'] = -1
            pass




        # query for MRT time taken
        try:
            ## retrieve Lats and Lngs of MRT
            nearest_mrt = row['Nearest MRT Name']
            mrt_y = df_mrt.loc[df_mrt['Station Address'] == nearest_mrt, 'Latitude'].iloc[0]
            mrt_x = df_mrt.loc[df_mrt['Station Address'] == nearest_mrt, 'Longitude'].iloc[0]

            ## calc time
            res_mrt = calc_time_between_points(house_x, house_y, mrt_x, mrt_y, 'walk', token)

            ## append to df
            tt_mrt = res_mrt['route_summary']['total_time']
            df_house.loc[df_house.index[i], 'Time to MRT'] = tt_mrt

        except:
            tt_mrt = -1
            df_house.loc[df_house.index[i], 'Time to MRT'] = -1
            pass




        # query for CBD time taken
        try:
            ## get current date and time
            today = date.today()
            now = datetime.now()

            ## calc time
            res_cbd = calc_time_to_CBD(mrt_x, mrt_y, token, today, now)

            ## append to df
            tt_cbd = res_cbd['plan']['itineraries'][1]['duration']
            df_house.loc[df_house.index[i], 'Time to CBD'] = tt_cbd

        except:
            tt_cbd = -1
            df_house.loc[df_house.index[i], 'Time to CBD'] = -1
            pass

        


        # log each row
        print(f"Row {i + 1}: MRT{tt_mrt:.2f} SM{tt_sm:.2f} CBD{tt_cbd:.2f}")


        # since dataset is large, for every 20k records, create a new csv file to store it
        count += 1
        if count >= 20000:
            # NOTE: Previous dataset is labelled as _003 and _004 are the new ones, to be merged after finished
            final_file = f'../datasets/Housing Resale Dataset/Housing Resale Dataset_004_{fno}.csv'
            df_house.to_csv(final_file, index=False, header=True)

            count = 0 # reset count
            fno += 1  # next file num


if __name__ == "__main__":
    count, fno = 0, 2
    main()


# calculate computational time
time_end = time.perf_counter()
hours, rem = divmod(time_end - time_start, 3600)
minutes, seconds = divmod(rem, 60)
print(f'''\n\nProcess Time:
            \r{int(hours):0>2}:{int(minutes):0>2}:{seconds:05.2f}''')