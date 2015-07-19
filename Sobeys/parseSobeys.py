from selenium import webdriver
import time


driver = webdriver.Firefox()
driver.get("https://www.sobeys.com/en/stores")
time.sleep(8)

zoomOut = driver.find_element_by_xpath(".//div[@title='Zoom out']")
for i in range(8):
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
    driver.get("https://www.sobeys.com/en/stores")
    time.sleep(5)
    zoomOut = driver.find_element_by_xpath(".//div[@title='Zoom out']")
    for i in range(8):
        zoomOut.click()
        time.sleep(0.5)
    try:
        driver.find_element_by_xpath(".//a[@href='" + link + "']").click()
    except:
        driver.find_element_by_xpath(".//a[@href='" + link.split(".com")[1] + "']").click()
    time.sleep(2)
    driver.get("https://www.sobeys.com/en/flyer")
    time.sleep(2)

driver.close()
