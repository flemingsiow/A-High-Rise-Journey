import pandas as pd
from geopy.distance import geodesic # Documentation: https://pypi.org/project/geopy/
import time
import numpy as np

# start clock
time_start = time.perf_counter()

# extract data
path_house = '../datasets/Housing Resale Dataset/Housing Resale Dataset_002.csv'
path_mrt = '../datasets/MRT Station Dataset/MRT Stations Dataset_003.csv'
path_sm = '../datasets/Shopping Mall Dataset/Shopping Mall Dataset_003.csv'
df_house = pd.read_csv(path_house, parse_dates=['Resale Date'])
df_mrt = pd.read_csv(path_mrt, parse_dates=['Opening Date'])
df_sm = pd.read_csv(path_sm, parse_dates=['Opening Date'])


def get_distance(c1, c2):
    '''
        calculates distance between two coordinates
    '''
    return geodesic(c1, c2).km


def find_minimum(ls):
    '''
        Finds the minimum value in a list, excluding missing/filling values.
        In my case the filling value is 0 since I appended 0 in my except statement
    '''
    return np.ma.masked_equal(np.array(ls), 0, copy=False).min()


def main():
    global count
    global fno
    ''' 
        Retrieve Lat and Lngs of Buildings, MRTs and SMs from df.
        Then, use geopy's harvesine formula to calculate dist from building to mrt/sm and find minimum
        Lastly, append data into df and save as CSV File
    '''

    ''' --- Extracting and Formatting Data --- '''

    # get the coords of buildings, MRTs and SMs
    house_lat = list(df_house['Latitude'])
    house_lon = list(df_house['Longitude'])
    mrt_lat = list(df_mrt['Latitude'])
    mrt_lon = list(df_mrt['Longitude'])
    sm_lat = list(df_sm['Latitude'])
    sm_lon = list(df_sm['Longitude'])

    # zip lat and lng together (format it for geopy's pkg harvesine formula)
    house_coords, mrt_coords, sm_coords = [], [], []
    for lat, lon in zip(house_lat, house_lon):
        house_coords.append((lat, lon))

    for lat, lon in zip(mrt_lat, mrt_lon):
        mrt_coords.append((lat, lon))

    for lat, lon in zip(sm_lat, sm_lon):
        sm_coords.append((lat, lon))


    ''' --- Calculate Distance and Find Minimum Distance to Building --- '''

    # to store dist and min dist
    dist_mrt, min_dist_mrt = [], []
    dist_sm, min_dist_sm = [], []

    for i, org in enumerate(house_coords):

        # dist mrt    
        for d in range(len(mrt_coords)):

            try:
                dist1 = get_distance(org, mrt_coords[d])
                dist_mrt.append(dist1)
            
            except:
                dist_mrt.append(0)
                pass 

        # dist sm
        for d in range(len(sm_coords)):
            try:
                dist2 = get_distance(org, sm_coords[d])
                dist_sm.append(dist2)

            except:
                dist_sm.append(0)
                pass


        # find the minimum distance in the list
        try:
            nearest_mrt = find_minimum(dist_mrt)
        except:
            nearest_mrt = -1
        try:
            nearest_sm = find_minimum(dist_sm)
        except:
            nearest_sm = -1

        # append data to df
        df_house.loc[df_house.index[i], 'Nearest Dist (MRT)'] = nearest_mrt
        df_house.loc[df_house.index[i], 'Nearest Dist (SM)'] = nearest_sm


        ''' --- Retrieve Names of the Nearest MRT and SM --- '''

        # get name of mrt
        if nearest_mrt != -1:
            name_mrt = df_mrt['Station Address'][df_mrt['Latitude'] == mrt_coords[dist_mrt.index(nearest_mrt)][0]].iloc[0]
            df_house.loc[df_house.index[i], 'Nearest MRT Name'] = name_mrt
        else:
            df_house.loc[df_house.index[i], 'Nearest MRT Name'] = -1

        # get name of sm
        if nearest_sm != -1:
            name_sm = df_sm['Shopping Mall Name'][df_sm['Latitude'] == sm_coords[dist_sm.index(nearest_sm)][0]].iloc[0]
            df_house.loc[df_house.index[i], 'Nearest SM Name'] = name_sm
        else:
            df_house.loc[df_house.index[i], 'Nearest SM Name'] = -1


        # remember to remove the mrt and sm coords from the list for the next building to check against
        del dist_mrt[:]
        del dist_sm[:]


        # log each row
        print(f"Row {i + 1}: {name_mrt}{nearest_mrt:.2f} {name_sm}{nearest_sm:.2f}")


        # since dataset is large, for every 20k records, create a new csv file to store it
        count += 1
        if count >= 20000:
            # NOTE: Previous dataset is labelled as _002 and _003 are the new ones, to be merged after finished
            final_file = f'../datasets/Housing Resale Dataset/Housing Resale Dataset_003_{fno}.csv'
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