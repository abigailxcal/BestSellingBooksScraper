import csv
import random
import time
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from Category import Category


class Amazon_Scraper:

    PATH_TO_DRIVER = Service('/Users/abigailcalderon/Downloads/chromedriver-mac-arm64/chromedriver')

    def __init__(self, url) -> None:
        self.driver = webdriver.Chrome(service=self.PATH_TO_DRIVER)
        self.url = url

    def scroll(self): 
        SCROLL_PAUSE_TIME = 1
        last_height = self.driver.execute_script("return document.body.scrollHeight")    # get height of first scroll
        while True:

            # why does it say scrollheight-1000? is it bc if u scroll all the way to the bottom, it doesn't scroll infinitely?
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight-1000);")  
            time.sleep(SCROLL_PAUSE_TIME)

            # get height of new scroll 
            new_height = self.driver.execute_script("return document.body.scrollHeight")     
            if new_height == last_height:
                break
            last_height = new_height
    
    #accesses given url and creates/returns soup object
    # RENAME THIS
    def parse_url_content(self, url=None):  
        '''
        when called, throw it in a try except block 
        '''
        if url is None:
            url = self.url
        self.driver.get(url)
        self.scroll()
        time.sleep(random.randint(0, 2))    #redundant? 
        soup = BeautifulSoup(self.driver.page_source, 'html.parser')
        return soup

    # returns list category html info for each url 
    def extract_categories(self,soup):  
        html_categories = soup.find_all('div', {'class': '_p13n-zg-nav-tree-all_style_zg-browse-item__1rdKf _p13n-zg-nav-tree-all_style_zg-browse-height-large__1z5B8'})  # list of category results
        #print("html categories: ", html_categories)
        del html_categories[0]  # delete the first result because it is not a "category"
        return html_categories
    
    
    # turns realtive URL into absolute URL 
    def clean_url(self, html_category):
        a_tag = html_category.find('a')  # find the 'a' tag (provides category name and part of the category URL),
        category_url = 'https://www.amazon.com' + a_tag.get('href')
        print("URL: ", category_url)
        return category_url
    
    def get_category_name(self, html_category):
        a_tag = html_category.find('a').text
        print("Category name: ", a_tag)
        return a_tag

    # don't need anymore 
    def extract_books(self, soup):
        book_results = soup.find_all('div', {'id': 'gridItemRoot'})  # create a list of all HTML code that represents a book listing
        #print("extract_books: ", book_results)
        return book_results
    
    def get_book_titles(self,soup):
        book_titles = []
        book_results = soup.find_all('div', {'id': 'gridItemRoot'})
        for book in book_results:
            book_titles.append(book.div.a.img.get('alt'))
        print(book_titles)
        return book_titles

    def extract_subcategories(self,soup):
        subcategories = soup.find_all('div', {'class': '_p13n-zg-nav-tree-all_style_zg-browse-item__1rdKf _p13n-zg-nav-tree-all_style_zg-browse-height-large__1z5B8'})
        if subcategories and 'span' in str(subcategories[0]):
            return subcategories[1:]
        return subcategories
    
    def quit_driver(self):
        self.driver.quit()

# SIMPLY MORE 
def main():
    url = 'https://www.amazon.com/gp/bestsellers/books/ref=zg_bs_nav_0'
    scraper = Amazon_Scraper(url)
    soup = scraper.parse_url_content()
    #soup.find_all('div', {'class': '_p13n-zg-nav-tree-all_style_zg-browse-item__1rdKf _p13n-zg-nav-tree-all_style_zg-browse-height-large__1z5B8'})
    category_list = scraper.extract_categories(soup)  #extracts html info of categories of first page 
    category_url_list=[]
    
    for category in category_list:
        print("*******CATEGORY********")
        #category_url_list.append(scraper.clean_url(category))
        category_url = scraper.clean_url(category)   # go to each link of category list
        soup = scraper.parse_url_content(category_url)   #parse the data of each category url
        name = scraper.get_category_name(category)
        new_category_obj = Category(name,category_url)
        bestsellers = scraper.get_book_titles(scraper.extract_books(soup))
        new_category_obj.set_best_selling_books(bestsellers)
        
        subcategory_list = scraper.extract_categories(soup)
        print("\t\tSUBCATEGORY: ",subcategory_list[0])
        while (str(subcategory_list[0])).find('span') != -1:
            del subcategory_list[0]
            for subcategory in subcategory_list:
                
                subcategory_url = scraper.clean_url(subcategory)
                soup = scraper.parse_url_content(subcategory_url)
                subcategory_name = scraper.get_category_name(subcategory)
                print("\tSubcategory: ", subcategory_name)
                subcategory_obj = Category(subcategory_name,subcategory_url)
                subcategory_bestsellers = scraper.get_book_titles(scraper.extract_books(soup))
                subcategory_obj.set_best_selling_books(subcategory_bestsellers)
            

if __name__ == '__main__':
    main()