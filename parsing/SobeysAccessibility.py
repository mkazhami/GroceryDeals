# -*- coding: utf-8 -*-

from baseparseclass import BaseParseClass
from item import Item
from selenium import webdriver
import time
import datetime
import os
import re
import csv

longSleep = 8
mediumSleep = 4
shortSleep = 3

class Sobeys(BaseParseClass):
    """
    Class for all stores that follow the format of Sobeys (so far just Sobeys...)
    """
    
    store_list_links = { 
                         "sobeys" : "https://www.sobeys.com/en/store-locator/"
                       }
    
    store_rewards_programs = {
                                "sobeys" : "Air Miles"
                             }

    def __init__(self, store_name, logger):
        self.store_name = store_name
        self.storeNames = []
        self.storeAddresses = []
        self.storeCities = []
        self.storeProvinces = []
        self.storePostalCodes = []
        self.storeNumbers = []
        self.log = logger

    def parse(self):
        # phantomjs.exe is located in the root directory
        driver = webdriver.PhantomJS(executable_path="phantomjs.exe", service_log_path=os.path.devnull)
        #driver = webdriver.Firefox()
        driver.set_window_size(1800,1400)
        logger = self.log
        
        try:
            logger.logInfo("Opening " + self.store_list_links[self.store_name])
            driver.get(self.store_list_links[self.store_name])
            time.sleep(longSleep)

            logger.logDebug("Zooming out of map...")
            tries = 0
            while tries <= 5:
                try:
                    zoomOut = driver.find_element_by_xpath(".//div[@title='Zoom out']")
                    for i in range(10):
                        zoomOut.click()
                        time.sleep(0.5)
                    break
                except Exception as e:
                    logger.logDebug("Faild to zoom out. Retrying... " + str(tries) " of 5.")
                    tries += 1
            if tries >= 5:
                logger.logError("Unable to zoom out. Skipping store.")
                continue



            time.sleep(shortSleep) # just in case
            stores = driver.find_elements_by_xpath(".//div[@class='row store-result-container']")
            saveMyStoreLinks = []
            storeNames = []
            storeAddresses = []
            storeCitys = []
            storeProvinces = []
            storePostalCodes = []
            storeNumbers = []

            logger.logDebug("Getting all 'save my store' buttons")
            for store in stores:
                button = store.find_element_by_xpath(".//a[@type='button']")
                saveStoreLink = str(button.get_attribute("href").encode('ascii', 'ignore'))
                saveMyStoreLinks.append(saveStoreLink)

            for link in saveMyStoreLinks:
                logger.logInfo("Opening new store's page at: " + link)
                if link == "https://www.sobeys.com/en/stores/test-preview-on/": # random test link/store that they didn't clean up i'm guessing - doesn't go anywhere
                    logger.logInfo("Skipping [test] store")
                    continue
                driver.get(link)
                time.sleep(shortSleep)
                
                # check if store is closed
                try:
                    storeHours = driver.find_element_by_xpath(".//div[@id='storehour']")
                    storeHoursText = storeHours.get_attribute("innerHTML").encode('utf-8', 'ignore')
                    if "Permanantly Closed" in storeHoursText: # some stores are closed but remain in the list - saving them as a store won't do anything
                        fout = open("../LogFiles/" + link.split("/")[-1] + ".source", 'w')
                        fout.write(storeHoursText)
                        fout.flush()
                        fout.close()
                        logger.logInfo("Skipping permanently closed store")
                        continue
                except Exception as e:
                    logger.logError(str(e))
                    logger.logError("Unable to find store hours. Skipping store...")
                    continue

                try:
                    logger.logDebug("Saving store as 'my store'")
                    driver.find_element_by_xpath(".//a[@id='save-as-my-store']").click()
                    time.sleep(shortSleep)
                except:
                    # if store is already selected, the button wouldn't be there - check for that in the currently selected store
                    myStore = driver.find_element_by_xpath(".//ul[@class='list-inline']")
                    if link.split("com")[1] in myStore.get_attribute("innerHTML").encode('ascii', 'ignore'):
                        pass # don't do anything, store is already selected
                    else:
                        raise Exception("Save my store button not found")

                name = ""
                address = ""
                storeNumber = ""
                city = ""
                postalCode = ""
                province = ""

                logger.logDebug("Getting store info...")
                try:
                    name = driver.find_element_by_xpath(".//div[@class='combo-right']//div[@class='left']").text.encode('ascii', 'ignore').strip()
                    # there are a couple of elements with identical structure
                    storeInformationElements = driver.find_elements_by_xpath(".//div[@class='col-sm-3']")
                    for element in storeInformationElements:
                        html = element.get_attribute("innerHTML")
                        if "Store Number" in html:
                            storeNumber = str(element.find_element_by_xpath(".//p").get_attribute("innerHTML").encode('ascii', 'ignore')).strip()
                        elif "Address" in html:
                            storeAddress = str(element.find_element_by_xpath(".//p").get_attribute("innerHTML").encode('ascii', 'ignore')).strip()
                            address = storeAddress.split("<br>")[0]
                            restOfAddress = storeAddress.split("<br>")[1]
                            city = restOfAddress.split(",")[0].strip()
                            findPostalCode = re.search("[A-Z][0-9][A-Z]( )?[0-9][A-Z][0-9]", restOfAddress.split(",")[1])
                            postalCode = restOfAddress.split(",")[1][findPostalCode.start():].replace(" ", "")
                            province = restOfAddress.split(",")[1][:findPostalCode.start()].strip()
                except Exception as e:
                    logger.logError(str(e))
                    if address == "" or postalCode == "":
                        logger.logError("Failed to find some store info. Address or postal code unavailable, skipping store.")
                        continue
                    logger.logError("Failed to find some store info. Continuing...")
                
                logger.logDebug("Name:  " + name)
                logger.logDebug("Store Number:  " + storeNumber)
                logger.logDebug("Address:  " + address)
                logger.logDebug("Postal Code:  " + postalCode)
                logger.logDebug("City:  " + city)
                logger.logDebug("Province:  " + province)
                
                logger.logDebug("Opening flyer...")
                # go to flyer with new preferred store
                driver.get("https://www.sobeys.com/en/flyer")
                time.sleep(mediumSleep)

                logger.logDebug("Switching frame...")
                # switch frame
                tries = 0
                while tries <= 5:
                    try:
                        driver.switch_to_frame(driver.find_element_by_xpath("//iframe[@id='flipp-iframe']"))
                        time.sleep(1)
                        break
                    except:
                        logger.logDebug("Failed to switch frame. Retrying " + str(tries) + " of 5...")
                        driver.refresh()
                        time.sleep(mediumSleep)
                        tries += 1
                
                if tries >= 5:
                    logger.logError("Unable to switch frame. Skipping store.")
                    continue

                logger.logDebug("Going to Item View...")
                # go to item view
                try:
                    noFlyer = driver.find_element_by_xpath(".//div[@class='enter_postal_code_area']//div[@class='enter_postal_code']//div[@id='zero_case_content']")
                    print("no flyer displayed")
                    logger.logError("No flyer for this store")
                    continue
                except Exception as e:
                    #logger.logDebug(str(e))
                    pass # all good
                
                tries = 0
                while tries <= 5:
                    try:
                        labelElement = driver.find_element_by_xpath(".//div[@class='grid-view-label']")
                        if "Item View" in labelElement.get_attribute("innerHTML"):
                            labelElement.click()
                        break
                    except:
                        logger.logDebug("Failed to press item view. Retrying + " + str(tries) + " of 5...")
                        tries += 1
                        driver.refresh()
                        time.sleep(mediumSleep)
                
                if tries >= 5:
                    logger.logDebug("Unable to press item view. Skipping store.")
                    continue
                    
                logger.flush()
                continue
                
                time.sleep(mediumSleep)
                
                logger.logDebug("Getting products...")
                # get all product elements
                tries = 0
                products = driver.find_elements_by_xpath(".//li[@class='item']")
                while len(products) == 0 and tries <= 5:
                    try:
                        logger.logDebug("number of products: " + str(len(products)))
                        driver.refresh()
                        time.sleep(8)
                        driver.switch_to_frame(driver.find_element_by_xpath("//iframe[@id='flipp-iframe']"))
                        time.sleep(1)
                        driver.find_element_by_xpath(".//div[@class='grid-view-label']").click()
                        time.sleep(8)
                        products = driver.find_elements_by_xpath(".//li[@class='item']")
                    except:
                        pass # keep retrying...
                    tries += 1
                logger.logDebug("number of products: " + str(len(products)))
                
                logger.logDebug("Parsing products information...")
                for product in products:
                    #print(str(product.get_attribute("innerHTML").encode('ascii', 'ignore')))
                    name = product.find_element_by_xpath(".//div[@class='item-name']").get_attribute("innerHTML").encode('utf-8', 'ignore')
                    if name == "Sobeys" or name == "Facebook" or name == "Twitter": # terrible design decisions by sobeys - put their info into product cards
                        continue
                    price = ""
                    quantity = "1"
                    weight = ""
                    limit = ""
                    each = ""
                    additional_info = ""
                    points = ""
                    promotion = ""
                    
                    fullPrice = product.find_element_by_xpath(".//div[@class='item-price']")
                    # sobeys divides the price into '$' 'x' '.' 'xx' '¢ (but usually hidden)' 'rest of text (i.e. OR $1.99 EACH)'
                    priceText = fullPrice.find_elements_by_xpath(".//span")
                    if len(priceText) >= 7:
                        prePriceText = priceText[0].get_attribute("innerHTML").encode('utf-8', 'ignore').replace('\n', '')
                        dollarSign = priceText[1].get_attribute("innerHTML").encode('utf-8', 'ignore')
                        dollar = priceText[2].get_attribute("innerHTML").encode('utf-8', 'ignore')
                        dot = priceText[3].get_attribute("innerHTML").encode('utf-8', 'ignore')
                        cents = priceText[4].get_attribute("innerHTML").encode('utf-8', 'ignore')
                        centSign = priceText[5].get_attribute("innerHTML").encode('utf-8', 'ignore')
                        additional_info = fullPrice.find_element_by_xpath(".//span[@class='price-text']").text.encode('utf-8', 'ignore')
                        additional_info = repr(additional_info).replace(r'\xc2\xae', '').replace("\'", "")
                        if "$" in dollarSign:
                            price = dollarSign + dollar + dot + cents
                        else:
                            logger.logDebug("NO DOLLAR SIGN IN DOLLARSIGN VAR: " + str(priceText[1].get_attribute("innerHTML")))
                        
                            
                        findQuantity = re.search("[0-9]+/", prePriceText)
                        if findQuantity is not None:
                            quantity = prePriceText[findQuantity.start():findQuantity.end()].replace("/", "")
                            
                        findPoints = re.search("(BUY|SPEND)[A-Z ]*[0-9]+.*EARN.*[0-9]+.*MILES", additional_info.upper())
                        if findPoints is not None:
                            points = additional_info[findPoints.start():findPoints.end()].upper().split("EARN")[1]
                            findNum = re.search("[0-9]+", points)
                            points = points[findNum.start():findNum.end()]
                            promotion = additional_info[findPoints.start():findPoints.end()]
                            additional_info = additional_info.replace(promotion, "")
                            
                        findWeight = re.search("/( )*(kg|lb|([0-9]+( )*g))", additional_info.lower())
                        if findWeight is not None:
                            weight = additional_info[findWeight.start():findWeight.end()].replace("/", "").strip()
                            additional_info = additional_info.replace(additional_info[findWeight.start():findWeight.end()], "")
                            
                        findEach = re.search("[Oo][Rr]( )* (\$)?[0-9]+(\.[0-9]+)?( )*[Ee][Aa]([Cc][Hh])?(\.)?", additional_info)
                        if findEach is not None:
                            findNum = re.search("(\$)?[0-9]+(\.[0-9]+)?", additional_info)
                            each = additional_info[findNum.start():findNum.end()]
                            if "$" not in each:
                                each = "$" + each
                            additional_info = additional_info.replace(additional_info[findEach.start():findEach.end()], "")
                        
                        if len(additional_info.replace(" ", "").replace("each", "")) < 5: # remove any leftover junk (periods, commas, some leftover 'each's)
                            additional_info = ""
                    else:
                        logger.logDebug("using uneven price")
                        #print(name)
                        for i in range(len(priceText)):
                            logger.logDebug(priceText[i].text.encode('utf-8', 'ignore'))
                    itemStory = product.find_element_by_xpath(".//div[@class='item-story wishabi-offscreen']")
                    itemStoryText = itemStory.get_attribute("innerHTML").encode('utf-8', 'ignore').replace("<span>", "").replace("</span>", "").strip()
                    if len(itemStoryText) < 3:
                        pass
                        # commented out because took 10 extra seconds for this
                        #try:
                        #    logger.logDebug("First attempt failed, looking for others")
                        #    additional_info += product.find_element_by_xpath(".//div[@class='item-story wishabi-offscreen']//span").get_attribute("innerHTML").encode('utf-8', 'ignore')
                        #except:
                        #    print("text: " + itemStory.text.encode('utf-8', 'ignore'))
                        #    print("html: " + itemStory.get_attribute("innerHTML").encode('utf-8', 'ignore'))
                    else:
                        findPoints = re.search("(BUY|SPEND)[A-Z ]*[0-9]+.*EARN.*[0-9]+.*MILES", additional_info.upper())
                        if findPoints is not None:
                            points = additional_info[findPoints.start():findPoints.end()].upper().split("EARN")[1]
                            findNum = re.search("[0-9]+", points)
                            points = points[findNum.start():findNum.end()]
                            promotion = additional_info[findPoints.start():findPoints.end()]
                            additional_info = additional_info.replace(promotion, "")
                        additional_info += itemStoryText
                            
                    if price == "" and len(additional_info.strip()) == 0:
                        continue # ignore item
                    logger.logDebug(name)
                    logger.logDebug("price: " + price + "  each: " + each + "   quantity: " + quantity + "  limit: " + limit + "  weight: " + weight + "  points: " + points + "  promotion: " + promotion + "  additional info: " + additional_info + "\n")
                    
                logger.logInfo("Done getting items")
        except Exception as e:
            logger.logError(str(e))
            driver.save_screenshot('out.png');
        finally:
            driver.close()
