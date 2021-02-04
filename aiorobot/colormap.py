COLOR_CALIBRATION = {
    'black': 400, # light surface with no light
    'red': 600, # white surface with red light
    'green': 200, # white surface with green light
    'blue': 700, # white surface with blue light
}


class ColorMap:
    def __init__(self):
        self.reset()

    def reset(self):
        self.calibrate(**COLOR_CALIBRATION)

    def calibrate(self, black=None, red=None, green=None, blue=None):
        if black is not None:
            self._black_k = black
        if red is not None:
            self._red_k = red
        if green is not None:
            self._green_k = green
        if blue is not None:
            self._blue_k = blue

    @staticmethod
    def _map_component(comp, a=255, b=0):
        comp = max(comp, 0)
        return min(int(255 * comp / a + b), 255)

    def get(self, raw_color):
        black, red, green, blue = raw_color
        red -= black
        green -= black
        blue -= black

        black = self._map_component(black, self._black_k)
        red = self._map_component(red, self._red_k, black)
        green = self._map_component(green, self._green_k, black)
        blue = self._map_component(blue, self._blue_k, black)

        return red, green, blue
