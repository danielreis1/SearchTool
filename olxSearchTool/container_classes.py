import time
from typing import Set, Any


class FeaturesContainer:
    # purpose is to be a container for given features, nothing else, all added values should default to None because
    # they might be used in a source or destination but not in the other

    def __init__(self, caixa_mudancas=None, traction=None, segmento=None, fuel_type=None, cv_int=None, year_int=None,
                 doors=None, version=None):
        self.caixa_mudancas = caixa_mudancas
        self.traction = traction
        self.segmento = segmento
        self.fuel_type = fuel_type
        self.cv_int = cv_int
        self.year_int = year_int
        self.doors = doors
        self.version = version

    def __str__(self):
        return "caixa de mudancas " + self.caixa_mudancas + "\n" \
               + "traction " + str(self.traction) + "\n" \
               + "segmento " + str(self.segmento) + "\n" \
               + "fuel " + str(self.fuel_type) + "\n" \
               + "cv " + str(self.cv_int) + "\n" \
               + "year " + str(self.year_int) + "\n" \
               + "doors " + str(self.doors) + "\n" \
               + "version " + str(self.version) + "\n"


class SearchStatus:
    def __init__(self, brand, model, type_comp):
        self.set_all(brand, model, type_comp)

    def get_brand(self):
        return self.brand

    def get_model(self):
        return self.model

    def get_type_c(self):
        return self.type_comp

    def set_all(self, brand, model, type_comp):
        self.brand = brand
        self.model = model
        self.type_comp = type_comp

    def __str__(self):
        return "brand: " + self.brand + " model " + self.model + " type_c " + self.type_comp


class OutputTextContainer:
    def __init__(self, text):
        """
        :type text: str
        """

        self.text = "the higher the score the better the more similiar was the car from standvirtual to the car " \
                    "at volantesic\n" \
                    "price difference is: price_volantensic - price_standvirtual \n dest links are the links related " \
                    "to the car at volantesic, might be more than one because the car may be similar to many options " \
                    "from volantesc \n"
        self.text += "\n" + text + "\n"
        t = time.time()
        self.h = hash(self.text + str(t))
        self.text += self.h

    def add_text(self, text):
        t = time.time()
        self.text += "\n" + text + "\n****\n"
        self.h = hash(self.text + str(t))
        self.text += str(self.h)

    def get_text(self):
        return self.text

    def verify_hash(self):
        # TODO for a verify hashes tool
        pass


class TextHistory:
    # purpose is to be a container class with all good links for a given brand and model
    def __init__(self, brand, model, links):
        self.brand = brand
        self.model = model
        self.latest_links = links.copy()
        self.links = links.copy()
        self.hash = hash(str(self.links.copy()))
        self.bad_links = {}

    def __str__(self) -> str:
        string = ""
        string += self.brand + "\n" + self.model + "\n"
        for i in self.links:
            string += "source: " + str(i) + "\n"
            string += "dest: " + str(self.links[i]) + "\n"
        return str(string)

    def __eq__(self, other):
        if not isinstance(other, TextHistory):
            return False
        return self.brand == other.brand and self.model == other.model

    def __hash__(self):
        return hash(str(self.links))

    def add_link(self, src_link, dest_link):
        if src_link not in self.links.keys():
            self.links[src_link] = dest_link.copy()
            self.latest_links[src_link] = dest_link.copy()
            self.hash = hash(str(self.links.copy()))
            return True
        return False

    def read_link(self, link):
        if link in self.latest_links:
            del self.latest_links[link]
            return True
        else:
            return False

    def get_unread_links(self):
        return self.latest_links

    def get_links(self):
        return self.links

    def is_hist(self, brand, model):
        if self.brand == brand and self.model == model:
            return True

    def get_brand(self):
        return self.brand

    def get_model(self):
        return self.model

    def add_bad_link(self, src_link, dest_links):
        if src_link in self.bad_links:
            return False
        self.bad_links[src_link] = dest_links
        return True

    def get_bad_links(self):
        return self.bad_links


class TextHistorySet:
    set_of_hist: Set[TextHistory]

    def __init__(self, list_of_history):
        self.set_of_hist = set(list_of_history)

    def __str__(self):
        s = ""
        for i in self.set_of_hist:
            s += str(i)
        return s

    def __eq__(self, other):
        if not isinstance(other, set):
            return False
        for i in self.set_of_hist:
            for j in other:
                if not isinstance(j, TextHistory):
                    return False
            if i not in other:
                return False
        return True

    def __hash__(self):
        return hash(str(self))

    def __next__(self):
        return next(iter(self.set_of_hist))

    def __iter__(self):
        return iter(self.set_of_hist)

    def __len__(self):
        return len(self.set_of_hist)

    def get_hist(self, brand, model):
        for i in self.set_of_hist:
            if i.is_hist(brand, model):
                return i

    def set_hist(self, hist):
        if hist in self.set_of_hist:
            new_links = hist.get_links().copy()
            brand = hist.get_brand()
            model = hist.get_model()
            old_hist = self.get_hist(brand, model)
            for new_link in new_links:
                src = new_link
                dest = new_links[new_link]
                old_hist.add_link(src, dest)
        else:
            self.set_of_hist.add(hist)

    def history_exists(self, brand, model):
        for i in self.set_of_hist:
            if i.get_brand() == brand and i.get_model() == model:
                return True
        return False
