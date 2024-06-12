import json
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
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight-1000);")  
            time.sleep(SCROLL_PAUSE_TIME)
            # get height of new scroll 
            new_height = self.driver.execute_script("return document.body.scrollHeight")     
            if new_height == last_height:
                break
            last_height = new_height
    
    #accesses given url and creates/returns soup object
    def parse_url_content(self, url=None):  
        if url is None:
            url = self.url
        self.driver.get(url)
        self.scroll()
        time.sleep(random.randint(0, 2))    #redundant? 
        soup = BeautifulSoup(self.driver.page_source, 'html.parser')
        return soup

    # returns list of category html info for each url 
    def extract_categories(self,soup):  
        html_categories = soup.find_all('div', {'class': '_p13n-zg-nav-tree-all_style_zg-browse-item__1rdKf _p13n-zg-nav-tree-all_style_zg-browse-height-large__1z5B8'})  # list of category results
        del html_categories[0]  # delete the first result because it is not a "category"
        return html_categories
    
    # returns list of all category urls that have been extracted from parser 
    def get_category_url(self,html_category):
        a_tag = html_category.find('a')
        url = 'https://www.amazon.com' + a_tag.get('href')    
        return url

    def get_category_name(self, html_category):
        a_tag = html_category.find('a').text
        return a_tag
    
    def get_book_titles(self,soup):
        book_titles = []
        book_results = soup.find_all('div', {'id': 'gridItemRoot'})
        for book in book_results[:10]:
            book_titles.append(book.div.a.img.get('alt'))
        print(book_titles)
        return book_titles

    def extract_subcategories(self,soup):
        subcategories = soup.find_all('div', {'class': '_p13n-zg-nav-tree-all_style_zg-browse-item__1rdKf _p13n-zg-nav-tree-all_style_zg-browse-height-large__1z5B8'})
        if subcategories and 'span' in str(subcategories[0]):
            return subcategories[1:]
        return subcategories
    
    def create_subcategory_object(self, html_subcategory):
        subcat_name = self.get_category_name(html_subcategory)
        subcat_url = self.get_category_url(html_subcategory)
        subcategory = Category(subcat_name,subcat_url)
        try: 
            subcat_soup = self.parse_url_content(subcat_url)
            subcategory.add_best_selling_books(self.get_book_titles(subcat_soup))
            other_subcategories = self.extract_subcategories(subcat_soup) 
            #if the subcateogry contains more subcategories 
            if len(other_subcategories)!= 0:    
                for subcat in other_subcategories:
                    new_subcategory = self.create_subcategory_object(subcat)
                    if new_subcategory:
                        subcategory.add_subcategory(subcategory)
            return subcategory
        
        except Exception as e:
            print(f"Error accessing subcategory {subcat_name}: {e}")
            return None


    def create_category_object(self,html_category):
        name = self.get_category_name(html_category)
        url = self.get_category_url(html_category)
        category = Category(name,url)
        try: 
            category_soup = self.parse_url_content(url)
            category.add_best_selling_books(self.get_book_titles(category_soup))
            html_subcategories = self.extract_subcategories(category_soup)
            for subcat in html_subcategories:
                subcategory = self.create_subcategory_object(subcat)
                if subcategory:
                    category.add_subcategory(subcategory)
        except Exception as e:
            print(f"Error accessing {name}: {e}")
        return category
    
    # def write_categories_to_csv(self, categories, filename):
    #     """Write categories and their details to a CSV file."""
    #     with open(filename, 'w', newline='') as file:
    #         writer = csv.writer(file)
    #         writer.writerow(['Category', 'Bestselling Books', 'Subcategory', 'Subcategory Bestselling Books'])
    #         for category in categories:
    #             writer.writerow([category.name, ', '.join(category.books)])
    #             for subcategory in category.subcategories:
    #                 writer.writerow(['', '', subcategory.name, ', '.join(subcategory.books)])

    def write_categories_to_json(self, categories, filename):
        """Write categories and their details to a JSON file."""
        with open(filename, 'w') as file:
            json.dump([category.to_dict() for category in categories], file, indent=4)

    def quit_driver(self):
        self.driver.quit()


def main():
    url = 'https://www.amazon.com/gp/bestsellers/books/ref=zg_bs_nav_0'
    scraper = Amazon_Scraper(url)
    soup = scraper.parse_url_content()
    categories = []
    category_htmls = scraper.extract_categories(soup)  #extracts html info of categories of first page 
    for category_html in category_htmls[:5]:
        category = scraper.create_category_object(category_html)
        categories.append(category)
    scraper.write_categories_to_csv(categories, 'amazonCategoriesUpdates.csv')
    scraper.quit_driver()


if __name__ == '__main__':
    main()
