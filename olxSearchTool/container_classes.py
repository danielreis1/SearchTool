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
