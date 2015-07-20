from selenium import webdriver
import time
import re


driver = webdriver.Firefox()
driver.get("https://www.sobeys.com/en/stores")
time.sleep(8)

zoomOut = driver.find_element_by_xpath(".//div[@title='Zoom out']")
for i in range(10):
    zoomOut.click()
    time.sleep(0.5)

time.sleep(2) # just in case
stores = driver.find_elements_by_xpath(".//div[@class='card-inset normal-hr box_item']")
saveMyStoreLinks = []
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
