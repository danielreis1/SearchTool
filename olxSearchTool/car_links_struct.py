class CarLinksStruct:
    # struct that links a brand and model to all its cars in the corresponding source website
    def __init__(self, brand, model, links, max_number_pages):
        self.brand = brand
        self.model = model
        self.links = links
        self.max_number_pages = max_number_pages

    def get_brand(self):
        return self.brand

    def get_model(self):
        return self.model

    def get_links(self):
        return self.links

    def __str__(self):
        string = ""
        string += self.brand + "\n"
        string += self.model + "\n"
        for link in self.links:
            string += link + "\n"
        string += str(self.max_number_pages) + "\n"
        return string


class CarLinkFeaturesList:
    # list of carLinkFeatures
    def __init__(self, brand, model, car_link_features_list=[]):
        self.car_link_features_list = set(car_link_features_list)
        self.brand = brand
        self.model = model

    def __str__(self):
        return self.brand + "\n" \
               + self.model + "\n"

    def __eq__(self, other):
        return self.brand == other.brand and self.model == other.model

    def __hash__(self):
        return hash(str(self))

    def get_features_list(self):
        return self.car_link_features_list

    def add_car(self, car):
        self.car_link_features_list.add(car)


class ContinueLoop(Exception):
    pass


class CarLinkFeatures:
    # associates features to a set of links(cars)
    # features are key, value is set(list) of links with given features
    def __init__(self, brand, model, features, links=set()):
        self.brand = brand
        self.model = model
        self.links = set(links)
        self.features = features

    def __str__(self) -> str:
        string = ""
        for i in self.links:
            string += i + "\n"
        string += str(self.features) + "\n"
        return string

    def __eq__(self, other):
        return self.features == other.features

    def __hash__(self):
        return hash(str(self.features))

    def add_link(self, link):
        self.links.add(link)

    def is_feats_equal(self, other_feats):
        if self.features == other_feats:
            return True
        return False


class CarFeatures:
    def __init__(self, brand, model, price, used, km, fuel_type, year, cv, color, caixa_mudancas, traction):
        self.brand = brand
        self.model = model
        self.price = int(price)
        self.used = used
        self.km = int(km)
        self.fuel_type = fuel_type
        self.year = int(year)
        self.cv = int(cv)
        self.color = color
        self.caixa_mudancas = caixa_mudancas
        self.traction = traction

    def __str__(self) -> str:
        return self.brand + "\n" \
               + self.model + "\n" \
               + "price " + str(self.price) + "\n" \
               + "used " + self.used \
               + "\n" + "km " + str(self.km) + "\n" \
               + "fuel_type " + self.fuel_type + "\n" \
               + "year " + str(self.year) + "\n" \
               + "power(cv) " + str(self.cv) + "\n" \
               + "color " + self.color + "\n" \
               + "traccao " + self.traction + "\n"

    def __eq__(self, other):
        return self.brand == other.brand \
               and self.model == other.model \
               and self.price == other.price \
               and self.used == other.used \
               and self.km == other.used \
               and self.km == other.km \
               and self.fuel_type == other.fuel_type \
               and self.year == other.year \
               and self.cv == other.cv \
               and self.color == other.color \
               and self.caixa_mudancas == other.caixa_mudancas \
               and self.traction == other.traction

    def __hash__(self):
        return hash(str(self))
