# -*- coding: utf-8 -*-

from baseparseclass import BaseParseClass
from item import Item
from selenium import webdriver
import time
import datetime
import os
import re
import csv

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
        driver.set_window_size(1400,1000)
        logger = self.log
        
        try:
            logger.logInfo("Opening " + self.store_list_links[self.store_name])
            driver.get(self.store_list_links[self.store_name])
            time.sleep(8)
            
            logger.logDebug("Zooming out of map...")
            zoomOut = driver.find_element_by_xpath(".//div[@title='Zoom out']")
            for i in range(10):
                zoomOut.click()
                time.sleep(0.5)

            time.sleep(2) # just in case
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
                    continue
                driver.get(link)
                time.sleep(5)

                try:
                    logger.logDebug("Saving store as 'my store'")
                    driver.find_element_by_xpath(".//a[@id='save-as-my-store']").click()
                    time.sleep(3)
                except:
                    # if store is already selected, the button wouldn't be there - check for that in the currently selected store
                    myStore = driver.find_element_by_xpath(".//ul[@class='list-inline']")
                    if link.split("com")[1] in myStore.get_attribute("innerHTML").encode('ascii', 'ignore'):
                        pass # don't do anything, store is already selected
                    else:
                        raise Exception("Save my store button not found")

                logger.logDebug("Getting store info...")
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
                
                logger.logDebug("Name:  " + name)
                logger.logDebug("Store Number:  " + storeNumber)
                logger.logDebug("Address:  " + address)
                logger.logDebug("Postal Code:  " + postalCode)
                logger.logDebug("City:  " + city)
                logger.logDebug("Province:  " + province)
                
                logger.logDebug("Opening flyer...")
                # go to flyer with new preferred store
                driver.get("https://www.sobeys.com/en/flyer")
                time.sleep(8)

                logger.logDebug("Switching frame...")
                # switch frame
                driver.switch_to_frame(driver.find_element_by_xpath("//iframe[@id='flipp-iframe']"))
                time.sleep(1)

                logger.logDebug("Going to Item View...")
                # go to item view
                labelElement = driver.find_element_by_xpath(".//div[@class='grid-view-label']")
                if "Item View" in labelElement.get_attribute("innerHTML"):
                    labelElement.click()
                else:
                    raise Exception("No 'Item View' found")
                time.sleep(8)
                
                logger.logDebug("Getting products...")
                # get all product elements
                tries = 0
                products = driver.find_elements_by_xpath(".//li[@class='item']")
                while len(products) == 0 and tries <= 5:
                    logger.logDebug("number of products: " + str(len(products)))
                    driver.refresh()
                    time.sleep(8)
                    driver.switch_to_frame(driver.find_element_by_xpath("//iframe[@id='flipp-iframe']"))
                    time.sleep(1)
                    driver.find_element_by_xpath(".//div[@class='grid-view-label']").click()
                    time.sleep(8)
                    products = driver.find_elements_by_xpath(".//li[@class='item']")
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
                            
                        findPoints = re.search("(BUY|SPEND)[A-Z ]*[0-9]+[A-Z ]*EARN.*[0-9]+.*MILES", additional_info.upper())
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
                        logger.logDebug("using normal price")
                        #print(name + "      " + repr(prePriceText) + " " + repr(dollarSign) + " " + repr(dollar) + " " + repr(dot) + " " + repr(cents) + " " + repr(restOfText))
                    else:
                        logger.logDebug("using uneven price")
                        #print(name)
                        for i in range(len(priceText)):
                            logger.logDebug(priceText[i].text.encode('utf-8', 'ignore'))
                    itemStory = product.find_element_by_xpath(".//div[@class='item-story']")
                    if len(itemStory.text) < 5:
                        try:
                            itemStory = itemStory.find_element_by_xpath(".//span")
                            if len(itemStory.text) > 0:
                                additional_info += itemStory.get_attribute("innerHTML").encode('utf-8', 'ignore')
                            else:
                                raise Exception("")
                        except:
                            try:
                                itemStory = itemStory.find_element_by_xpath(".//div[@class='item-story wishabi-offscreen']")
                                if len(itemStory.text) > 0:
                                    additional_info += itemStory.get_attribute("innerHTML").encode('utf-8', 'ignore')
                                else:
                                    raise Exception("")
                            except:
                                logger.logDebug("Unable to get item story")
                            
                    logger.logDebug(name) #+ "      " + prePriceText + " " + dollarSign + " " + dollar + " " + dot + " " + cents + " " + restOfText)
                    logger.logDebug("price: " + price + "  each: " + each + "   quantity: " + quantity + "  limit: " + limit + "  weight: " + weight + "  points: " + points + "  promotion: " + promotion + "  additional info: " + additional_info + "\n")
                    
                    #print("printing item story")
                    #print(repr(itemStory.text.encode('utf-8', 'ignore')) + " \n")
                        
                    #if "$" in dollarSign:
                    #    price = dollar + dot + cents
                logger.logInfo("Done getting items")
        except Exception as e:
            print(str(e))
        finally:
            driver.close()
