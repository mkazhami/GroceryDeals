# -*- coding: utf-8 -*-

from baseparseclass import BaseParseClass
from item import Item
from selenium import webdriver
import time
import datetime
import os
import re
import csv


class ZehrsLoblaws(BaseParseClass):
    """
    Parent class to the different stores that follow similar page formats
    """
    
    store_list_links = { 
                         "zehrs" : "http://www.zehrs.ca/en_CA/store-list-page.html",
                         "loblaws" : "http://www.loblaws.ca/en_CA/store-list-page.html"
                       }
    
    store_rewards_programs = {
                                "zehrs": "PCPlus",
                                "loblaws": "PCPlus"
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
        logger = self.log
        csvFileName = "../CsvFiles/" + self.store_name + "-" + str(datetime.date.today()) + ".csv"
        try:
            os.remove(csvFileName)
        except OSError:
            pass
        #csvFile = open("../CsvFiles/" + self.store_name + "-" + str(datetime.date.today()) + ".csv", "w")
        # opens phantom browser
        # phantomjs.exe is located in the root directory
        #self.driver = webdriver.PhantomJS(executable_path="/home/mikhail/Documents/htmlparse/phantomjs_linux")
        #driver = webdriver.PhantomJS(executable_path="./phantomjs_linux")
        driver = webdriver.PhantomJS()
        driver.set_window_size(1400,1000)
        driver.set_page_load_timeout(30)
        #self.driver = webdriver.Firefox()

        logger.logInfo("Opening store list page for " + self.store_name + "...")
        # go to the list page of all stores in ontario
        driver.get(self.store_list_links[self.store_name])
        # let javascript load
        time.sleep(5)

        if self.store_name == "loblaws":
            logger.logInfo("Closing 'select province' button for loblaws")
            # press 'ontario' button to close the pop-up
            # shouldn't have any affect on the flyers
            tries = 0
            while tries <= 5:
                try:
                    driver.find_element_by_xpath(".//a[@class='btn' and @data-province='ON']").click()
                except:
                    driver.refresh()
                    tries += 1
                    time.sleep(5)
                    Logger.logInfo("Failed to find/close loblaws province button. Retrying " + str(tries) + " of 5...")
            time.sleep(1)
        
        provinces = []
        provinceLinks = []
        # get list of provinces
        provinceElementList = driver.find_elements_by_xpath(".//div[@class='col']//ul[@class='store-select']//li//a")
        for provinceElement in provinceElementList:
            provinces.append(str(provinceElement.text.encode('ascii', 'ignore')))
            provinceLinks.append(str(provinceElement.get_attribute("href").encode('ascii', 'ignore')))

        storeCount = 0
        for provIdx, provinceLink in enumerate(provinceLinks):
            if provinces[provIdx].strip().upper() == "QUEBEC":
                saveRE = "(économisez/)?save"
                dozenRE = "(((\$[0-9]+( )*DOZEN)|([0-9]+( )*\$( )*DOZEN))|((DOZEN( )*\$[0-9]+)|(DOZEN( )*[0-9]+( )*\$)))"
                lessThanRE = "LESS( )*THAN( )*[0-9]+( )*(\$)?[0-9]+(\.| |,)[0-9]+( )*(\$( )*)?(CH\./)?EA(\.|CH)"
                orRE = "[0-9]+/((\$[0-9]+((\.|,)[0-9]+)?)|([0-9]+((\.|,)[0-9]+)?( )*\$))( )*(OU/)?OR( )*((\$[0-9]+((\.| |,)[0-9]+)?)|([0-9]+((\.| |,)[0-9]+)?( )*\$)|([0-9]+( )*¢))( )*((CH\./)?( )*EA(\.|CH))?"
                lbRE = "((\$[0-9]*((\.|,)[0-9]*)?)|([0-9]+((\.|,)[0-9]*)?( )*\$))( )*(([Cc][Hh]\.)?[Ee][Aa]\.)?( )*/?( )*lb( )*(/)?"
                kgRE = "\$[0-9]*(\.|,)[0-9]*( )*/( )*kg( )*(/)?"
                gRE = "\$[0-9]+((\.| |,)[0-9]+)?( )*/[0-9]+( )*[Gg]"
                limitRE = "LIMIT( OF|E DE)?( )*[0-9]+( )*(AFTER|APRèS) LIMIT(E)?( )*((\$[0-9]+((\.| |,)[0-9]+)?)|([0-9]+((\.| |,)[0-9]+)?( )*\$))( )*(CH\.( )*/( )*)?(EA(\.|CH))?"
                xforyRE = "[0-9]+( )*/( )*((\$[0-9]+((\.| |,)[0-9]+)?)|([0-9]+((\.| |,)[0-9]+)?( )*\$))"
                eachRE = '((\$[0-9]+((\.| |,)[0-9]+)?)|([0-9]+((\.| |,)[0-9]*)?( )*\$))( )*((ch\./)?ea(\.|ch))'
                priceRE = "((\$[0-9]+((\.| |,)[0-9]+)?)|([0-9]+((\.| |,)[0-9]*)?( )*\$)|([0-9]+( )*¢))"
            else:
                saveRE = "[Ss][Aa][Vv][Ee]"
                dozenRE = "\$[0-9]+( )*DOZEN"
                lessThanRE = "LESS( )*THAN( )*[0-9]+( )*\$[0-9]+(\.| )[0-9]+( )*EA(\.|CH)"
                orRE = "[0-9]+/\$[0-9]+(\.[0-9]+)?( )*OR( )*((\$[0-9]+(\.| )?[0-9]*)|([0-9]+¢))( )*EA(\.|CH)"
                lbRE = "\$[0-9]*(\.[0-9]*)?( )*([Ee][Aa]\.)?( )*/?( )*lb( )*(/)?"
                kgRE = "\$[0-9]*\.[0-9]*( )*/( )*kg( )*(/)?"
                gRE = "\$[0-9]+((\.| )[0-9]+)?( )*/[0-9]+( )*[Gg]"
                limitRE = "LIMIT( )*[0-9]+( )*AFTER LIMIT( )*\$[0-9]*(\.| )[0-9]*( )*(EA(\.|CH))?"
                xforyRE = "[0-9]+( )*/( )*\$[0-9]+((\.| )[0-9]+)?"
                eachRE = '\$[0-9]+((\.| )[0-9]+)?( )*(ea(\.|ch))'
                priceRE = "((\$[0-9]+)|([0-9]+¢))((\.| )[0-9]+)?(( )*(ea(\.|ch)))?"
                
            logger.logInfo("Opening " + provinces[provIdx] + " city list for " + self.store_name)
            driver.get(provinceLink)
            time.sleep(8)
            # get list columns of stores
            cityLists = driver.find_elements_by_xpath(".//div[@class='content']//div[@class='column-layout col-4']//div")
            cityURLs = []

            logger.logInfo("Getting urls for each city...")
            # extracts the urls for each city
            for cityList in cityLists:
                urls = cityList.find_elements_by_xpath(".//ul[@class='store-select']//li//a")
                for url in urls:
                    cityURLs.append(str(url.get_attribute("href").encode('ascii', 'ignore')))
            logger.logInfo("Going through each city and store, opening flyers...")
            # goes through each city, opens each store's flyers
            
            for url in cityURLs:
                logger.logInfo("Opening store link: " + url)
                # open link to city's page
                driver.get(url)
                time.sleep(8)
                tries = 0
                while tries <= 5:
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
                        logger.logError("unequal number of view flyer buttons, names of stores, addresses, and store numbers")
                        logger.logError("flyer buttons: " + str(len(viewFlyerButtons)) + "  names: " + str(len(names)) +\
                                        "  addresses: " + str(len(addresses)) + "  store numbers: " + str(len(storeNumberElements)))
                        logger.logError("retrying... " + str(tries) + " of 5")
                        tries += 1
                        driver.refresh()
                        time.sleep(8)
                        continue
                    break
                if tries >= 5:
                    raise Exception("exiting due to error in parsing")

                # get all the store 'view flyer' urls from the buttons as well as each store's info
                for i in range(len(viewFlyerButtons)):
                    viewFlyerLinks.append(str(viewFlyerButtons[i].get_attribute("href").encode('ascii', 'ignore')))
                    # store title tag just contains the name
                    self.storeNames.append(str(names[i].text.encode('ascii', 'ignore')))
                    # split the full address by <br> tag
                    fullAddress = str(addresses[i].get_attribute("innerHTML").encode('ascii', 'ignore')).split("<br>")
                    # street name comes first with no special characters
                    address = fullAddress[0]
                    # split on the "no-break space" character that they use to separate the city and postal code
                    cityAndPostal = fullAddress[1].split("&nbsp;")
                    cityAndPostal = [item for item in cityAndPostal if item != ""]
                    # split city and province using the ',' and get rid of leading/trailing whitespace
                    self.storeCities.append(cityAndPostal[0].split(",")[0].strip())
                    self.storeProvinces.append(cityAndPostal[0].split(",")[1].strip())
                    self.storePostalCodes.append(cityAndPostal[1].replace(" ", ""))
                    # get the store number
                    self.storeNumbers.append(str(storeNumberElements[i].get_attribute("data-store-number").encode('ascii', 'ignore')))
                    self.storeAddresses.append(address)

                    
                for idx, link in enumerate(viewFlyerLinks):
                    logger.logInfo("Opening flyer for store: " + self.storeNames[storeCount] + "...")
                    # open specific store's flyer
                    tries = 0
                    while tries <= 5:
                        try:
                            driver.get(link)
                            time.sleep(8)
                        except:
                            logger.logError("Failed to open store flyer")
                            logger.logError("Retrying... " + str(tries) + " of 5")
                            driver.refresh()
                            time.sleep(8)
                            tries += 1
                    if tries >= 5:
                        logger.logError("Skipping store")
                        continue
                    logger.logInfo("Opening accessibility view...")
                    tries = 0
                    while tries <= 5:
                        try:
                            # go to accessibility view
                            driver.find_element_by_xpath("//ul[@class='sort-options tab-layout tabs-3']//li//a[@class='accessible-view']").click()
                            time.sleep(8)
                            break
                        except:
                            logger.logError("Failed to open accessible view")
                            logger.logError("Retrying... " + str(tries) + " of 5")
                            driver.refresh()
                            time.sleep(8)
                            tries += 1
                    if tries >= 5:
                        logger.logError("\n\nUnable to open accessible view for store: " + self.storeNames[storeCount])
                        logger.logError("Skipping store...\n\n")
                        #TODO: raise some sort of alarm but don't quit program
                        storeCount += 1
                        continue
                    logger.logInfo("Getting product info...")
                    try:
                        # get all html elements that have product info
                        tries = 0
                        while tries <= 5:
                            try:
                                driver.switch_to_frame(driver.find_element_by_xpath("//iframe[@id='videoFrame']"))
                                break
                            except:
                                logger.logError("Failed to switch to frame")
                                logger.logError("Retrying... " + str(tries) + " out of 5")
                                driver.refresh()
                                time.sleep(8)
                                tries += 1
                        if tries >= 5:
                            logger.logError("Unable to switch to frame for store: " + self.storeNames[storeCount])
                            logger.logError("Skipping store...\n\n")
                            storeCount += 1
                            continue
                        #print(driver.page_source.encode('utf-8', 'ignore'))
                        elements = driver.find_elements_by_xpath(".//div[@id='content']//table//tbody//tr")
                        if len(elements) == 0:
                            raise Exception("could not find elements")
                            
                        items = []
                        # iterate over each product
                        for i in range(len(elements)):
                            element = elements[i]
                            if re.search("Page [0-9]", element.text) is not None:
                                i += 1
                                products = elements[i].find_elements_by_xpath(".//table")
                                for product in products:
                                    product = product.find_elements_by_xpath(".//tbody/tr")
                                    name = product[0].text.encode('utf-8', 'ignore')
                                    price = ""
                                    quantity = "1"
                                    weight = ""
                                    limit = ""
                                    each = ""
                                    additionalInfo = ""
                                    points = ""
                                    promotion = ""
                                    productInfo = product[1].text.encode('utf-8', 'ignore').replace("\n", " ")
                                    
                                    # remove 'SAVE $x' from the info, not needed
                                    findSave = re.search(saveRE, productInfo)
                                    if findSave is not None:
                                        productInfo = productInfo[:findSave.start()].strip()
                                        promotion = productInfo[findSave.start():].strip()

                                    # check for '$x dozen' - usually used for flowers
                                    findDozen = re.search(dozenRE, productInfo.upper())
                                    if findDozen is not None:
                                        price = productInfo[findDozen.start():findDozen.end()].upper().replace("DOZEN", "").strip()
                                        quantity = "12"
                                        productInfo = productInfo.replace(productInfo[findDozen.start():findDozen.end()], "").strip()
                                    
                                    # get the 'less than x $y each' deals
                                    findLessThan = re.search(lessThanRE, productInfo.upper())
                                    if findLessThan is not None:
                                        split = productInfo[findLessThan.start():findLessThan.end()].split("$")
                                        each = "$" + split[1].replace("each", "").replace("ea.", "").strip().replace(" ", ".")
                                        productInfo = productInfo.replace(productInfo[findLessThan.start():findLessThan.end()], "").strip()

                                    # get '2/$x or $y each" deals
                                    findOr = re.search(orRE, productInfo.upper())
                                    if findOr is not None:
                                        split = productInfo[findOr.start():findOr.end()].upper().split("OR")
                                        quantityPriceSplit = split[0].split("/")
                                        quantity = quantityPriceSplit[0].strip()
                                        price = quantityPriceSplit[1].strip()
                                        each = split[1].replace("EACH", "").replace("EA.", "").strip().replace(" ", ".")
                                        productInfo = productInfo.replace(productInfo[findOr.start():findOr.end()], "").strip()
                                        promotion = str(quantity) + " for " + str(price) + " or " + str(each) + " each"

                                    # get weight unit of product - prioritize lb, but if only kg then use that
                                    # and take it out of the product info
                                    findLb = re.search(lbRE, productInfo)
                                    if findLb is not None:
                                        price = productInfo[findLb.start():findLb.end()].split("lb")[0].lower().replace("ea.", "").replace("/", "").strip()
                                        weight = "lb"
                                        productInfo = productInfo.replace(productInfo[findLb.start():findLb.end()], "").strip()
                                    else:
                                        findKg = re.search(kgRE, productInfo)
                                        if findKg is not None:
                                            price = productInfo[findKg.start():findKg.end()].split("kg")[0].replace("/", "").strip()
                                            weight = "kg"
                                            productInfo = productInfo.replace(productInfo[findKg.start():findKg.end()], "").strip()
                                        else:
                                            findG = re.search(gRE, productInfo)
                                            if findG is not None and price == "":
                                                split = productInfo[findG.start():findG.end()].split("/")
                                                # sometimes there is a price /x grams and sometimes price is separate
                                                price = split[0].strip().replace(" ", ".")
                                                weight = split[1].replace(" ", "")
                                                productInfo = productInfo.replace(productInfo[findG.start():findG.end()], "").strip()

                                    # get item limit if applicable and remove from product info
                                    findLimit = re.search(limitRE, productInfo.upper())
                                    if findLimit is not None:
                                        split = productInfo[findLimit.start():findLimit.end()].upper().split("AFTER LIMIT")
                                        limit = split[0][re.search("[0-9]+", split[0]).start():].strip()
                                        each = split[1].replace("EACH", "").replace("EA.", "").strip().replace(" ", ".")
                                        productInfo = productInfo.replace(productInfo[findLimit.start():findLimit.end()], "").strip()

                                    # get 'x/$y' deals
                                    findXForY = re.search(xforyRE, productInfo)
                                    if findXForY is not None:
                                        split = productInfo[findXForY.start():findXForY.end()].split("/")
                                        quantity = split[0].strip()
                                        price = split[1].strip().replace(" ", ".")
                                        productInfo = productInfo.replace(productInfo[findXForY.start():findXForY.end()], "").strip()
                                        promotion = str(quantity) + " for " + str(price)
                                    
                                    # sometimes there are multiple products, make sure we have the 'each' price if it's left
                                    findEach = re.search(eachRE, productInfo)
                                    if findEach is not None and each == "":
                                        each = productInfo[findEach.start():findEach.end()].replace("each", "").replace("ea.", "").strip().replace(" ", ".")
                                        productInfo = productInfo.replace(productInfo[findEach.start():findEach.end()], "").strip()

                                    # lastly get the price, should be the only thing remaining with a price
                                    # 'kg' price might still be there so '$' must be there
                                    findPrice = re.findall(priceRE, productInfo)
                                    if len(findPrice) != 0 and price == "":
                                        logger.logDebug("Using price (last resort)")
                                        min = ""
                                        minStr = ""
                                        for priceMatch in re.finditer(priceRE, productInfo):
                                            priceMatch = productInfo[priceMatch.start():priceMatch.end()].replace("each", "").replace("ea.", "").strip()
                                            logger.logDebug("match: " + priceMatch)
                                            #priceMatch = priceMatch[0]
                                            amount = 0
                                            if "." not in priceMatch and "," not in priceMatch:
                                                if "¢" in priceMatch:
                                                    amount = int(priceMatch.replace("¢", "").strip())
                                                else:
                                                    amount = int(priceMatch.replace("$", "").strip()) * 100
                                            else:
                                                amount = int(priceMatch.replace(".", "").replace(",", "").replace("$", "").replace("¢", "").strip())
                                            
                                            if min == "" or amount < int(min):
                                                min = amount
                                                minStr = priceMatch
                                        price = minStr
                                        if "¢" in price:
                                            price.replace(" ", "")
                                        else:
                                            price.replace(" ", ".")
                                        productInfo = productInfo.replace(minStr, "").strip()

                                    # just in case
                                    if price == "" and each != "":
                                        price = each
                                    elif price == "" and each == "" and promotion != "": # if there's no price and just a savings
                                        productInfo += " " + promotion
                                    
                                    item = Item(name, price, quantity, weight, limit, each, productInfo,
                                                    points, promotion, self.storeNames[storeCount], self.storeAddresses[storeCount],
                                                    self.storeCities[storeCount], self.storeProvinces[storeCount], self.storePostalCodes[storeCount])
                                    logger.logDebug(str(item))
                                    items.append(item.toCSVFormat())
                                    #csvFile.write(item.toCSVFormat() + "\n")

                                    #if weight == "":
                                    #    print("name: " + name + "      price: " + price + "     quantity: " + quantity + "   limit: " + limit + "   each: " + each + "   info: " + productInfo)
                                    #else:
                                    #    print("name: " + name + "      price: " + price + "     weight: " + weight + "   limit: " + limit + "   each: " + each + "   info: " + productInfo)
                                    logger.logDebug("\n")
                                
                                # write the store's items to the csv file
                                with open(csvFileName, 'ab') as f:
                                    csvWrite = csv.writer(f, delimiter=',')
                                    csvWrite.writerows(items)
                        
                        logger.logInfo("Done getting product info for store: " + self.storeNames[storeCount])
                        storeCount += 1
                        #exit()



                        driver.switch_to_default_content()
                    except Exception as e:
                        # print exception message and break from loop since we've gone through all the pages
                        logger.logError(str(e))
        driver.quit()
        #csvFile.close()
