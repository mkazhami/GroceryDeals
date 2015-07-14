from selenium import webdriver
import time




driver = webdriver.Firefox()
driver.get("http://www.foodbasics.ca/en/flyer.html#resultat")
time.sleep(3)


flyerFrame = driver.find_element_by_id('flyerFrame')
flyerFrameSrc = str(flyerFrame.get_attribute('src').encode('ascii', 'ignore'))
driver.get(flyerFrameSrc)
#print(str((button.get_attribute('src').encode('ascii', 'ignore'))))
#detectLocation = driver.find_element(by='id', value='btnGeoIP')
#detectLocation.click()
time.sleep(3)



driver.close()
