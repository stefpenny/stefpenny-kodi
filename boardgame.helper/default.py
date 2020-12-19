# import the kodi python modules we are going to use
# see the kodi api docs to find out what functionality each module provides
import xbmc
import xbmcgui
import xbmcaddon
import json
import time
import sys
import imagedownload
import collection
import os

try:
    import StorageServer
except:
    import storageserverdummy as StorageServer

cache = StorageServer.StorageServer("boardgame.helper", 24)

# create a class for your addon, we need this to get info about your addon
ADDON = xbmcaddon.Addon()
# get the full path to your addon, decode it to unicode to handle special (non-ascii) characters in the path
# CWD = ADDON.getAddonInfo('path') # for kodi 19 and up..
CWD = ADDON.getAddonInfo('path').decode('utf-8')
__profile__ = xbmc.translatePath(ADDON.getAddonInfo('profile')).decode("utf-8")


# add a class to create your xml based window
class GUI(xbmcgui.WindowXML):

    def __init__(self, *args, **kwargs):
        # get the optional data and add it to a variable you can use elsewhere in your script
        self.data = kwargs['optional1']
        self.table = []
        self.curFilter = 0
        self.curSort = 0
        self.mediapath = os.path.join(CWD, 'resources', 'skins', 'Default', 'media')

    def onClick(self, control):
        if control == 50:
            curctl = self.getFocus()
            listitem = curctl.getListItem(1)

        if control == self.SortButton.getId():
            dialog = xbmcgui.Dialog()
            entries = ["By Name (ASC)", "By Name (DESC)", "By Year published (ASC)", "By Year published (DESC)",
                       "By Type (ASC)", "By Type (DESC)"]
            nr = dialog.select("Sort Games", entries)
            if nr >= 0:
                entry = entries[nr]
                if entry == "By Name (ASC)":
                    self.curSort = 0
                elif entry == "By Name (DESC)":
                    self.curSort = 1
                elif entry == "By Year published (ASC)":
                    self.curSort = 2
                elif entry == "By Year published (DESC)":
                    self.curSort = 3
                elif entry == "By Type (ASC)":
                    self.curSort = 4
                elif entry == "By Type (DESC)":
                    self.curSort = 5

                self.clearList()
                listitems = self.build_list(self.curFilter, self.curSort)
                self.addItems(listitems)

        if control == self.FilterButton.getId():
            dialog = xbmcgui.Dialog()
            entries = ["Show All Owned", "Show Base Games", "Show Expansions", "Show WishList"]
            nr = dialog.select("Filter Games", entries)
            if nr >= 0:
                entry = entries[nr]
                if entry == "Show All Owned":
                    self.curFilter = 0
                elif entry == "Show Base Games":
                    self.curFilter = 1
                elif entry == "Show Expansions":
                    self.curFilter = 2
                elif entry == "Show WishList":
                    self.curFilter = 3

                self.clearList()
                listitems = self.build_list(self.curFilter, self.curSort)
                self.addItems(listitems)

    def build_list(self, mode, sort):
        listitems = []
        i = 1

        full_list = []
        if mode == 0:
            for elt in self.table.games:
                full_list.append(elt)
            for elt in self.table.expansions:
                full_list.append(elt)
        elif mode == 1:
            for elt in self.table.games:
                full_list.append(elt)
        elif mode == 2:
            for elt in self.table.expansions:
                full_list.append(elt)
        elif mode == 3:
            for elt in self.table.wish_list:
                full_list.append(elt)

        if sort == 0:
            full_list.sort(key=lambda x: x.get('name'))
        elif sort == 1:
            full_list.sort(key=lambda x: x.get('name'), reverse=True)
        elif sort == 2:
            full_list.sort(key=lambda x: x.get('year_published'))
        elif sort == 3:
            full_list.sort(key=lambda x: x.get('year_published'), reverse=True)
        elif sort == 4:
            full_list.sort(key=lambda x: x.get('subtype'))
        elif sort == 5:
            full_list.sort(key=lambda x: x.get('subtype'), reverse=True)

        for elt in full_list:
            file_name = elt['thumbnail'].cdata.split('/')[-1]
            file_ext = file_name.split('.')[-1]

            listitem = xbmcgui.ListItem(elt['name'] + ' (' + str(elt['year_published']) + ')')
            listitem.setIsFolder(True)
            listitem.setArt({'icon': str(__profile__ + 'imgCache\\' + str(elt['bgg_id'] + '.' + file_ext))})

            # Item properties
            listitem.setProperty('RatingValue', str(elt['rating']))

            RankValue = 'RANK: '
            for rank in elt['rank']:
                if rank == 'Not Ranked':
                    RankValue = RankValue + '-- '
                elif rank == 'Board Game Rank':
                    RankValue = RankValue + 'Overall '
                else:
                    RankValue = RankValue + rank.replace('Rank', '') + ' '

            if elt['subtype'] == 'boardgameexpansion':
                TypeValue = 'Expansion'
            elif elt['subtype'] == 'boardgame':
                TypeValue = 'Boardgame'

            if elt['min_players'] == elt['max_players'] or elt['max_players'] == -1:
                NumPlayers = str(elt['min_players']) + ' Players'
            else:
                NumPlayers = str(elt['min_players']) + '-' + str(elt['max_players']) + ' Players'

            if elt['min_play_time'] == -1 and elt['max_play_time'] == -1:
                PlayingTime = '-- Min'
            elif elt['max_play_time'] == -1:
                PlayingTime = str(elt['min_play_time']) + ' Min'
            else:
                PlayingTime = str(elt['min_play_time']) + '-' + str(elt['max_play_time']) + ' Min'

            listitem.setProperty('RankValue', RankValue)
            listitem.setProperty('TypeValue', TypeValue)
            listitem.setProperty('NumPlayers', NumPlayers)
            listitem.setProperty('PlayingTime', PlayingTime)

            listitems.append(listitem)

        return listitems

        # until now we have a blank window, the onInit function will parse your xml file

    def onInit(self):

        self.setProperty('WinWidth', str(self.getWidth()))
        self.setProperty('RatingIcon', 'rating.png')
        self.setProperty('RankIcon', 'star-icon.png')
        self.setProperty('TypeIcon', 'genius-icon.png')
        self.setProperty('LineSepV', 'linev.png')
        self.setProperty('LineSepH', 'lineh.png')
        self.setProperty('TestValue', __profile__)

        xbmc.executebuiltin('Container.SetViewMode(50)')
        my_addon = xbmcaddon.Addon()
        user_name = my_addon.getSetting('username')

        progress = xbmcgui.DialogProgress()
        progress.create('Refreshing database for user \"' + user_name + '\"')
        progress.update(0)

        cache.table_name = "BGGInfos"

        # table = cache.get("collection")
        # if not table:

        self.table = collection.Collection(user_name)
        self.table.load()

        # cache.set("collection", table)

        self.setProperty('CollectionStats',
                         user_name + '\'s collection: ' + str(self.table.total_owned) + ' Boardgames / ' + str(
                             self.table.total_exp) + ' Expansions')

        i = 1
        for elt in self.table.games:

            imagedownload.download(__profile__ + 'imgCache\\', str(elt['image'].cdata), str(elt['bgg_id']))
            imagedownload.download(__profile__ + 'imgCache\\', str(elt['thumbnail'].cdata), str(elt['bgg_id']) + '_tn')

            progress.update(100 * i / (self.table.total_owned + self.table.total_wish_list),
                            line1='Game ' + str(i) + ' of ' + str(self.table.total_owned + self.table.total_wish_list),
                            line2=elt['name'])
            i = i + 1

            if progress.iscanceled():
                break

        for elt in self.table.expansions:

            imagedownload.download(__profile__ + 'imgCache\\', str(elt['image'].cdata), str(elt['bgg_id']))
            imagedownload.download(__profile__ + 'imgCache\\', str(elt['thumbnail'].cdata), str(elt['bgg_id']) + '_tn')

            progress.update(100 * i / (self.table.total_owned + self.table.total_wish_list),
                            line1='Game ' + str(i) + ' of ' + str(self.table.total_owned + self.table.total_wish_list),
                            line2=elt['name'])
            i = i + 1

            if progress.iscanceled():
                break

        for elt in self.table.wish_list:

            imagedownload.download(__profile__ + 'imgCache\\', str(elt['image'].cdata), str(elt['bgg_id']))
            imagedownload.download(__profile__ + 'imgCache\\', str(elt['thumbnail'].cdata), str(elt['bgg_id']) + '_tn')

            progress.update(100 * i / (self.table.total_owned + self.table.total_wish_list),
                            line1='Game ' + str(i) + ' of ' + str(self.table.total_owned + self.table.total_wish_list),
                            line2=elt['name'])
            i = i + 1

            if progress.iscanceled():
                break

        progress.update(100)
        progress.close()

        listitems = self.build_list(self.curFilter, self.curSort)

        self.clearList()
        self.addItems(listitems)

        self.SortButton = xbmcgui.ControlButton(1500, 10, 270, 50, 'Sort Games', alignment=2
                                                , focusTexture=os.path.join(self.mediapath, 'buttonhover.png')
                                                , noFocusTexture=os.path.join(self.mediapath, 'button.png'))
        self.addControl(self.SortButton)

        self.FilterButton = xbmcgui.ControlButton(1200, 10, 270, 50, 'Filter Games', alignment=2
                                                , focusTexture=os.path.join(self.mediapath, 'buttonhover.png')
                                                , noFocusTexture=os.path.join(self.mediapath, 'button.png'))
        self.addControl(self.FilterButton)

        # Navigation between controls
        self.SortButton.controlRight(self.FilterButton)
        self.SortButton.controlLeft(self.FilterButton)
        self.FilterButton.controlRight(self.SortButton)
        self.FilterButton.controlLeft(self.SortButton)

        self.SortButton.controlDown(self.getControl(50))
        self.FilterButton.controlDown(self.getControl(50))

        self.getControl(50).controlLeft(self.FilterButton)
        self.getControl(50).controlRight(self.SortButton)

        xbmc.sleep(100)
        # this puts the focus on the top item of the container
        self.setFocusId(self.getCurrentContainerId())


if __name__ == '__main__':
    ui = GUI('bgglist.xml', CWD, 'default', '1080i', True, optional1='some data')
    ui.doModal()
    del ui
