class Category:    # class that contains name, bestselling books, and subcategory (as objects)  of each category

    def __init__(self, name, url):
        self.best_selling_books = []
        self.subcategories = []
        #self.subcategoryObjectList = subcategories
        self.categoryName = name
        self.category_url = url

    def get_name(self):
        return self.categoryName
    
    def set_url(self,url):
        self.category_url = url

    def get_url(self):
        return self.category_url

    def set_best_selling_books(self, books):
        self.best_selling_books = books

    def best_selling_books(self):
        return self.best_selling_books

    def add_subcategories(self, subcategory_object):
        self.subcategories.append(subcategory_object)

    def get_subcategories(self):
        return self.subcategories