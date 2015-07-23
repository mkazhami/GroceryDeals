# -*- coding: utf-8 -*-

from selenium import webdriver
import time
import os
import re

# Authors: e4 + m7
#
# this program will go through all pages of the zehrs flyer and grab the info for each product
#
# requires selenium (and python obviously) to be installed - selenium can be installed through 'pip install selenium'
# assuming you have the pip installer




# opens phantom browser
# phantomjs.exe is located in the root directory
#driver = webdriver.PhantomJS(executable_path="/home/mikhail/Documents/htmlparse/phantomjs_linux")
driver = webdriver.PhantomJS()
driver.set_window_size(1400,1000)
#driver = webdriver.Firefox()

# go to the list page of all stores in ontario
driver.get("http://www.loblaws.ca/en_CA/store-list-page.ON.html")
# let javascript load
time.sleep(5)

# press 'ontario' button to close the pop-up
# shouldn't have any affect
driver.find_element_by_xpath(".//a[@class='btn' and @data-province='ON']").click()
time.sleep(1)

# get list columns of stores
cityLists = driver.find_elements_by_xpath(".//div[@class='content']//div[@class='column-layout col-4']//div")
cityURLs = []
storeNames = []
storeAddresses = []
storeCitys = []
storeProvinces = []
storePostalCodes = []
storeNumbers = []
# extracts the urls for each city
for cityList in cityLists:
    urls = cityList.find_elements_by_xpath(".//ul[@class='store-select']//li//a")
    for url in urls:
        cityURLs.append(str(url.get_attribute("href").encode('ascii', 'ignore')))
# goes through each city, opens each store's flyers
for url in cityURLs:
    # open link to city's page
    driver.get(url)
    time.sleep(5)
    # get all the store 'view flyer' buttons
    viewFlyerButtons = driver.find_elements_by_xpath(".//a[@class='button view-flyer']")
    viewFlyerLinks = []
    # get all of the store numbers
    storeNumberElements = driver.find_elements_by_xpath(".//div[@class='store-listing-row']")
    # get the addresses and names of all the stores
    # address is in form:
    #       street
    #       city, province    postal code
    #       phone
    #       manager
    # we only care about the first two lines
    addresses = driver.find_elements_by_xpath(".//p[@class='store-address']")
    names = driver.find_elements_by_xpath(".//div[@class='store-info']//h3[@class='title']")
    
    # make sure there is one button, name, and address for each store
    if (len(viewFlyerButtons) != len(names)) or (len(viewFlyerButtons) != len(addresses)) or (len(viewFlyerButtons) != len(storeNumberElements)):
        print("unequal number of view flyer buttons, names of stores, addresses, and store numbers")
        print("flyer buttons: " + str(len(viewFlyerButtons)) + "  names: " + str(len(names)) + "  addresses: " + str(len(addresses)) + "  store numbers: " + len(storeNumberElements))
        raise Exception("exiting due to error in parsing")

    # get all the store 'view flyer' urls from the buttons as well as each store's info
    for i in range(len(viewFlyerButtons)):
        viewFlyerLinks.append(str(viewFlyerButtons[i].get_attribute("href").encode('ascii', 'ignore')))
        # store title tag just contains the name
        storeNames.append(str(names[i].text.encode('ascii', 'ignore')))
        # split the full address by <br> tag
        fullAddress = str(addresses[i].get_attribute("innerHTML").encode('ascii', 'ignore')).split("<br>")
        # street name comes first with no special characters
        address = fullAddress[0]
        # split on the "no-break space" character that they use to separate the city and postal code
        cityAndPostal = fullAddress[1].split("&nbsp;")
        cityAndPostal = [item for item in cityAndPostal if item != ""]
        # split city and province using the ',' and get rid of leading/trailing whitespace
        storeCitys.append(cityAndPostal[0].split(",")[0].strip())
        storeProvinces.append(cityAndPostal[0].split(",")[1].strip())
        storePostalCodes.append(cityAndPostal[1].replace(" ", ""))
        # get the store number
        storeNumbers.append(str(storeNumberElements[i].get_attribute("data-store-number").encode('ascii', 'ignore')))
        storeAddresses.append(address)

        
    for link in viewFlyerLinks:
        # open specific store's flyer
        driver.get(link)
        time.sleep(10)
        # go to accessibility view
        driver.find_element_by_xpath("//ul[@class='sort-options tab-layout tabs-3']//li//a[@class='accessible-view']").click()
        time.sleep(5)
        try:
            # get all html elements that have product info
            driver.switch_to_frame(driver.find_element_by_xpath("//iframe[@id='videoFrame']"))
            #print(driver.page_source.encode('utf-8', 'ignore'))
            elements = driver.find_elements_by_xpath(".//div[@id='content']//table//tbody//tr")
            if len(elements) == 0:
                raise Exception("could not find elements")
            # iterate over each product
            for i in range(len(elements)):
                element = elements[i]
                if re.search("Page [0-9]", element.text) is not None:
                    i += 1
                    products = elements[i].find_elements_by_xpath(".//table")
                    for product in products:
                        product = product.find_elements_by_xpath(".//tbody/tr")
                        name = product[0].text.encode('utf-8', 'ignore')
                        productInfo = product[1].text.encode('utf-8', 'ignore').replace("\n", " ")
                        print("name: " + name + "      info: " + productInfo)

        except Exception as e:
            # print exception message and break from loop since we've gone through all the pages
            print(str(e))

#for i in range(len(storeNames)):
#    print("\n\n\nname:  " + storeNames[i] + "\naddress:  " + storeAddresses[i] + "\ncity:  " + storeCitys[i] + "\nprovince:  "  +
#            storeProvinces[i] + "\npostal:  " + storePostalCodes[i] + "\nstore number:  " + storeNumbers[i])
                
# close the web browser
driver.close()
