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
driver = webdriver.PhantomJS(executable_path="../phantomjs.exe", service_log_path=os.path.devnull)
driver.set_window_size(1400,1000)
#driver = webdriver.Firefox()
# go to the list page of all stores in ontario
driver.get("http://www.zehrs.ca/en_CA/store-list-page.ON.html")
# let javascript load
time.sleep(5)
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
    time.sleep(10)
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
        
        print("\n\n\nname       " + str(names[i].text.encode('ascii', 'ignore')))
        print("store number  " + str(storeNumberElements[i].get_attribute("data-store-number").encode('ascii', 'ignore')))
        print("address      " + address)
        print("postal code      " + cityAndPostal[1].replace(" ", ""))
        print("city      " + cityAndPostal[0].split(",")[0].strip())
        print("province    " + cityAndPostal[0].split(",")[1].strip())

    # get product info
    for link in viewFlyerLinks:
        # open specific store's flyer
        driver.get(link)
        time.sleep(3)
        # loop will break once the 'next' button is no longer on the screen
        while(True):
            try:
                # get all html blocks/elements on this page that have class name 'card product' - this is where each product is stored
                elements = driver.find_elements_by_xpath(".//div[@class='card product']")
                # iterate over each product
                for element in elements:
                    # get points if applicable
                    pointsAmount = ""
                    try:
                        pointsDiv = element.find_element_by_xpath(".//span[@class='sticker card-points']")
                        if pointsDiv is not None:
                            pointsAmount = pointsDiv.find_element_by_xpath(".//span[@class='amt']")
                            pointsAmount = str((pointsAmount.get_attribute("innerHTML")).encode('ascii', 'ignore'))
                    except Exception as e:
                        pass
                    # get the child html element that contains the details (price and name)
                    div = element.find_element_by_xpath(".//div[@class='footer']//div[@class='details more']")
                    
                    # get the actual child html element that contains the price
                    # could've been done in one step (without getting 'div'), but this way is cleaner
                    price = div.find_element_by_xpath("./p[@class='price']")
                    
                    # quantity is how many for the price - eg. 2 for $5
                    # weight is how much you get for the price
                    # only one of these can be used for a product
                    quantity = "1"
                    weight = ""
                    limit = ""
                    each = ""
                    # additional info is other facts about the product/pricing - start with the 'more' section
                    additionalInfo = str(div.find_element_by_xpath(".//div[@class='more']").get_attribute("innerHTML").encode('ascii', 'ignore'))
                    additionalTag = re.search("<span.*?>", additionalInfo)
                    # sometimes it won't have an additional span tag, check for that
                    if additionalTag is not None:
                        additionalInfo = additionalInfo[additionalTag.end():].replace("</span>", "").strip()
                    additionalInfo = additionalInfo.replace("<br>", "").replace("</br>", "") # remove these tags if possible
                    additionalInfo = additionalInfo.replace("\n", " ")
                    
                    # get the actual child html element that contains the name
                    name = div.find_element_by_xpath("./h3[@class='title']")
                    
                    # clean up the price string - it contains some html tags like <sup>
                    #
                    # this is just used for testing to be able to print the price cleanly,
                    # though could be useful for getting the actual price without the extra html junk
                    # this is super hard-coded but it's unlikely that there's a better way
                    cleanPrice = str((price.get_attribute("innerHTML")).encode('ascii', 'ignore'))
                    cleanPrice = cleanPrice.replace("<sup>$</sup>", "$").replace("<sup>", ".").replace("</sup>", "")
                    
                    # get rid of 'limit of x' text
                    limitX = re.search("LIMIT", additionalInfo)
                    if limitX is not None:
                        limit = additionalInfo[limitX.start():].split("after limit")[0]
                        limit = limit[re.search("LIMIT", limit).end():].strip()
                        each = additionalInfo[limitX.start():].split("after limit")[1]
                        each = each[:re.search("ea(\.|ch)", each).start()].strip()
                        additionalInfo = cleanPrice[limitX.start():] + ",   " +  additionalInfo
                        cleanPrice = cleanPrice[:limitX.start()]
                    # get rid of 'less than x, $y each' text
                    less = re.search("less than [0-9]*", cleanPrice)
                    if less is not None:
                        # get the $y and put into 'each'
                        each = cleanPrice[less.end():]
                        each = each[:re.search("ea(\.|ch)", each).start()].strip()
                        additionalInfo = cleanPrice[less.start():] + ",   " +  additionalInfo
                        cleanPrice = cleanPrice[:less.start()]
                    # change '$x dozen' to '$x' and update quantity
                    dozen = re.search("dozen", cleanPrice)
                    if dozen is not None:
                        cleanPrice = cleanPrice[:dozen.start()]
                        quantity = 12
                    # get the weight that will be used - kg vs lb
                    kg = re.search("kg", cleanPrice)
                    if kg is not None:
                        lb = re.search("lb", cleanPrice)
                        if lb is not None:
                            cleanPrice = cleanPrice[:lb.start()].replace("/", "") # get rid of all slashes too
                            weight = "lb"
                        else:
                            cleanPrice = cleanPrice[:kg.start()].replace("/", "")
                            weight = "kg"
                    # check if weight is in litres
                    litre = re.search("[0-9]*( )?L", cleanPrice)
                    if litre is not None:
                        cleanPrice = cleanPrice[:litre.start()]
                        weight = "L"
                    # check if it's a '2/$x or $y each' type of deal
                    orX = re.search("or", cleanPrice)
                    if orX is not None:
                        orXInfo = cleanPrice[orX.start():]
                        orEachX = re.search("ea(\.|ch)", orXInfo)
                        if orEachX is not None:
                            each = orXInfo[:orEachX.start()].replace("or", "").strip()
                        additionalInfo = cleanPrice[orX.start():] + ",   " + additionalInfo
                        cleanPrice = cleanPrice[:orX.start()]
                    
                    # get rid of $x each, just set quantity to 1 instead
                    eachX = re.search("ea(\.|ch)", cleanPrice)
                    if eachX is not None:
                        cleanPrice = cleanPrice[:eachX.start()]
                        quantity = "1"

                    priceSplit = cleanPrice.split("/")
                    if len(priceSplit) > 1:
                        quantity = priceSplit[0]
                        cleanPrice = priceSplit[1]
                    # clear trailing/leading whitespace
                    cleanPrice = cleanPrice.strip()
	                # print the price (clean version), followed by the html text of the name and price elements (not clean version)
                    # this is just for testing purposes, info will be stored somehow
                    #print(cleanPrice)
                    if weight == "":
                        print(str((name.text).encode('ascii', 'ignore')) + "   price: " + cleanPrice + "    quantity: " + quantity +  "   limit: " + limit + "   each: " + each + "         add. info: " + additionalInfo)
                    else:
                        print(str((name.text).encode('ascii', 'ignore')) + "   price: " + cleanPrice + "    weight: " + weight + "   limit: " + limit + "   each: " + each + "      add. info: " + additionalInfo)
                    #if not pointsAmount == "":
                    #    print(str(name.text.encode('ascii','ignore')) + " gives " + pointsAmount + " points")

                try:
                    # get the 'next' button element if it exists
                    # all this does is go through the html hierarchy to where the 'next page' element is and returns it
                    #
                    # will throw exception if not found - this is fine because we handle it
                    nextButton = driver.find_element_by_xpath(
                        "//section[@class='container']//div[@class='content']//" + 
                        "div[@class='ctrl-wrap']//nav[@class='pagination light-theme" + 
                        " simple-pagination']//ul//li//a[@title='Next Page']")
                    # click it - goes to next page
                    nextButton.click()
                    # sleep to let the javascript for the next page load
                    time.sleep(5)
                except Exception as e:
                    # if exception was thrown, then button does not exist, and we're on the last page
                    # throw another exception to exit the loop
                    raise Exception("\n\nnext button not found - likely finished searching")

            except Exception as e:
                # print exception message and break from loop since we've gone through all the pages
                print(str(e))
            	print("breaking from loop")
                break

for i in range(len(storeNames)):
    print("\n\n\nname:  " + storeNames[i] + "\naddress:  " + storeAddresses[i] + "\ncity:  " + storeCitys[i] + "\nprovince:  "  +
            storeProvinces[i] + "\npostal:  " + storePostalCodes[i] + "\nstore number:  " + storeNumbers[i])
                
# close the web browser
driver.close()
