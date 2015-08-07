

class Item():
    
    name = ""
    price = ""
    quantity = ""
    weight = ""
    limit = ""
    each = ""
    additional_info = ""
    rewards_program = ""
    points = "" # ???????????????????
    promotion = "" # XforY, BOGO, etc.
    store_name = ""
    store_address = ""
    store_city = ""
    store_province = ""
    store_postal_code = ""
    
    
    def __init__(self, name, price, quantity, weight, limit, each, additional_info, points, promotion, store_name, store_address, store_city, store_province, store_postal_code):
        self.name = name
        self.price = price
        self.quantity = quantity
        self.weight = weight
        self.limit = limit
        self.each = each
        self.additional_info = additional_info
        self.points = points
        self.promotion = promotion
        self.store_name = store_name
        self.store_address = store_address
        self.store_city = store_city
        self.store_province = store_province
        self.store_postal_code = store_postal_code
    
    def __str__(self):
        return "name: " + self.name + "      price: " + self.price + "      quantity: " + self.quantity + "       limit: " + self.limit + "   weight: " + self.weight +\
              "\neach: " + self.each + "   info: " + self.additional_info + "    points: " + self.points + "    promotion: " + self.promotion +\
              "store: " + self.store_name + ",  " + self.store_address + ",  " + self.store_city + "," + self.store_province + ",  " + self.store_postal_code
        
    def toCSVFormat(self):
        #return self.name + "," + self.price + "," + self.quantity + "," + self.limit + "," + self.weight +\
        #      "," + self.each + "," + self.additional_info + "," + self.points + "," + self.promotion +\
        #      "," + self.store_name + "," + self.store_address + ","+ self.store_city + "," + self.store_province + "," + self.store_postal_code
        return [self.name, self.price, self.quantity, self.limit, self.weight, self.each, self.additional_info, self.points, self.promotion,
                self.store_name, self.store_address, self.store_city, self.store_province, self.store_postal_code]
    