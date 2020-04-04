# OBJECTIVE:
# Web-scrapper to look at house auction dates coming up in CT within one week of running the program

import requests, webbrowser
import bs4
from datetime import date
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
import pprint
import datetime
import datetime as DT
import time


# Edit towns from this list:
list_town = ['Milford', 'Norwalk', 'Stamford', 'Fairfield', 'Trumbull'] # Missing Shelton

# list_town = ['Trumbull']


# Converts + sees if auction is within the upcoming week
def comp_dates(date_str):
	format_str = '%m/%d/%Y'
	datetime_obj = datetime.datetime.strptime(date_str, format_str) #2020-03-14
	one_week = datetime.datetime.now() + DT.timedelta(days=7)
	if datetime_obj <= one_week and datetime_obj >= datetime.datetime.now():
		return True
	else:
		return False


# Opens a new window for each town
for b in list_town:
	driver = webdriver.Chrome("C:/Users/Taniya/AppData/Local/Programs/Python/Python37/Selenium/chromedriver.exe")  # Optional argument, if not specified will search path.
	driver.get('https://sso.eservices.jud.ct.gov/Foreclosures/Public/PendPostbyTownList.aspx')
	time.sleep(5)
	try:
		driver.find_element_by_partial_link_text(b).click()
		test = driver.find_elements_by_xpath('/html/body/form/table/tbody/tr[2]/td/table/tbody/tr[4]/td/div/table/tbody/tr')


	# Opens auction page if date is within the next week
		for a in range(2,len(test)+1): # range = number of rows in a table - 1
			date_matching = driver.find_element_by_xpath('/html/body/form/table/tbody/tr[2]/td/table/tbody/tr[4]/td/div/table/tbody/tr[{index}]/td[2]/span'.format(index=a))
			date_time = (date_matching.text)
			date_only = date_time[:10] # pulls date text
			if comp_dates(date_only):
				geshu = driver.find_element_by_xpath('/html/body/form/table/tbody/tr[2]/td/table/tbody/tr[4]/td/div/table/tbody/tr[{index}]/td[5]/a'.format(index=a))
				time.sleep(5)
				# Opens link from last column "View Full Notice" in a new tab
				ActionChains(driver) \
				    .key_down(Keys.CONTROL) \
				    .click(geshu) \
				    .key_up(Keys.CONTROL) \
				    .perform()

	except:
		print ('Could not find {town}'.format(town=b) )
print('Search completed!')
