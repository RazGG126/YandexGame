levels = ['game_map.txt', 'game_map_2.txt', 'game_map_3.txt']


class User:
    def __init__(self,level, coins, skin=None, kills=0, restarts=0, game_replays=0, ammo_spend=0, caught_cat=''):
        self.level = level
        self.coins = coins
        self.skin = skin
        self.kills = kills
        self.restarts = restarts
        self.game_replays = game_replays
        self.ammo_spend = ammo_spend
        self.caught_cat = caught_cat

    def create_dict(self):
        data = dict()

        data['level'] = self.level
        data['coins'] = self.coins
        data['skin'] = self.skin
        data['kills'] = self.kills
        data['restarts'] = self.restarts
        data['game_replays'] = self.game_replays
        data['ammo_spend'] = self.ammo_spend
        data['caught_cat'] = self.caught_cat

        return data

    def new_level(self):
        self.level = self.level + 1
