class CarLinksStruct:
    # struct that links a brand and model to all its
    # s in the corresponding source website
    # purpose is to have all cars from brand and model in one place
    def __init__(self, brand, model, links, max_number_pages):
        self.brand = brand
        self.model = model
        self.links = set()
        self.add_links(links.copy())
        self.max_number_pages = max_number_pages

    def get_brand(self):
        return self.brand

    def get_model(self):
        return self.model

    def get_links(self):
        return self.links

    def get_max_pages(self):
        return self.max_number_pages

    def add_links(self, links):
        links = links.copy()
        if len(links) != 0:
            for i in links:
                self.links.add(i)
        else:
            print("nothing added to carLinksStruct in add_links")

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
    # associates a brand and model to a max_pages number in the source
    def __init__(self, brand, model, car_link_features_list=None, max_pages=None):

        if car_link_features_list is None:
            car_link_features_list = []
        self.car_link_features_list = set(car_link_features_list.copy())
        self.brand = brand
        self.model = model

        if max_pages is None:
            max_pages = {}
        self.max_pages = max_pages.copy()

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

    def __len__(self):
        return len(self.car_link_features_list)

    def get_brand(self):
        return self.brand

    def get_model(self):
        return self.model

    def get_features_list(self):
        return self.car_link_features_list

    def add_features(self, feats):
        self.car_link_features_list.add(feats)

    def add_car_link_feats_list_to_existing_set(self, list_of_car_link_feats):
        set_of_car_link_feats = set(list_of_car_link_feats)
        self.car_link_features_list = self.car_link_features_list.union(set_of_car_link_feats)

    def get_max_pages(self, source):
        return self.max_pages[source]

    def set_max_pages(self, source, max_pages):
        self.max_pages[source] = max_pages

    def car_exists(self, link):
        for car_link_feat in self.car_link_features_list:
            for car in car_link_feat.get_cars():
                if link == car.get_link():
                    return True
        return False


class CarLinkFeatures:
    # purpose is to link CarFeatures class to Car classes associates features(and destination url - associated to a
    # score) to a set of links(cars) -> 1 set of features can have many cars(links) with != prices, kms,
    # etc. features are key, value is set(Car) of Car class with given feature
    def __init__(self, features, cars=None, searched_dests=None):
        """
        :type searched_dests: set
        :type cars: set
        :type features: CarFeatures
        """
        if searched_dests is None:
            searched_dests = set()
        if cars is None:
            cars = []
        self.cars = set(cars)
        self.features = features
        self.searched_dests = searched_dests

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
        self.cars.add(Car(km, price, link, color))

    def remove_car(self, link):
        # this should remove car with link, because link is what defines a car
        self.cars.remove(Car(0, 0, link, "red"))

    def get_cars(self):
        return self.cars

    def is_feats_equal(self, other_feats):
        if self.features == other_feats:
            return True
        return False

    def get_feats(self):
        return self.features

    def get_feats_dict(self):
        return self.features.get_feats_dict()

    def set_destination(self, urls, max_score):
        self.features.set_destination(urls, max_score)

    def add_searched_dest(self, searched_dest):
        self.searched_dests.add(searched_dest)

    def get_searched_dests(self):
        return self.searched_dests

    def get_max_score(self):
        return self.get_feats().get_destination()[1]

    def get_destination(self):
        return self.get_feats().get_destination()


class CarFeatures:
    # has an associated score and url(destination) destination url may change, because one source can be compared to
    # several destination, and a destination may have a higher score than the other
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

        self.urls = []
        self.max_score = 0

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

    def set_destination(self, urls, max_score):
        self.urls += urls
        self.max_score = max_score

    def get_destination(self):
        return self.urls, self.max_score

    def get_version(self):
        return self.version


class Car:
    # purpose is to link one car link to his features
    # this class also has km, price, link

    def __init__(self, km, price, link, color, estimated_price=None, estimated_price_history=None):

        self.km = int(km)
        self.price = int(price)
        self.link = link
        self.color = color
        if estimated_price is None:
            self.estimated_price = 0
        else:
            self.estimated_price = estimated_price
        if estimated_price_history is None:
            estimated_price_history = {}
            self.estimated_price_history = estimated_price_history
        else:
            self.estimated_price_history = estimated_price_history.copy()

    def __eq__(self, other):
        return self.link == other.link

    def __hash__(self):
        return hash(str(self.link))

    def __str__(self):
        return "link " + self.link + "\n" \
               + "km " + str(self.km) + "\n" \
               + "price " + str(self.price) + "\n" \
               + "color " + str(self.color) + "\n"

    def is_good_estimation(self):
        diff = self.estimated_price - self.price
        if diff > 0:
            print("good offer")
            return True
        else:
            return False

    def get_estimation(self):
        print("estimated_price " + str(self.estimated_price) + " price " + str(self.price))
        diff = self.estimated_price - self.price
        if self.estimated_price == 0:
            print("score was not big enough, price not set, it's zero")
            return diff
        print("difference " + str(diff))
        return diff

    def set_new_estimation(self, estimated_price, dest):
        if estimated_price == -1:  # this indicates a problem when estimating price
            self.estimated_price = 0
            return
        print("set estimated_price " + str(estimated_price))
        if estimated_price > self.estimated_price:
            self.estimated_price = estimated_price
            print("new price estimated, higher than the last")
            self.estimated_price_history[dest] = self.estimated_price

    def get_estimated_price_history(self, dest):
        hist = None
        try:
            hist = self.estimated_price_history[dest]
        except KeyError:
            print('no history for this dest: ' + dest)
        return hist

    def get_link(self):
        return self.link

    def history_exists(self, dest):
        try:
            hist = self.estimated_price_history[dest]
            return True
        except KeyError:
            return False


class ContinueLoop(Exception):
    pass


class MaxScoreTooLowForEvaluation(Exception):
    def __init__(self, score):
        self.score = score

    def get_score_error_msg(self):
        print("error max score too low: " + str(self.score))


class FailedURLException(Exception):
    def __init__(self, url):
        self.url = url

    def get_url(self):
        stri = "failed url exception at\n" + self.url
        return stri
