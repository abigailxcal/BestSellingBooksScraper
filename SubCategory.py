
class SubCategory:  # class that contains name and bestselling books of each subcategory

    def __init__(self, name, best_sellers):
        self.subcategoryBooks = []
        self.subcategoryName = name
        self.best_sellers = best_sellers

    def set_subcategory_name(self, name):
        self.subcategoryName = name

    def get_subcategory_name(self):
        return self.subcategoryName

    def set_subcategory_bestsellers(self, bestsellers):
        self.subcategory_bestsellers = bestsellers

    def get_subcategory_books(self):
        return self.subcategory_bestsellers