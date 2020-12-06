import pandas as pd
from geopy.distance import geodesic # Documentation: https://pypi.org/project/geopy/
import time
import numpy as np

# start clock
time_start = time.clock()

path_house = 'Housing Resale Dataset.csv'
path_mrt = 'MRT Stations Dataset.csv'
path_sm = 'Shopping Mall Dataset.csv'
df_house = pd.read_csv(path_house, parse_dates=['Resale Date'])
df_mrt = pd.read_csv(path_mrt, parse_dates=['Opening Date'])
df_sm = pd.read_csv(path_sm, parse_dates=['Opening Date'])

# get the coords
house_lat = list(df_house['Latitude'])
house_lon = list(df_house['Longitude'])
mrt_lat = list(df_mrt['Latitude'])
mrt_lon = list(df_mrt['Longitude'])
sm_lat = list(df_sm['Latitude'])
sm_lon = list(df_sm['Longitude'])
house_coords, mrt_coords, sm_coords = [], [], []

## zipping lat and long together as a list of tuples
for lat, lon in zip(house_lat, house_lon):
    house_coords.append((lat, lon))

for lat, lon in zip(mrt_lat, mrt_lon):
    mrt_coords.append((lat, lon))

for lat, lon in zip(sm_lat, sm_lon):
    sm_coords.append((lat, lon))


## using geopy's harvesine formula to calculate the distance
dist_mrt, min_dist_mrt = [], []
dist_sm, min_dist_sm = [], []

for idx, org in enumerate(house_coords):

    print(idx)

    # mrt    
    for d in range(len(mrt_coords)):

        try:

            dist1 = geodesic(org, mrt_coords[d]).km
            dist_mrt.append(dist1)
        
        except:
            dist_mrt.append(0)
            pass 

    # sm
    for d in range(len(sm_coords)):

        try:
            dist2 = geodesic(org, sm_coords[d]).km
            dist_sm.append(dist2)

        except:
            dist_sm.append(0)
            pass


    try:
        nearest_mrt = np.ma.masked_equal(np.array(dist_mrt), 0, copy=False).min()
    except:
        nearest_mrt = -1
    try:
        nearest_sm = np.ma.masked_equal(np.array(dist_sm), 0, copy=False).min()
    except:
        nearest_sm = -1


    df_house.loc[df_house.index[idx], 'Nearest Dist (MRT)'] = nearest_mrt
    df_house.loc[df_house.index[idx], 'Nearest Dist (SM)'] = nearest_sm

    # get name of mrt
    if nearest_mrt != -1:
        name_mrt = df_mrt['Station Address'][df_mrt['Latitude'] == mrt_coords[dist_mrt.index(nearest_mrt)][0]].iloc[0]
        df_house.loc[df_house.index[idx], 'Nearest MRT Name'] = name_mrt
    else:
        df_house.loc[df_house.index[idx], 'Nearest MRT Name'] = -1

    # get name of sm
    if nearest_sm != -1:
        name_sm = df_sm['Shopping Mall Name'][df_sm['Latitude'] == sm_coords[dist_sm.index(nearest_sm)][0]].iloc[0]
        df_house.loc[df_house.index[idx], 'Nearest SM Name'] = name_sm
    else:
        df_house.loc[df_house.index[idx], 'Nearest SM Name'] = -1

    del dist_mrt[:]
    del dist_sm[:]

df_house.to_csv(path_house, index=False, header=True)

# calcualte computational time
time_end = time.clock()
hours, rem = divmod(time_end - time_start, 3600)
minutes, seconds = divmod(rem, 60)
print(f'''\n\nProcess Time:
            \r{int(hours):0>2}:{int(minutes):0>2}:{seconds:05.2f}''')