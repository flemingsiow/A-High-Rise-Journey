import pandas as pd
import requests
import json
import time

# start clock
time_start = time.perf_counter()

# extract data
filename = '../datasets/Shopping Mall Dataset/Shopping Mall Dataset_002.csv'
df = pd.read_csv(filename, parse_dates=['Opening Date'])


def main():
    '''
        Retrieve name of shopping malls from df.
        Then use OneMap API to find the Lats and Lngs of the SM.
        Lastly, append data into df and save as CSV File
    '''
    for i, row in df.iterrows():
        sm_name = row['Shopping Mall Name']

        # query
        url = f'https://developers.onemap.sg/commonapi/search?searchVal={str(sm_name)}&returnGeom=Y&getAddrDetails=Y&pageNum=1'


        try:

            # convert to json for extraction
            response = requests.get(url).json()

            # store data into pandas dataframe
            ###df.loc[df.index[i], 'SearchVal'] = response['results'][0]['SEARCHVAL']
            ###df.loc[df.index[i], 'Address'] = response['results'][0]['ADDRESS']
            df.loc[df.index[i], 'Postal'] = response['results'][0]['POSTAL']
            df.loc[df.index[i], 'Latitude'] = response['results'][0]['LATITUDE']
            df.loc[df.index[i], 'Longitude'] = response['results'][0]['LONGITUDE']

        except:

            print(f'Row {i + 1}: Error Occurred.')
            pass

        else:
            print(f"Row {i + 1}: LAT{response['results'][0]['LATITUDE'][:6]} LNG{response['results'][0]['LONGITUDE'][:6]}")


    # save to csv file
    final_file = f'../datasets/Shopping Mall Dataset/Shopping Mall Dataset_003.csv'
    df.to_csv(final_file, index=False, header=True)


if __name__ == "__main__":
    main()


# calculate computational time
time_end = time.perf_counter()
hours, rem = divmod(time_end - time_start, 3600)
minutes, seconds = divmod(rem, 60)
print(f'''\n\nProcess Time:
            \r{int(hours):0>2}:{int(minutes):0>2}:{seconds:05.2f}''')