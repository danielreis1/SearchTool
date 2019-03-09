class CarLinksStruct:
    # struct that links a brand and model to all its cars in the corresponding source website
    # purpose is to have all cars from brand and model in one place
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
    # purpose is to have all brand-models associated with all existing features for that brand-model pair
    def __init__(self, brand, model, car_link_features_list=None):
        if car_link_features_list is None:
            car_link_features_list = []
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

    def __next__(self):
        return next(iter(self.car_link_features_list))

    def __iter__(self):
        return iter(self.car_link_features_list)

    def get_features_list(self):
        return self.car_link_features_list

    def add_features(self, feats):
        self.car_link_features_list.add(feats)


class CarLinkFeatures:
    # purpose is to link CarFeatures class to Car class
    # associates features to a set of links(cars) -> 1 set of features can have many cars(links) with != prices, kms,
    # etc.
    # features are key, value is set(Car) of Car class with given feature
    def __init__(self, features, cars=None):
        if cars is None:
            cars = set()
        self.cars = set(cars)
        self.features = features

    def __str__(self) -> str:
        string = ""
        for i in self.cars:
            string += str(i) + "\n"
        string += str(self.features) + "\n"
        return string

    def __eq__(self, other):
        return self.features == other.features

    def __hash__(self):
        return hash(str(self.features))

    def add_car(self, price, km, link, color):
        self.cars.add(Car(price, km, link, color))

    def remove_car(self, link):
        # this should remove car with link, because link is what defines a car
        self.cars.remove(Car(0, 0, link, "red"))

    def is_feats_equal(self, other_feats):
        if self.features == other_feats:
            return True
        return False

    def get_feats(self):
        return self.features

    def get_feats_dict(self):
        return self.features.get_feats_dict()


class CarFeatures:
    def __init__(self, used, fuel_type, year, cv, caixa_mudancas, traction, segmento,
                 version, doors):
        self.used = used
        self.fuel_type = fuel_type.strip().lower()
        self.year = int(year)
        self.cv = int(cv)
        self.caixa_mudancas = caixa_mudancas.strip().lower()
        self.traction = traction.strip().lower()
        self.segmento = segmento.strip().lower()
        self.version = version.strip().lower()
        self.doors = int(doors)

    def __str__(self) -> str:
        return "used " + self.used \
               + "fuel_type " + self.fuel_type + "\n" \
               + "year " + str(self.year) + "\n" \
               + "power(cv) " + str(self.cv) + "\n" \
               + "traccao " + self.traction + "\n" \
               + "segment " + self.segmento + "\n" \
               + "version " + self.version + "\n" \
               + "doors " + str(self.doors) + "\n"

    def __eq__(self, other):
        # price not compared
        return self.used == other.used \
               and self.fuel_type == other.fuel_type \
               and self.year == other.year \
               and self.cv == other.cv \
               and self.caixa_mudancas == other.caixa_mudancas \
               and self.traction == other.traction \
               and self.segmento == other.segmento \
               and self.doors == other.doors \
               and self.version == other.version

    def get_feats_dict(self):
        t_dic = {"segmento": self.segmento, "traccao": self.traction, "combustivel": self.fuel_type,
                 "tipo de caixa": self.caixa_mudancas}
        for i in t_dic:
            t_dic[i] = t_dic[i].strip().lower()
        return t_dic


class Car:
    # purpose is to link one car link to his features
    # this class also has km, price, link

    def __init__(self, km, price, link, color):
        self.km = int(km)
        self.price = int(price)
        self.link = link
        self.color = color

    def __eq__(self, other):
        return self.link == other.link

    def __hash__(self):
        return hash(str(self.link))

    def __str__(self):
        return "link " + self.link + "\n" \
               + "km " + str(self.km) + "\n" \
               + "price " + str(self.price) + "\n"\
               + "color " + str(self.color) + "\n"


class ContinueLoop(Exception):
    pass


class MaxScoreToLowForEvaluation(Exception):
    pass
