from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException 
from selenium import webdriver
from fake_useragent import UserAgent
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import json
import time
import sys
import os.path
 

class WebScraping:
	def __init__(self):
		# Setting webdriver
		options = Options()
		ua = UserAgent()
		options.binary_location = '/usr/bin/brave-browser'
		options.add_argument("--incognito")
		options.add_argument(f'user-agen={ua.random}')
		self.driver = webdriver.Chrome(options = options)
		self.domain = 'https://harddiskdirect.com/'
		self.categories = {}
		self.products_filename = "hardisk_products.json"


	# Start scraping
	def scrap_harddiskdirect(self):
		self.driver.get(self.domain)
		self.driver.maximize_window()
		categories_li = self.driver.find_elements(By.CSS_SELECTOR, 'li[class$="classic"]')
		print("Scraped categories: "+ str(len(categories_li)))
		categories = {}
		for li in categories_li:
			a_li = li.find_element(By.TAG_NAME, 'a')
			a_href = a_li.get_attribute("href")
			a_text = a_li.find_element(By.TAG_NAME, 'span').get_attribute('innerHTML')
			self.categories[a_text] = a_href
		# Scrap products list
		self.get_product_list()


	# Scraping final category product list
	def get_product_list(self):
		for category in self.categories.keys():
			print("Scraping products: "+ category)
			self.driver.get(self.categories[category])
			self.driver.maximize_window()
			end_page = False
			products_url_list = []
			while end_page == False:
				# Scrap products list
				product_elements = self.driver.find_elements(By.CSS_SELECTOR, 'a[class="product photo product-item-photo"]')
				products_url_list += list(map(lambda x: x.get_attribute("href"), product_elements))
				# Check last page
				end_page = self.check_last_page()
				if end_page == False:
					pagination_element = self.driver.find_element(By.CSS_SELECTOR, 'a[title="Next"]')
					self.driver.get(pagination_element.get_attribute("href"))
			# Scrap product
			for product_url in products_url_list:
				self.get_product(product_url, category)
			print("Products scraped")


	# Scraping product data
	def get_product(self, product_url, category_name):
		self.driver.close()
		self.set_driver_options()
		self.driver.get(product_url)
		timeout = 10
		try:
			element_present = EC.presence_of_element_located((By.CSS_SELECTOR,'[class="fotorama__img magnify-opaque magnify-opaque"]'))
			WebDriverWait(self.driver, timeout).until(element_present)
		except TimeoutException:
			pass
		# Title
		if self.check_exists('[data-ui-id="page-title-wrapper"]'):
			title = self.driver.find_element(By.CSS_SELECTOR,'[data-ui-id="page-title-wrapper"]').text
		else: 
			title = ""
		# Price
		if self.check_exists('[class="excl_vat_price"]'):
			price = self.driver.find_element(By.CSS_SELECTOR,'[class="excl_vat_price"]').text
			price = price.replace("$","")
		else: 
			price = ""
		# RRPPrice
		if self.check_exists('[class="old-price"'):
			rrpprice_el = self.driver.find_element(By.CSS_SELECTOR,'[class="old-price"]')
			rrpprice = rrpprice_el.find_element(By.XPATH,'./*')
			rrpprice_text = rrpprice.text.replace("was$ ","")
		else:
			rrpprice_text = ""
		# Description
		if self.check_exists('[class="product attribute description"]'):
			description_div = self.driver.find_element(By.CSS_SELECTOR,'[class="product attribute description"]')
			description_el = description_div.find_element(By.CSS_SELECTOR,'[class="value"]')
			description = description_el.text
		else:
			description = ""
		# Image
		if self.check_exists('[id="magnifier-item-0"]'):
			image_div = self.driver.find_element(By.CSS_SELECTOR,'[id="magnifier-item-0"]')
			image = image_div.get_attribute("src")
		else:
			image = ""
		# Creating product dictionary data
		product_dict = {"name": title, "description": description, "regular_price": rrpprice_text, "sale_price": price,
		"image": image, "url":product_url, "category":category_name} 
		self.write_product_to_file(product_dict)


	# Writing product to file
	def write_product_to_file(self, product_dict):
		data = []
		if os.path.isfile("./"+self.products_filename):
			pass
		else:
			# Write json file
			with open(self.products_filename, "w") as file:
				json.dump(data, file, indent=4)

		# Read file contents
		with open(self.products_filename, "r") as file:
			data = json.load(file)
			# Update json object
			data.append(product_dict)
		# Write json file
		with open(self.products_filename, "w") as file:
			json.dump(data, file, indent=4)


	# Checking if it is last page od product list
	def check_last_page(self):
		div_pages = self.driver.find_elements(By.CSS_SELECTOR, 'span[class="toolbar-number"]')
		txt_page = [div_page.text for div_page in div_pages]
		actual = txt_page[1]
		last = txt_page[2]
		if actual == last:
			return True
		else:
			return False

	# Reset driver to avoid web blocking
	def set_driver_options(self):
		# Setting webdriver
		options = Options()
		ua = UserAgent()
		options.binary_location = '/usr/bin/brave-browser'
		options.add_argument("--incognito")
		options.add_argument(f'user-agen={ua.random}')
		self.driver = webdriver.Chrome(options = options)


	# Checking if DOM element class exists
	def check_exists(self, class_name):
	    try:
	        self.driver.find_element(By.CSS_SELECTOR, class_name)
	    except NoSuchElementException:
	        return False
	    return True


if __name__ == "__main__":
	web_scrap = WebScraping()
	web_scrap.scrap_harddiskdirect()
