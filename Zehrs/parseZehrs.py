from selenium import webdriver
import time
import os

# Authors: e4 + m7
#
# this program will go through all pages of the zehrs flyer and grab the info for each product
#
# requires selenium (and python obviously) to be installed - selenium can be installed through 'pip install selenium'
# assuming you have the pip installer




# opens phantom browser
# phantomjs.exe is located in the root directory
#driver = webdriver.PhantomJS(executable_path="../phantomjs.exe", service_log_path=os.path.devnull)
#driver.set_window_size(1400,1000)
driver = webdriver.Firefox()
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

    # get all the store 'view flyer' urls from the buttons
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

    continue # FOR TESTING, REMOVE LATER!
        
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
                    # get the actual child html element that contains the name
                    name = div.find_element_by_xpath("./h3[@class='title']")
                    # clean up the price string - it contains some html tags like <sup>
                    #
                    # this is just used for testing to be able to print the price cleanly,
                    # though could be useful for getting the actual price without the extra html junk
                    # this is super hard-coded but it's unlikely that there's a better way
                    cleanPrice = str((price.get_attribute("innerHTML")).encode('ascii', 'ignore'))
                    cleanPrice = cleanPrice.replace("<sup>$</sup>", "$").replace("<sup>", ".").replace("</sup>", "")
	            # print the price (clean version), followed by the html text of the name and price elements (not clean version)
                    # this is just for testing purposes, info will be stored somehow
                    #print(cleanPrice)
                    #print(str((name.text).encode('ascii', 'ignore')) + "     " + str((price.text).encode('ascii', 'ignore')))
                    if not pointsAmount == "":
                        print(str(name.text.encode('ascii','ignore')) + " gives " + pointsAmount + " points")

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
