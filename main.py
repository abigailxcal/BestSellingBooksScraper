
import csv
import random
import time
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
import SubCategory
import Category
import BestSeller



# from X import Y imports Y from module X
# import Y imports all of Y 


# handles infinite scrolling
## deals with webdriver
def scroll(): 
    SCROLL_PAUSE_TIME = 5
    last_height = driver.execute_script("return document.body.scrollHeight")    # get height of first scroll
    while True:

        # why does it say scrollheight-1000? is it bc if u scroll all the way to the bottom, it doesn't scroll infinitely?
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight-1000);")  
        time.sleep(SCROLL_PAUSE_TIME)

        # get height of new scroll 
        new_height = driver.execute_script("return document.body.scrollHeight")     
        if new_height == last_height:
            break
        last_height = new_height


category_list = []
url = 'https://www.amazon.com/gp/bestsellers/books/ref=zg_bs_nav_0'

# path to chromedriver executable
s = Service('/Users/abigailcalderon/Downloads/chromedriver-mac-arm64/chromedriver')
driver = webdriver.Chrome(service=s)
driver.get(url)
scroll()
soup = BeautifulSoup(driver.page_source, 'html.parser') #html parser 
html_categories = soup.find_all('div', {'class': '_p13n-zg-nav-tree-all_style_zg-browse-item__1rdKf _p13n-zg-nav-tree-all_style_zg-browse-height-large__1z5B8'})  # list of category results
del html_categories[0]  # delete the first result because it is not a "category"

## first for loop: goes to each category URL and (tries to) create a category object 
for results in range(len(html_categories)-29):  # for every category result in HTML,
    atag = html_categories[results].find('a')  # find the 'a' tag (provides category name and part of the category URL),
    categoryURL = 'https://www.amazon.com' + atag.get('href')
    category_name = atag.text
    category = Category(category_name)           # create Category Object and set name, PUT TOWARDS END OF LOOPS???
    try:
        driver.get(categoryURL)     # go to category URL,
        scroll()
        time.sleep(random.randint(0, 5))    #redundant? 
        soup = BeautifulSoup(driver.page_source, 'html.parser')
    except Exception:
        print("Could not access category url")
        print(categoryURL)
        continue
    book_results = soup.find_all('div', {'id': 'gridItemRoot'})  # create a list of all HTML code that represents a book listing
    print("Category : " + str(category_name))


    for b in range(len(book_results)):   # add to categoryObj's list of Category Books
        categoryObj.set_category_books(book_results[b].div.a.img.get('alt'))
    # create list of HTML code that represents the subcategories
    sub_results = soup.find_all('div', {'class': '_p13n-zg-nav-tree-all_style_zg-browse-item__1rdKf _p13n-zg-nav-tree-all_style_zg-browse-height-large__1z5B8'})
    string_sub = str(sub_results[0])
    span_idx = string_sub.find('span')
    if span_idx != -1:  # check if the first item in the list contains the 'span' tag
        del sub_results[0]  # delete the span tag item because it does not represent a subcategory

        for s in range(len(sub_results)):  # for the other subcategories found
            try:
                subcategoryObj = SubCategory(sub_results[s].find('a').text)  # create subcategory object and set name
                print("subcategoryObj: " + str(subcategoryObj.get_subcategory_name()) + " has been accessed")
                sub_url = 'https://www.amazon.com' + sub_results[s].find('a').get('href')  # try to get the subcategory URL
                driver.get(sub_url)
                scroll()
                time.sleep(random.randint(0, 5))
                soup = BeautifulSoup(driver.page_source, 'html.parser')
                # if the header for the subcategory is clickable, then that means there are no subcategories
                sub_book_results = soup.find_all('div', {'id': 'gridItemRoot'})
                for sb in range(len(sub_book_results)):
                    sBook = sub_book_results[sb]
                    atag = sBook.div.a
                    subcategoryObj.set_subcategory_books(atag.img.get('alt'))  # set subcategory books
            except Exception:
                print("subcategoryObj: " + str(subcategoryObj.get_subcategory_name()) + " NOT accessed")
                categoryObj.set_subcategories(None)
                continue
            categoryObj.set_subcategories(subcategoryObj)
    else:
        # if the first item in subcategory list does not contain 'span', then the category does not have subcategories
        categoryObj.set_subcategories(None)
    categoryObjectsList.append(categoryObj)


with open('amazonCategoriesUpdates.csv', 'w', newline='') as k:
    thewriter = csv.writer(k)
    thewriter.writerow(['Categories/Subcategories and Their Bestselling Books'])

    for m in range(len(categoryObjectsList)):
        thewriter.writerow(
            ['Category: ' + str(categoryObjectsList[m].get_category_name()), " Bestselling Books: " + str(categoryObjectsList[m].get_category_books())])

        for n in categoryObjectsList[m].get_subcategories():
            if n is None:
                print("No Subcategories/No Books")
                continue
            thewriter.writerow(['      Subcategory: ' + str(n.get_subcategory_name()), " Bestselling Books: " + str(n.get_subcategory_books())])

            # print('      Subcategory: ' + str(n.get_subcategory_name()))
            # print("      Bestselling Books: " + str(n.get_subcategory_books()))
            # print('      Subcategory Size:' + str(len(n.get_subcategory_books())))

