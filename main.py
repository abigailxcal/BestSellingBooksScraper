import json
import time
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from Category import Category



class Amazon_Scraper:
    PATH_TO_DRIVER = Service('/opt/homebrew/bin/chromedriver')
    def __init__(self, url) -> None:
        self.driver = webdriver.Chrome(service=self.PATH_TO_DRIVER)
        self.url = url

    # scrolls to bottom of page to load all web content
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
    def get_soup(self, url=None):  
        if url is None:
            url = self.url
        self.driver.get(url)
        self.scroll()
        soup = BeautifulSoup(self.driver.page_source, 'html.parser')
        return soup

    # returns list of category html info for each url 
    def extract_category_elements(self,soup):  
        category_element = soup.find_all('div', 
                                         {'class': '_p13n-zg-nav-tree-all_style_zg-browse-item__1rdKf _p13n-zg-nav-tree-all_style_zg-browse-height-large__1z5B8'})  # list of category results
        del category_element[0]  # delete the first result because it is not a "category"
        return category_element
    
    # returns list of all category urls that have been extracted from parser 
    def get_category_url(self,category_element):
        a_tag = category_element.find('a')   
        return 'https://www.amazon.com' + a_tag.get('href')   

    def get_category_name(self, category_element):
        return category_element.find('a').text
    
    def get_book_titles(self,soup):
        book_results = soup.find_all('div',{'class': '_cDEzb_p13n-sc-css-line-clamp-1_1Fn1y'})
        return [book.get_text() for book in book_results[:10]]
    

    def extract_subcategory_elements(self,soup,subcat_name = None):
        group_div = soup.find('div', {
            'role': 'group',
            'class': '_p13n-zg-nav-tree-all_style_zg-browse-group__88fbz'})
        if group_div:
            subcategory_elements = group_div.find_all('div', recursive=True)
            if subcat_name is not None:
                for elem in subcategory_elements:
                    if subcat_name and 'span' in str(elem):
                        return []
            return subcategory_elements
        return []
                    
                
    
    # create and return a subcategory object
    def create_subcategory(self, subcategory_element):
        subcategory_name = self.get_category_name(subcategory_element)
        subcategory_url = self.get_category_url(subcategory_element)
        subcategory = Category(subcategory_name, subcategory_url)
        try: 
            #print("Subcategory Name: ", subcategory_name)
            subcat_soup = self.get_soup(subcategory_url)
            subcategory.add_best_selling_books(self.get_book_titles(subcat_soup))
            nested_subcategories = self.extract_subcategory_elements(subcat_soup, subcategory_name)

            #if the subcateogry contains more subcategories 
            if len(nested_subcategories) != 0:  
                #print(subcategory_name, " has ", (len(nested_subcategories)), " many subcategories")
                for nested_subcat_element in nested_subcategories:
                    #print(subcategory_name,"'s subcategory: ",self.get_category_name(nested_subcat_element) )
                    #print("nested_subcat_element: ", nested_subcat_element)
                    nested_subcategory = self.create_subcategory(nested_subcat_element)
                    if nested_subcategory:
                        subcategory.add_subcategory(nested_subcategory)  
            return subcategory

        except Exception as e:
            print(f"Error accessing subcategory {subcategory_name}: {e}")
            return None
        

    
    #create and return category object
    def create_category(self,category_element):
        category_name = self.get_category_name(category_element)
        #print("Category Name: ", category_name)
        category_url = self.get_category_url(category_element)
        category = Category(category_name,category_url)
        try: 
            category_soup = self.get_soup(category_url)
            category.add_best_selling_books(self.get_book_titles(category_soup))
            subcategory_elements = self.extract_subcategory_elements(category_soup)
            #print(category_name," has ", (len(subcategory_elements)), " many subcategories")
            for subcategory_element in subcategory_elements[:5]:    #LIMIT
                subcategory = self.create_subcategory(subcategory_element)
                if subcategory:
                    category.add_subcategory(subcategory)
        except Exception as e:
            print(f"Error accessing {category_name}: {e}")
        return category

    # write categories and their details to a JSON file
    def write_categories_to_json(self, categories, filename):
        with open(filename, 'w') as file:
            json.dump([category.to_dict() for category in categories], file, indent=4)

    def quit_driver(self):
        self.driver.quit()


def main():
    base_url = 'https://www.amazon.com/gp/bestsellers/books/ref=zg_bs_nav_0'
    scraper = Amazon_Scraper(base_url)
    soup = scraper.get_soup()


    categories = []
    category_htmls = scraper.extract_category_elements(soup)  #extracts html info of categories of first page 
    for category_html in category_htmls[:2]:
        category = scraper.create_category(category_html)
        categories.append(category)
    scraper.write_categories_to_json(categories, 'amazon_bestselling_books.json')
    scraper.quit_driver()


if __name__ == '__main__':
    main()



