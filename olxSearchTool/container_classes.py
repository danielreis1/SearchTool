import time


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
