from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait     
from selenium.webdriver.common.by import By     
from selenium.webdriver.support import expected_conditions as EC
import re
import numpy as np
import pandas as pd

driver = webdriver.Chrome('/Drivers/Chrome/chromedriver')
driver.get('https://en.wikipedia.org/wiki/List_of_shopping_malls_in_Singapore')


def dms2dd(dms):
    # Reference: dms = """1°51′56.29"N"""
    deg, mins, secs, direction = re.split('[°′″]+', dms)
    dd = float(deg) + float(mins) / 60 + float(secs) / (60*60)
    if direction in ('S', 'W'):
        dd *= -1
    return dd


# shopping_malls = driver.find_elements_by_xpath('//div[@class="div-col columns column-width"]/ul/li/a')
shopping_malls = WebDriverWait(driver, 20).until(EC.visibility_of_all_elements_located((By.XPATH, '//div[@class="div-col columns column-width"]/ul/li/a')))
links = [s.get_attribute('href') for s in shopping_malls]


sm_list = []
for s in range(len(shopping_malls)):
    sm_list.append(shopping_malls[s].text)

columns = ['Shopping Mall Name', 'Location', 'Address', 'Latitude', 'Longitude', 'Opening Date',
           'Developer', 'Management', 'Owner', 'Number of Stores', 'Number of Floors', 
           'Floor Area', 'Transit Access', 'Website']
df = pd.DataFrame(columns=columns, index=np.arange(len(sm_list)))

for idx, link in enumerate(links):
    driver.get(link)

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

        df.loc[df.index[idx], 'Shopping Mall Name'] = sm_list[idx]
        df.loc[df.index[idx], 'Location'] = location[0].text if location else None
        df.loc[df.index[idx], 'Address'] = address[0].text if address else None

        lat, lon = 0, 0
        if coordinates:

            # convert coords to latitude and longitude
            coord = coordinates[0].text
            lat, lon = str(coord).split(' ')

            if any(dms_str in coord for dms_str in ['″', '′']):
                lat = dms2dd(lat)
                lon = dms2dd(lon)
            else:
                print(lat, lon)
                lat = lat.translate(str.maketrans({'°': None, 'N': None, 'E': None, 'S': None, 'W': None}))
                lon = lon.translate(str.maketrans({'°': None, 'N': None, 'E': None, 'S': None, 'W': None}))

        df.loc[df.index[idx], 'Latitude'] = lat if lat else None
        df.loc[df.index[idx], 'Longitude'] = lon if lon else None
        df.loc[df.index[idx], 'Opening Date'] = opening_date[0].text if opening_date else None
        df.loc[df.index[idx], 'Developer'] = developer[0].text if developer else None
        df.loc[df.index[idx], 'Management'] = management[0].text if management else None
        df.loc[df.index[idx], 'Owner'] = owner[0].text if owner else None
        df.loc[df.index[idx], 'Number of Stores'] = num_of_stores[0].text if num_of_stores else None
        df.loc[df.index[idx], 'Number of Floors'] = num_of_floors[0].text if num_of_floors else None
        df.loc[df.index[idx], 'Floor Area'] = floor_area[0].text if floor_area else None
        df.loc[df.index[idx], 'Transit Access'] = transit_access[0].text if transit_access else None
        df.loc[df.index[idx], 'Wesbite'] = website[0].text if website else None

    except:

        print('Erorr Occurred!')
        pass

#print(sm_list)
#print(links)
df.to_csv('Shopping Mall Dataset.csv', index=False, header=True)

driver.quit()