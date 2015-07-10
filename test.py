from selenium import webdriver
import time

driver = webdriver.Firefox()
driver.get("http://www.zehrs.ca/en_CA/flyers.banner@ZEHRS.storenum@550.html")
time.sleep(5)
try:
	elements = driver.find_elements_by_xpath("//div[@class='card product']")
	for element in elements:
		print(str((element.text).encode('ascii', 'ignore')))
	#print(str((driver.page_source).encode('utf-8')))
except Exception as e:
	print(str(e))

driver.close()