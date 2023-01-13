levels = ['game_map.txt', 'game_map_2.txt', 'game_map_3.txt']


class User:
    def __init__(self,level, coins, skin=None, kills=0, restarts=0, ammo_spend=0):
        self.level = min(3, level)
        self.coins = coins
        self.skin = skin
        self.kills = kills
        self.restarts = restarts
        self.ammo_spend = ammo_spend

    def create_dict(self):
        data = dict()

        data['level'] = self.level
        data['coins'] = self.coins
        data['skin'] = self.skin
        data['kills'] = self.kills
        data['restarts'] = self.restarts
        data['ammo_spend'] = self.ammo_spend

        return data

    def new_level(self):
        self.level = min(3, self.level + 1)
