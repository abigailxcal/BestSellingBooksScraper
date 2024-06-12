class Category:    # class that contains name, bestselling books, and subcategory (as objects) of each category

    def __init__(self, name, url):
        self.best_selling_books = []
        self.subcategories = []
        self.category_name = name
        self.category_url = url

    def get_name(self):
        return self.category_name
    
    def set_url(self,url):
        self.category_url = url

    def get_url(self):
        return self.category_url

    def add_best_selling_books(self, books):
        self.best_selling_books = books

    def get_best_selling_books(self):
        return self.best_selling_books

    def add_subcategory(self, subcategory):
        self.subcategories.append(subcategory)

    def get_subcategories(self):
        return self.subcategories