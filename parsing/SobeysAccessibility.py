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
        #driver = webdriver.PhantomJS(executable_path="phantomjs.exe", service_log_path=os.path.devnull)
        driver = webdriver.Firefox()
        driver.set_window_size(1400,1000)
        driver.get(self.store_list_links[self.store_name])
        time.sleep(8)
        

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

        for store in stores:
            button = store.find_element_by_xpath(".//a[@type='button']")
            saveStoreLink = str(button.get_attribute("href").encode('ascii', 'ignore'))
            saveMyStoreLinks.append(saveStoreLink)

        for link in saveMyStoreLinks:
            # go back to page with store preference links
            #driver.get(self.store_list_links[self.store_name])
            #time.sleep(8)
            # get zoom out object and zoom out
            #zoomOut = driver.find_element_by_xpath(".//div[@title='Zoom out']")
            #for i in range(10):
            #    zoomOut.click()
            #    time.sleep(0.5)
            #time.sleep(3)
            #try:
            #    # try to get original preference link and click it
            #    #driver.find_element_by_xpath(".//a[@class='btn btn-default save-as-my-store' and @href='" + link + "']").click()
            #except:
            #    try:
            #        # try it with http instead of https - for some reason it changes...
            #        driver.find_element_by_xpath(".//a[@class='btn btn-default save-as-my-store' and @href'" + link.replace("https", "http") + "']").click()
            #    except:
            #        try:
            #            # if previous link fails, try just the relative path instead of full link
            #            # if this fails then exit, because something is wrong
            #            driver.find_element_by_xpath(".//a[@class='btn btn-default save-as-my-store' and @href='" + link.split(".com")[1] + "']").click()
            #        except:
            #            raise Exception("Unable to press button to save store as preference: " + link)
            driver.get(link)
            time.sleep(5)

            try:
                driver.find_element_by_xpath(".//a[@id='save-as-my-store']").click()
                time.sleep(3)
            except:
                # if store is already selected, the button wouldn't be there - check for that
                myStore = driver.find_element_by_xpath(".//ul[@class='list-inline']")
                if link.split("com")[1] in myStore.get_attribute("innerHTML").encode('ascii', 'ignore'):
                    pass # don't do anything, store is already selected
                else:
                    raise Exception("Save my store button not found")

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
                 
            print("\n\n\nname       " + name)
            print("store number  " + storeNumber)
            print("address      " + address)
            print("postal code      " + postalCode)
            print("city      " + city)
            print("province    " + province)
                    
                    
            #continue
            
            # go to flyer with new preferred store
            driver.get("https://www.sobeys.com/en/flyer")
            time.sleep(8)

            # switch frame
            driver.switch_to_frame(driver.find_element_by_xpath("//iframe[@id='flipp-iframe']"))
            time.sleep(1)

            # go to item view
            labelElement = driver.find_element_by_xpath(".//div[@class='grid-view-label']")
            if "Item View" in labelElement.get_attribute("innerHTML"):
                labelElement.click()
            else:
                raise Exception("No 'Item View' found")
            time.sleep(8)
            
            # get all product elements
            tries = 0
            products = driver.find_elements_by_xpath(".//li[@class='item']")
            while len(products) == 0 and tries <= 5:
                print("number of products: " + str(len(products)))
                driver.refresh()
                time.sleep(8)
                driver.switch_to_frame(driver.find_element_by_xpath("//iframe[@id='flipp-iframe']"))
                time.sleep(1)
                driver.find_element_by_xpath(".//div[@class='grid-view-label']").click()
                time.sleep(8)
                products = driver.find_elements_by_xpath(".//li[@class='item']")
                tries += 1
            print("number of products: " + str(len(products)))
            
            for product in products:
                #print(str(product.get_attribute("innerHTML").encode('ascii', 'ignore')))
                name = product.find_element_by_xpath(".//div[@class='item-name']").get_attribute("innerHTML").encode('utf-8', 'ignore')
                fullPrice = product.find_element_by_xpath(".//div[@class='item-price']")
                # sobeys divides the price into '$' 'x' '.' 'xx' '¢ (but usually hidden)' 'rest of text (i.e. OR $1.99 EACH)'
                priceText = fullPrice.find_elements_by_xpath(".//span")
                if len(priceText) >= 7:
                    prePriceText = priceText[0].text.encode('utf-8', 'ignore')
                    dollarSign = priceText[1].text.encode('utf-8', 'ignore')
                    dollar = priceText[2].text.encode('utf-8', 'ignore')
                    dot = priceText[3].text.encode('utf-8', 'ignore')
                    cents = priceText[4].text.encode('utf-8', 'ignore')
                    centSign = priceText[5].text.encode('utf-8', 'ignore')
                    restOfText = fullPrice.find_element_by_xpath(".//span[@class='price-text']").text.encode('utf-8', 'ignore')
                    #restOfText = priceText[6].text.encode('utf-8', 'ignore')
                    print(name + "      " + prePriceText + " " + dollarSign + " " + dollar + " " + dot + " " + cents + " " + centSign + " " + restOfText)
                else:
                    for i in range(len(priceText)):
                        print(priceText[i].text.encode('utf-8', 'ignore'))
                #if "$" in dollarSign:
                #    price = dollar + dot + cents
            
            

        driver.close()
