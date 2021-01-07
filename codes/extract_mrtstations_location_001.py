import pandas as pd
import requests
import json
import time

# start clock
time_start = time.perf_counter()

# extract data
filename = '../datasets/MRT Station Dataset/MRT Stations Dataset_002.csv'
df = pd.read_csv(filename, parse_dates=['Opening Date'])


def main():
    '''
        Retrieve station code and address of each MRT and combine them as an MRT address.
        Then use OneMap API to find the Lats and Lngs of the MRT addresses.
        Lastly, append data into df and save as CSV File
    '''
    for i, row in df.iterrows():
        stn_code = row['Station Code']
        stn_addr = f"{row['Station Address']} ({stn_code})"

        # query
        url = f'https://developers.onemap.sg/commonapi/search?searchVal={str(stn_addr)}&returnGeom=Y&getAddrDetails=Y&pageNum=1'


        try:

            # convert to json for extraction
            response = requests.get(url).json()

            # store data into pandas dataframe
            ###df.loc[df.index[i], 'SearchVal'] = response['results'][0]['SEARCHVAL']
            ###df.loc[df.index[i], 'Road Name'] = response['results'][0]['ROAD_NAME']
            ###df.loc[df.index[i], 'Building'] = response['results'][0]['BUILDING']
            ###df.loc[df.index[i], 'Address'] = response['results'][0]['ADDRESS']
            df.loc[df.index[i], 'Postal'] = response['results'][0]['POSTAL']
            df.loc[df.index[i], 'Latitude'] = response['results'][0]['LATITUDE']
            df.loc[df.index[i], 'Longitude'] = response['results'][0]['LONGITUDE']

        except:
            # NOTE: Dataset contains future MRT Stations as well which will result in an error since it doesn't exist yet
            print(f'Row {i + 1}: Error Occurred.')
            pass

        else:
            print(f"Row {i + 1}: LAT{response['results'][0]['LATITUDE'][:6]} LNG{response['results'][0]['LONGITUDE'][:6]}")


    # save to csv file
    final_file = f'../datasets/MRT Station Dataset/MRT Stations Dataset_003.csv'
    df.to_csv(final_file, index=False, header=True)


if __name__ == "__main__":
    main()


# calculate computational time
time_end = time.perf_counter()
hours, rem = divmod(time_end - time_start, 3600)
minutes, seconds = divmod(rem, 60)
print(f'''\n\nProcess Time:
            \r{int(hours):0>2}:{int(minutes):0>2}:{seconds:05.2f}''')


