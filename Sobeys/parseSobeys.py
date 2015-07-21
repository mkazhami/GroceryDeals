from selenium import webdriver
import time
import re
import os

# phantomjs.exe is located in the root directory
driver = webdriver.PhantomJS(executable_path="../phantomjs.exe", service_log_path=os.path.devnull)
driver.set_window_size(1400,1000)
driver.get("https://www.sobeys.com/en/stores")
time.sleep(8)

zoomOut = driver.find_element_by_xpath(".//div[@title='Zoom out']")
for i in range(10):
    zoomOut.click()
    time.sleep(0.5)

time.sleep(2) # just in case
stores = driver.find_elements_by_xpath(".//div[@class='card-inset normal-hr box_item']")
saveMyStoreLinks = []
storeNames = []
storeAddresses = []
storeCitys = []
storeProvinces = []
storePostalCodes = []
storeNumbers = []

for store in stores:
    button = store.find_element_by_xpath(".//a[@class='button']")
    saveStoreLink = str(button.get_attribute("href").encode('ascii', 'ignore'))
    saveMyStoreLinks.append(saveStoreLink)

for link in saveMyStoreLinks:
    # go back to page with store preference links
    driver.get("https://www.sobeys.com/en/stores")
    time.sleep(5)
    # get zoom out object and zoom out
    zoomOut = driver.find_element_by_xpath(".//div[@title='Zoom out']")
    for i in range(10):
        zoomOut.click()
        time.sleep(0.5)
    time.sleep(1)
    try:
        # try to get original preference link and click it
        driver.find_element_by_xpath(".//a[@href='" + link + "']").click()
    except:
        # if previous link fails, try just the relative path instead of full link
        driver.find_element_by_xpath(".//a[@href='" + link.split(".com")[1] + "']").click()
    # get the store number
    storeNumberElement = driver.find_elements_by_xpath(".//div[@class='grid__item one-quarter lap--one-half palm--one-whole normal-bottom']//p[not(@*)]")[1] # ugly class name
    storeNumber = str(storeNumberElement.get_attribute("innerHTML").encode('ascii', 'ignore')).strip()
    # get the name of the store
    nameElement = driver.find_element_by_xpath(".//h3[@class='h3-sobeys no-bottom']")
    name = str(nameElement.text.encode('ascii', 'ignore')).strip()
    # get address of store
    fullAddress = driver.find_element_by_xpath(".//p[@class='palm--hide']")
    fullAddress = str(fullAddress.text.encode('ascii', 'ignore')).splitlines()
    address = fullAddress[0]
    postalSubstringStart = re.search("[A-Z][1-9][A-Z]( )*[1-9][A-Z][1-9]" , fullAddress[1]).start()
    postalCode = fullAddress[1][postalSubstringStart:].strip()
    cityAndProvince = fullAddress[1][:postalSubstringStart].split(",")
    city = cityAndProvince[0].strip()
    province = cityAndProvince[1].strip()
    print("\n\n\nname       " + name)
    print("store number  " + storeNumber)
    print("address      " + address)
    print("postal code      " + postalCode)
    print("city      " + city)
    print("province    " + province)
        
    continue
    # go to flyer with new preferred store
    driver.get("https://www.sobeys.com/en/flyer")
    time.sleep(2)

    while(True):
        productCards = driver.find_elements_by_xpath(".//div[@class='card-top']//div[@class='card-inset']")
        for product in productCards:
            nameElement = product.find_element_by_xpath(".//h6[@class='h6 x-small-bottom']")
            priceElement = product.find_element_by_xpath(".//div[@class='price']")
            name = str(nameElement.get_attribute("innerHTML").encode('ascii', 'ignore'))
            priceElement = priceElement.find_element_by_xpath(".//div[@class='price-amount']")
            priceUnit = ""
            xForY = ""
            price = ""
            pricePer = ""
            promo = ""
            try:
                priceUnit = str(priceElement.find_element_by_xpath(".//span[@class='price-unit']").get_attribute("innerHTML").encode('ascii', 'ignore'))
            except:
                try:
                    priceUnit = ""
                    xForY = str(priceElement.get_attribute("innerHTML").encode('ascii', 'ignore'))
                    price = xForY.replace('<sup>', '.').replace('</sup>', '')
                    pricePer = price.split("/")[0]
                    price = price.split("/")[1]
                    print(name + " is " + pricePer + " for $" + price)
                except:
                    promosElement = product.find_element_by_xpath(".//li[@class='price-promos-air-miles']")
                    promo = str(product.find_element_by_xpath(".//p").text.encode('ascii', 'ignore'))
                    promo = promo[re.search("BUY .* EARN", promo).start():]
                    print(name + " has a promo! " + promo)
                    
                    
        try:
            nextButton = driver.find_element_by_xpath(".//i[@class='icon-arrow-right']")
            nextButton.click()
            time.sleep(1)
        except:
            # were on last page, break loop
            break


    

driver.close()
