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
                         "sobeys" : ""
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
        trueStoresListLink = "https://www.sobeys.com/en/stores"
        driver.get("https://www.sobeys.com/en/stores")
        time.sleep(8)
        if len(driver.page_source) < 100:
            trueStoresListLink = "https://www.sobeys.com/en/store-locator/"
            driver.get("https://www.sobeys.com/en/store-locator/")
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
            driver.get(trueStoresListLink)
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
                
            name = driver.find_element_by_xpath(".//div[@class='combo-right']//div[@class='left']").text.encode('ascii', 'ignore').strip()
            # there are a couple of elements with identical structure
            storeInformationElements = driver.find_elements_by_xpath(".//div[@class='col-sm-3']")
            for element in storeInformationElements:
                print("going through a store information element")
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

            # go to item view
            labelElements = driver.find_elements_by_xpath(".//div[@class='grid-view-label']")
            for labelElement in labelElements:
                if "Item View" in labelElement.get_attribute("innerHTML"):
                    labelElement.click()
                    break
            time.sleep(8)
            
            # get all product elements
            products = driver.find_elements_by_xpath(".//li[@class='item']")
            
            for product in products:
                print(str(product.get_attribute("innerHTML")))
            
            

        driver.close()
