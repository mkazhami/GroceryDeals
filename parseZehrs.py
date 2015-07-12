from selenium import webdriver
import time

# Authors: e4 + m7
#
# this program will go through all pages of the zehrs flyer and grab the info for each product
#
# requires selenium (and python obviously) to be installed - selenium can be installed through 'pip install selenium'
# assuming you have the pip installer




# opens web browser
driver = webdriver.Firefox()
# go to the list page of all stores in ontario
driver.get("http://www.zehrs.ca/en_CA/store-list-page.ON.html")
# let javascript load
time.sleep(5)
# get list columns of stores
cityLists = driver.find_elements_by_xpath(".//div[@class='content']//div[@class='column-layout col-4']//div")
cityURLs = []
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
    # get all the store 'view flyer' urls from the buttons
    for button in viewFlyerButtons:
        viewFlyerLinks.append(str(button.get_attribute("href").encode('ascii', 'ignore')))

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
                    print(cleanPrice)
                    print(str((name.text).encode('ascii', 'ignore')) + "     " + str((price.text).encode('ascii', 'ignore')))

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

# close the web browser
driver.close()
