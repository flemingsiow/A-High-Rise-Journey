import pandas as pd
import requests
import json
import time

# start clock
time_start = time.perf_counter()

path = '../datasets/Housing Resale Dataset/Housing Resale Dataset_001.csv'
df = pd.read_csv(path, parse_dates=['Resale Date'])
#df = pd.read_csv(path, parse_dates=['month', 'lease_commence_date'])

def main():
    global count
    global fno
    '''
        retreives addresses from csv file. extracts their lat and lng from onemap API and append it to pd dataframe.
    '''
    for i, row in df.iterrows():

        addr = row['Address']
        #addr = row['town']

        # query
        url = f'https://developers.onemap.sg/commonapi/search?searchVal={str(addr)}&returnGeom=Y&getAddrDetails=Y&pageNum=1'


        try:

            # convert to json for extraction
            response = requests.get(url).json()

            # store data into pandas dataframe
            #df.loc[df.index[i], 'SearchVal'] = response['results'][0]['SEARCHVAL']
            #df.loc[df.index[i], 'Road Name'] = response['results'][0]['ROAD_NAME']
            #df.loc[df.index[i], 'Building'] = response['results'][0]['BUILDING']
            #df.loc[df.index[i], 'Address'] = response['results'][0]['ADDRESS']
            df.loc[df.index[i], 'Postal'] = response['results'][0]['POSTAL']
            df.loc[df.index[i], 'Latitude'] = response['results'][0]['LATITUDE']
            df.loc[df.index[i], 'Longitude'] = response['results'][0]['LONGITUDE']

        except:
            
            print(f'Row {i + 1}: Error Occurred.')
            pass

        else:
            print(f"Row {i + 1}: LAT{response['results'][0]['LATITUDE'][:6]} LNG{response['results'][0]['LONGITUDE'][:6]}")


        # since dataset is large, for every 20k records, create a new csv file to store it
        count += 1
        if count >= 20000:
            # NOTE: Original dataset is labelled with _001 and _002 are the new ones, to be merged after finished
            final_file = f'../datasets/Housing Resale Dataset/Housing Resale Dataset_002_{fno}.csv'
            df.to_csv(final_file, index=False, header=True)

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