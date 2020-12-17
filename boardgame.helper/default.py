# import the kodi python modules we are going to use
# see the kodi api docs to find out what functionality each module provides
import xbmc
import xbmcgui
import xbmcaddon
import untangle
import json
#import requests
import time
import sys
import imagedownload

try:
   import StorageServer
except:
   import storageserverdummy as StorageServer

cache = StorageServer.StorageServer("boardgame.helper", 24) 

# create a class for your addon, we need this to get info about your addon
ADDON = xbmcaddon.Addon()
# get the full path to your addon, decode it to unicode to handle special (non-ascii) characters in the path
#CWD = ADDON.getAddonInfo('path') # for kodi 19 and up..
CWD = ADDON.getAddonInfo('path').decode('utf-8')

class Collection:
    def __init__(self, name):
        self.name = name
        self.games = []
        self.expansions = []
        self.wish_list = []
        self.total_owned = 0
        self.total_wish_list = 0
        self.total_exp = 0

    def __build_dict(self, p, fp):
        rank = fp.stats.rating.ranks.rank
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

        if fp.stats.rating['value'] == 'N/A':
            rating = -1
        else:
            rating = fp.stats.rating['value']

        _d = {
            'name': p.name.cdata,
            'bgg_id': p['objectid'],
            'year_published': pub_year,
            'min_players': fp.stats['minplayers'],
            'max_players': self.__check_none(fp.stats['maxplayers']),
            'min_play_time': fp.stats['minplaytime'],
            'max_play_time': self.__check_none(fp.stats['maxplaytime']),
            'total_owned': fp.stats['numowned'],
            'rating': rating,
            'total_ratings': fp.stats.rating.usersrated['value'],
            'average_rating': fp.stats.rating.average['value'],
            'bayes_average': fp.stats.rating.bayesaverage['value'],
            'std_dev': fp.stats.rating.stddev['value'],
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

    def __pre_build(self, _obj, _full_obj, _exp):
        try:
            for i in range(len(_obj.items)):

                _path = _obj.items.item[i]
                _full_path = _full_obj.items.item[i]

                _game_dict = self.__build_dict(_path, _full_path)

                if int(_game_dict['own']):
                    if _exp:
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

        no_expansion = "&excludessubtype=boardgameexpansion"
        expansion = "&subtype=boardgameexpansion"
        full_stats = "&stats=1"

        # Three calls are necessary due to quirks in boardgamegeek.com's API - see bgg xml document tree.txt
        while True:
            api_url = str("https://api.geekdo.com/xmlapi2/collection?username=" + self.name)
            obj_full = untangle.parse(api_url + full_stats)
            obj_games = untangle.parse(api_url + no_expansion)
            obj_expansion = untangle.parse(api_url + expansion)

            # test for invalid username
            try:
                if obj_full.errors.error:
                    if __name__ == '__main__':
                        self.name = input(obj_full.errors.error.message.cdata + ".  Enter User Name: ")
                    else:
                        return 1

                    if self.name == 'q':
                        sys.exit()
                    elif self.name == '-h':
                        Collection.usage(True)

                    continue
            except AttributeError:
                # if no "error" attribute then there were no errors
                pass

            # Test for 202 response
            try:
                if obj_games.items['totalitems'] == '0':
                    if __name__ == '__main__':
                        print("User has no collection data")
                        self.name = input(".  Enter User Name: ")
                        continue
                    else:
                        return 3

                self.__pre_build(obj_games, obj_full, 0)
                self.__pre_build(obj_expansion, obj_full, 1)
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

    

# add a class to create your xml based window
class GUI(xbmcgui.WindowXML):
    # [optional] this function is only needed of you are passing optional data to your window
    def __init__(self, *args, **kwargs):
        # get the optional data and add it to a variable you can use elsewhere in your script
        self.data = kwargs['optional1']

    # until now we have a blank window, the onInit function will parse your xml file
    def onInit(self):
        # select a view mode, '50' in our case, as defined in the skin file
        xbmc.executebuiltin('Container.SetViewMode(50)')
        # define a temporary list where we are going to add all the listitems to
        listitems = []
        # this will be the first item in the list. 'my first item' will be the label that is shown in the list

        cache.table_name = "BGGInfos"

        table = cache.get("collection")
        if not table:
            my_addon = xbmcaddon.Addon()
            user_name = my_addon.getSetting('username')
            table = Collection(user_name)
            table.load()
            cache.set("collection", table)



        for elt in table.games:
            listitem3 = xbmcgui.ListItem(elt['name'])
            listitem3.setArt({'icon': str(elt['bgg_id'] + '.jpg')})
            listitems.append(listitem3)


        imagedownload.download()

        # by default the built-in container already contains one item, the 'up' (..) item, let's remove that one
        self.clearList()
        # now we are going to add all the items we have defined to the (built-in) container
        self.addItems(listitems)
        # give kodi a bit of (processing) time to add all items to the container
        xbmc.sleep(100)
        # this puts the focus on the top item of the container
        self.setFocusId(self.getCurrentContainerId())

# this is the entry point of your addon, execution of your script will start here
if (__name__ == '__main__'):
    # define your xml window and pass these four (kodi 17) or five (kodi 18) arguments (more optional items can be passed as well):
    # 1 'the name of the xml file for this window', 
    # 2 'the path to your addon',
    # 3 'the name of the folder that contains the skin',
    # 4 'the name of the folder that contains the skin xml files'
    # 5 [kodi 18] set to True for a media window (a window that will list music / videos / pictures), set to False otherwise
    # 6 [optional] if you need to pass additional data to your window, simply add them to the list
    # you'll have to add them as key=value pairs: key1=value1, key2=value2, etc...
    ui = GUI('script-testwindow.xml', CWD, 'default', '1080i', True, optional1='some data') # for kodi 18 and up..
#    ui = GUI('script-testwindow.xml', CWD, 'default', '1080i', optional1='some data') # use this line instead for kodi 17 and earlier
    # now open your window. the window will be shown until you close your addon
    ui.doModal()
    # window closed, now cleanup a bit: delete your window before the script fully exits
    del ui

# the end!


