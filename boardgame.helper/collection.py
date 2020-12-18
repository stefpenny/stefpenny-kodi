import untangle

class Collection:
    def __init__(self, name):
        self.name = name
        self.games = []
        self.expansions = []
        self.wish_list = []
        self.total_owned = 0
        self.total_wish_list = 0
        self.total_exp = 0

    def __build_dict(self, p):
        rank = p.stats.rating.ranks.rank
        rank_list = []

        # Handling untangle returning single-element list containing string in dictionary format for ranks
        for i in range(len(rank)):
            temp = str(rank[i])
            arr = temp.split("'")
            n_index = arr.index("friendlyname")
            r_index = arr.index("value")
            rank_list.append(arr[n_index+2])
            rank_list.append(arr[r_index+2])

        # Handling unpublished games
        try:
            pub_year = p.yearpublished.cdata
        except AttributeError:
            pub_year = -1

        if p.stats.rating['value'] == 'N/A':
            rating = round(float(p.stats.rating.average['value']), 1)
        else:
            rating = round(float(p.stats.rating['value']), 1)

        _d = {
            'name': p.name.cdata,
            'bgg_id': p['objectid'],
            'subtype': p['subtype'],
            'year_published': pub_year,
            'min_players': p.stats['minplayers'],
            'max_players': self.__check_none(p.stats['maxplayers']),
            'min_play_time': self.__check_none(p.stats['minplaytime']),
            'max_play_time': self.__check_none(p.stats['maxplaytime']),
            'total_owned': p.stats['numowned'],
            'rating': rating,
            'total_ratings': p.stats.rating.usersrated['value'],
            'average_rating': p.stats.rating.average['value'],
            'bayes_average': p.stats.rating.bayesaverage['value'],
            'std_dev': p.stats.rating.stddev['value'],
            'rank': rank_list,
            'own': p.status['own'],
            'wish_list': p.status['wishlist'],
            'num_plays': p.numplays.cdata,
            'image': p.image,
            'thumbnail': p.thumbnail,
            'msrp': 0,
            'price': 0,
            'amzlink': ""
        }

        return _d

    def __check_none(self, value):
        if value is None:
            return -1
        else:
            return value

    def __pre_build(self, _obj):
        try:
            for i in range(len(_obj.items)):

                _path = _obj.items.item[i]
                _game_dict = self.__build_dict(_path)

                if int(_game_dict['own']):
                    if _game_dict['subtype'] == 'boardgameexpansion':
                        self.expansions.append(_game_dict)
                        self.total_exp += 1
                    else:
                        self.games.append(_game_dict)
                        self.total_owned += 1
                elif int(_game_dict['wish_list']):
                    self.wish_list.append(_game_dict)
                    self.total_wish_list += 1
                else:
                    pass

        except AttributeError:
            sys.exit()

    def load(self):

        no_expansion = "&excludesubtype=boardgameexpansion"
        expansion = "&subtype=boardgameexpansion"
        full_stats = "&stats=1"

        # Three calls are necessary due to quirks in boardgamegeek.com's API - see bgg xml document tree.txt
        while True:
            api_url = str("https://api.geekdo.com/xmlapi2/collection?username=" + self.name)
            obj_games = untangle.parse(api_url + no_expansion + full_stats)
            obj_expansion = untangle.parse(api_url + expansion + full_stats)

            # test for invalid username
            try:
                if obj_games.errors.error:
                    if __name__ == '__main__':
                        return 98
                    else:
                        return 1

            except AttributeError:
                # if no "error" attribute then there were no errors
                pass

            # Test for 202 response
            try:
                if obj_games.items['totalitems'] == '0':
                    if __name__ == '__main__':
                        return 99
                    else:
                        return 3

                self.__pre_build(obj_games)
                self.__pre_build(obj_expansion)
            except AttributeError:
                # 202 Response produces AttributeError -- 202 is common on your first call to a given username in a day
                if __name__ == '__main__':
                    time.sleep(3)
                    continue
                else:
                    return 2
            break

        if not __name__ == '__main__':
            return 0

    
