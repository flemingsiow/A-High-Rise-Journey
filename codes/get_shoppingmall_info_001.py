from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait     
from selenium.webdriver.common.by import By     
from selenium.webdriver.support import expected_conditions as EC
import re
import numpy as np
import pandas as pd

# drivers
driver = webdriver.Chrome('/Drivers/Chrome/chromedriver') # NOTE: Change to the directory wherever you installed your driver

# retrieve website
driver.get('https://en.wikipedia.org/wiki/List_of_shopping_malls_in_Singapore')


def dms2dd(dms):
    '''
        convert dms coordinates to dd
    '''
    deg, mins, secs, direction = re.split('[°′″]+', dms) # dms = """1°51′56.29"N"""
    dd = float(deg) + float(mins) / 60 + float(secs) / (60*60)

    # check direction
    if direction in ('S', 'W'):
        dd *= -1

    return dd

def format_dd(dd):
    '''
        remove the unnecessary ° and directions (N, W, S, E) from dd coords
    '''
    return dd.translate(str.maketrans({'°': None, 'N': None, 'E': None, 'S': None, 'W': None}))


def main():
    '''

    '''
    # retrieve all the lists of shopping mall from wikipedia
    shopping_malls = WebDriverWait(driver, 20).until(EC.visibility_of_all_elements_located(\
                    (By.XPATH, '//div[@class="div-col columns column-width"]/ul/li/a')))

    # retrieve the respective links for each SM so can get more details on the SM
    links = [s.get_attribute('href') for s in shopping_malls]




    # create the dataframe to store the data
    sm_list = []
    for s in range(len(shopping_malls)):
        sm_list.append(shopping_malls[s].text)

    columns = ['Shopping Mall Name', 'Location', 'Address', 'Latitude', 'Longitude', 'Opening Date',
            'Developer', 'Management', 'Owner', 'Number of Stores', 'Number of Floors', 
            'Floor Area', 'Transit Access', 'Website']
    df = pd.DataFrame(columns=columns, index=np.arange(len(sm_list)))

    # get details of each SM
    for i, link in enumerate(links):
        driver.get(link) ## retrieve website of each link

        location = driver.find_elements_by_xpath("//tr[th/text()='Location']/td")
        address = driver.find_elements_by_xpath("//tr[th/text()='Address']/td")
        coordinates = driver.find_elements_by_xpath("//tr[th/a[@title='Geographic coordinate system']]/td//span[@class='geo-default']/span")
        opening_date = driver.find_elements_by_xpath("//tr[th/text()='Opening date']/td")
        developer = driver.find_elements_by_xpath("//tr[th/text()='Developer']/td")
        management = driver.find_elements_by_xpath("//tr[th/text()='Management']/td")
        owner = driver.find_elements_by_xpath("//tr[th/text()='Owner']/td")
        num_of_stores = driver.find_elements_by_xpath("//tr[th/text()='No. of stores and services']/td")
        num_of_floors = driver.find_elements_by_xpath("//tr[th/text()='No. of floors']/td")
        floor_area = driver.find_elements_by_xpath("//tr[th/text()='Total retail floor area']/td")
        transit_access = driver.find_elements_by_xpath("//tr[th/text()='Public transit access']/td")
        website = driver.find_elements_by_xpath("//tr[th/text()='Website']/td")

        try:
            # convert coords to latitude and longitude
            lat, lng = 0, 0
            if coordinates:
                coord = coordinates[0].text
                lat, lng = str(coord).split(' ')

                if any(dms_str in coord for dms_str in ['″', '′']):
                    lat = dms2dd(lat)
                    lng = dms2dd(lng)
                else:
                    lat = format_dd(lat)
                    lng = format_dd(lng)

            
            df.loc[df.index[i], 'Shopping Mall Name'] = sm_list[i]
            df.loc[df.index[i], 'Location'] = location[0].text if location else None
            df.loc[df.index[i], 'Address'] = address[0].text if address else None
            df.loc[df.index[i], 'Latitude'] = lat if lat else None
            df.loc[df.index[i], 'Longitude'] = lng if lng else None
            df.loc[df.index[i], 'Opening Date'] = opening_date[0].text if opening_date else None
            df.loc[df.index[i], 'Developer'] = developer[0].text if developer else None
            df.loc[df.index[i], 'Management'] = management[0].text if management else None
            df.loc[df.index[i], 'Owner'] = owner[0].text if owner else None
            df.loc[df.index[i], 'Number of Stores'] = num_of_stores[0].text if num_of_stores else None
            df.loc[df.index[i], 'Number of Floors'] = num_of_floors[0].text if num_of_floors else None
            df.loc[df.index[i], 'Floor Area'] = floor_area[0].text if floor_area else None
            df.loc[df.index[i], 'Transit Access'] = transit_access[0].text if transit_access else None
            df.loc[df.index[i], 'Wesbite'] = website[0].text if website else None
            
            # log each row
            print(f"Row {i + 1}: {sm_list[i]} LAT{lat} LNG{lng}")

        except:

            print(f'Row {i + 1}: Error Occurred.')
            pass

    # save to csv file
    final_file = '../datasets/Shopping Mall Dataset/Shopping Mall Dataset_006.csv'
    df.to_csv(final_file, index=False, header=True)


if __name__ == "__main__":
    main()
    driver.quit()




