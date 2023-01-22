levels = ['game_map.txt', 'game_map_2.txt', 'game_map_3.txt']


class User:
    def __init__(self,level, coins, skin='default', skins_have=['default'], gun='ak47', kills=0, gun_have=['ak47']
                 , restarts=0, game_replays=0, ammo_spend=0, caught_cat='', menu_music_volume=0, control=True):
        self.level = level
        self.coins = coins
        self.skin = skin
        self.skins_have = skins_have
        self.gun = gun
        self.gun_have = gun_have
        self.kills = kills
        self.restarts = restarts
        self.game_replays = game_replays
        self.ammo_spend = ammo_spend
        self.caught_cat = caught_cat
        self.menu_music_volume = menu_music_volume
        self.control = control

    def create_dict(self):
        data = dict()

        data['level'] = self.level
        data['coins'] = self.coins
        data['skin'] = self.skin
        data['skins_have'] = self.skins_have
        data['kills'] = self.kills
        data['restarts'] = self.restarts
        data['gun'] = self.gun
        data['gun_have'] = self.gun_have
        data['game_replays'] = self.game_replays
        data['ammo_spend'] = self.ammo_spend
        data['caught_cat'] = self.caught_cat
        data['menu_music_volume'] = self.menu_music_volume
        data['control'] = self.control

        return data

    def new_level(self):
        self.level = self.level + 1