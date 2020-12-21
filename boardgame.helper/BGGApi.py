import untangle
import xbmc
import time
import requests
import json

class BGGApi:
    def __init__(self):
        self.games = []
        self.videos = []
        self.categories = []
        self.expansions = []
        self.wish_list = []
        self.total_owned = 0
        self.total_wish_list = 0
        self.total_exp = 0
        self.game = []
        self.pageId = 1

    def __build_dict(self, p):
        rank = p.stats.rating.ranks.rank
        rank_list = []

        # Handling untangle returning single-element list containing string in dictionary format for ranks
        for i in range(len(rank)):
            temp = str(rank[i])
            arr = temp.split("'")
            n_index = arr.index("friendlyname")
            r_index = arr.index("value")
            rank_list.append(arr[n_index + 2])
            rank_list.append(arr[r_index + 2])

        # Handling unpublished games
        try:
            pub_year = p.yearpublished.cdata
        except AttributeError:
            pub_year = -1

        if p.stats.rating['value'] == 'N/A':
            rating = round(float(p.stats.rating.average['value']), 1)
        else:
            rating = round(float(p.stats.rating['value']), 1)

        image = ''
        try:
            if p.image != '':
                image = p.image
            else:
                image = 'no_img.jpg'
        except:
            image = 'no_img.jpg'

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
            'image': image,
            'thumbnail': p.thumbnail,
            'msrp': 0,
            'price': 0,
            'amzlink': ""
        }

        return _d

    def __build_game_dict(self, p):
        rank_list = []
        try:
            rank = p.statistics.ratings.ranks.rank

            for i in range(len(rank)):
                temp = str(rank[i])
                arr = temp.split("'")
                n_index = arr.index("friendlyname")
                r_index = arr.index("value")
                rank_list.append(arr[n_index + 2])
                rank_list.append(arr[r_index + 2])
        except:
            rank_list = []

        names = p.name
        name = ''
        if len(names) > 0:
            for i in range(len(names)):
                if names[i]['type'] == "primary":
                    name = names[i]['value'].encode('utf-8')
        else:
            name = p.name['value'].encode('utf-8')


        # Handling unpublished games
        try:
            pub_year = p.yearpublished['value']
        except AttributeError:
            pub_year = -1

        try:
            weight = round(float(p.statistics.ratings.averageweight['value']))
        except:
            weight = '--'

        image = ''
        try:
            if p.image != '':
                image = p.image
            else:
                image = 'no_img.jpg'
        except:
            image = 'no_img.jpg'

        links = p.link
        count = 0
        designer = ''
        try:
            for i in range(len(links)):
                if links[i]['type'] == "boardgamedesigner":
                    designer = designer + links[i]['value'].encode('utf-8')
                    count = count + 1
                    if count > 3:
                        break
                    else:
                        designer = designer + ', '
        except:
            designer = '--'

        count = 0
        artist = ''
        try:
            for i in range(len(links)):
                if links[i]['type'] == "boardgameartist":
                    artist = artist + links[i]['value'].encode('utf-8')
                    count = count + 1
                    if count > 3:
                        break
                    else:
                        artist = artist + ', '
        except:
            artist = '--'

        count = 0
        publisher = ''
        try:
            for i in range(len(links)):
                if links[i]['type'] == "boardgamepublisher":
                    publisher = publisher + links[i]['value'].encode('utf-8')
                    count = count + 1
                    if count > 3:
                        break
                    else:
                        publisher = publisher + ', '
        except:
            publisher = '--'

        _d = {
            'name': name,
            'bgg_id': p['id'],
            'type': p['type'],
            'year_published': pub_year,
            'min_players': p.minplayers['value'],
            'max_players': self.__check_none(p.maxplayers['value']),
            'min_play_time': self.__check_none(p.minplaytime['value']),
            'max_play_time': self.__check_none(p.maxplaytime['value']),
            'playingtime ': self.__check_none(p.playingtime['value']),
            'average_rating': round(float(p.statistics.ratings.average['value'])),
            'rank': rank_list,
            'image': image,
            'description': p.description,
            'minage': p.minage['value'],
            'weight': weight,
            'designer': designer,
            'artist': artist,
            'publisher': publisher,
            'vidcount': p.videos['total']
        }

        return _d

    def __build_search_dict(self, p):

        _d = {
            'name': p.name['value'],
            'bgg_id': p['id'],
            'type': p['type'],
            'year_published': p.yearpublished['value']
        }

        return _d

    def __build_video_dict(self, p):

        _d = {
            'extvideoid': p['extvideoid'],
            'title': p['title'],
            'videohost': p['videohost'],
            'image': p['images']['thumb'],
            'language': p['language'],
            'category': p['gallery']
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

    def loadcollection(self, name):

        no_expansion = "&excludesubtype=boardgameexpansion"
        expansion = "&subtype=boardgameexpansion"
        full_stats = "&stats=1"

        while True:
            api_url = str("https://api.geekdo.com/xmlapi2/collection?username=" + name)
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

    def loadgame(self, gameid):
        while True:
            api_url = str("https://api.geekdo.com/xmlapi2/thing?id=" + str(gameid) + '&stats=1&videos=1')
            obj_game = untangle.parse(api_url)

            try:
                if obj_game.errors.error:
                    xbmc.log('ERROR 98')
                    if __name__ == '__main__':
                        return 98
                    else:
                        return 1

            except AttributeError:
                # if no "error" attribute then there were no errors
                pass

            # Test for 202 response
            try:
                if len(obj_game.items.item) == 0:
                    if __name__ == '__main__':
                        return 99
                    else:
                        return 3

                self.game = self.__build_game_dict(obj_game.items.item)

            except AttributeError:
                # 202 Response produces AttributeError -- 202 is common on your first call to a given username in a day
                if __name__ == '__main__':
                    time.sleep(3)
                    continue
                else:
                    return 2
            break

    def searchgames(self, query):
        while True:
            api_url = str(
                "https://api.geekdo.com/xmlapi2/search?query=" + str(query) + '&type=boardgame,boardgameexpansion')
            obj_games = untangle.parse(api_url)

            try:
                if obj_games.errors.error:
                    xbmc.log('ERROR 98')
                    if __name__ == '__main__':
                        return 98
                    else:
                        return 1

            except AttributeError:
                # if no "error" attribute then there were no errors
                pass

            # Test for 202 response
            try:
                if obj_games.items['total'] == '0':
                    if __name__ == '__main__':
                        return 99
                    else:
                        return 3
                for i in range(len(obj_games.items)):
                    _game_dict = self.__build_search_dict(obj_games.items.item[i])
                    self.games.append(_game_dict)

            except AttributeError:
                # 202 Response produces AttributeError -- 202 is common on your first call to a given username in a day
                if __name__ == '__main__':
                    time.sleep(3)
                    continue
                else:
                    return 2
            break

    def loadvideos(self, gameid):
        while True:
            api_url = str('https://api.geekdo.com/api/videos?ajax=1&gallery=all&nosession=1&objectid=' + gameid + '&objecttype=thing&pageid=' + str(self.pageId) + '&showcount=50&sort=recent')
            result = requests.get(api_url)
            obj_videos = json.loads(result.text.encode("utf-8"))
            xbmc.log('api_url : ' + api_url)
            try:
                if obj_videos.errors.error:
                    xbmc.log('ERROR 98')
                    if __name__ == '__main__':
                        return 98
                    else:
                        return 1

            except AttributeError:
                # if no "error" attribute then there were no errors
                pass

            # Test for 202 response
            try:
                if len(obj_videos) == 0:
                    if __name__ == '__main__':
                        return 99
                    else:
                        return 3

                for x in obj_videos:
                    try:
                        if x == 'videos':
                            for y in obj_videos[x]:
                                _vid_dict = self.__build_video_dict(y)
                                self.videos.append(_vid_dict)

                        if x == 'config' and self.pageId == 1:
                            numitems = obj_videos[x]['numitems']
                            for y in obj_videos[x]:
                                if y == "galleries":
                                    for cat in obj_videos[x][y]:
                                        _category = {
                                            'type': cat['type'],
                                            'name': cat['name']
                                        }
                                        self.categories.append(_category)

                        if len(self.videos) < numitems:
                            self.pageId = self.pageId + 1
                            continue

                    except:
                        xbmc.log('tret : ' + str(x))

            except AttributeError:
                # 202 Response produces AttributeError -- 202 is common on your first call to a given username in a day
                if __name__ == '__main__':
                    time.sleep(3)
                    continue
                else:
                    return 2
            break
