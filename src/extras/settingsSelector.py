from discord.ui import View


class MapSelector(View):
    def __init__(self, maps: dict):
        self.maps = maps
