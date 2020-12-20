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
import gamedetail

# create a class for your addon, we need this to get info about your addon
ADDON = xbmcaddon.Addon()
CWD = ADDON.getAddonInfo('path').decode('utf-8')
__profile__ = xbmc.translatePath(ADDON.getAddonInfo('profile')).decode("utf-8")


# add a class to create your xml based window
class GUI(xbmcgui.WindowXML):

    def __init__(self, *args, **kwargs):
        self.mediapath = os.path.join(CWD, 'resources', 'skins', 'Default', 'media')
        self.videobutton = xbmcgui.ControlButton(900, 30, 270, 50, 'Video', alignment=2
                                                 , focusTexture=os.path.join(self.mediapath, 'buttonhover.png')
                                                 , noFocusTexture=os.path.join(self.mediapath, 'button.png'))
        self.FilterButton = xbmcgui.ControlButton(1200, 30, 270, 50, 'Filter Games', alignment=2
                                                  , focusTexture=os.path.join(self.mediapath, 'buttonhover.png')
                                                  , noFocusTexture=os.path.join(self.mediapath, 'button.png'))
        self.SortButton = xbmcgui.ControlButton(1500, 30, 270, 50, 'Sort Games', alignment=2
                                                , focusTexture=os.path.join(self.mediapath, 'buttonhover.png')
                                                , noFocusTexture=os.path.join(self.mediapath, 'button.png'))
        self.data = kwargs['optional1']
        self.table = []
        self.curFilter = 0
        self.curSort = 0
        self.CurIndex = 0
        self.full_list = []
        self.firstInit = True

    def MoveIndex(self, Direction):
        if Direction == 1:
            if self.CurIndex == (len(self.full_list) - 1):
                self.CurIndex = 0
            else:
                self.CurIndex = self.CurIndex + 1
        elif Direction == -1:
            if self.CurIndex > 0:
                self.CurIndex = self.CurIndex - 1
            else:
                self.CurIndex = (len(self.full_list) - 1)

        self.setProperty('TestValue', str(self.CurIndex))

    def onAction(self, action):
        if action.getId() == 10:
            self.close()
        try:
            curctl = self.getFocus()
            if curctl.getId() == 50 and action.getId() == 3:
                self.MoveIndex(-1)

            elif curctl.getId() == 50 and action.getId() == 4:
                self.MoveIndex(1)
                if self.CurIndex == 180:
                    curctl.selectItem(4)
                    self.CurIndex = 4

            elif curctl.getId() == 50 and action.getId() == 7:
                game_id = self.full_list[self.CurIndex]['bgg_id']
                newWin = gamedetail.GameDetail('gamedetail.xml', CWD, 'default', '1080i', True, gameid=game_id)
                newWin.doModal()
                del newWin
        finally:
            return

    def onClick(self, control):

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
                self.CurIndex = 0
                self.setFocusId(50)
                self.getControl(50).selectItem(self.CurIndex)

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
                self.CurIndex = 0
                self.setFocusId(50)
                self.getControl(50).selectItem(self.CurIndex)

        if control == self.videobutton.getId():
            xbmc.executebuiltin("RunPlugin(plugin://plugin.video.youtube/play/?video_id=GYyNQVxofc8&incognito=true)")

    def build_list(self, mode, sort):
        listitems = []
        i = 1

        self.full_list = []
        if mode == 0:
            for elt in self.table.games:
                self.full_list.append(elt)
            for elt in self.table.expansions:
                self.full_list.append(elt)
        elif mode == 1:
            for elt in self.table.games:
                self.full_list.append(elt)
        elif mode == 2:
            for elt in self.table.expansions:
                self.full_list.append(elt)
        elif mode == 3:
            for elt in self.table.wish_list:
                self.full_list.append(elt)

        if sort == 0:
            self.full_list.sort(key=lambda x: x.get('name'))
        elif sort == 1:
            self.full_list.sort(key=lambda x: x.get('name'), reverse=True)
        elif sort == 2:
            self.full_list.sort(key=lambda x: x.get('year_published'))
        elif sort == 3:
            self.full_list.sort(key=lambda x: x.get('year_published'), reverse=True)
        elif sort == 4:
            self.full_list.sort(key=lambda x: x.get('subtype'))
        elif sort == 5:
            self.full_list.sort(key=lambda x: x.get('subtype'), reverse=True)

        for elt in self.full_list:
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
        my_addon = xbmcaddon.Addon()

        self.setProperty('WinWidth', str(self.getWidth()))
        self.setProperty('RatingIcon', 'rating.png')
        self.setProperty('RankIcon', 'star-icon.png')
        self.setProperty('TypeIcon', 'genius-icon.png')
        self.setProperty('LineSepV', 'linev.png')
        self.setProperty('LineSepH', 'lineh.png')
        self.setProperty('TestValue', __profile__)

        xbmc.executebuiltin('Container.SetViewMode(50)')
        user_name = my_addon.getSetting('username')

        if self.firstInit == True:
            self.curSort = int(my_addon.getSetting('default_sort'))
            self.curFilter = int(my_addon.getSetting('default_filter'))
            self.table = collection.Collection(user_name)
            self.table.load()

            if my_addon.getSetting('refresh') == 'true':
                progress = xbmcgui.DialogProgress()
                progress.create('Refreshing database for user \"' + user_name + '\"')
                progress.update(0)

                total_games = int(self.table.total_owned) + int(self.table.total_exp) + int(self.table.total_wish_list)
                i = 1
                for elt in self.table.games:

                    imagedownload.download(__profile__ + 'imgCache\\', str(elt['image'].cdata), str(elt['bgg_id']))
                    imagedownload.download(__profile__ + 'imgCache\\', str(elt['thumbnail'].cdata),
                                           str(elt['bgg_id']) + '_tn')

                    progress.update(100 * i / total_games,
                                    line1='Game ' + str(i) + ' of ' + str(total_games),
                                    line2=elt['name'])
                    i = i + 1

                    if progress.iscanceled():
                        break

                for elt in self.table.expansions:

                    imagedownload.download(__profile__ + 'imgCache\\', str(elt['image'].cdata), str(elt['bgg_id']))
                    imagedownload.download(__profile__ + 'imgCache\\', str(elt['thumbnail'].cdata),
                                           str(elt['bgg_id']) + '_tn')

                    progress.update(100 * i / total_games,
                                    line1='Game ' + str(i) + ' of ' + str(total_games),
                                    line2=elt['name'])
                    i = i + 1

                    if progress.iscanceled():
                        break

                for elt in self.table.wish_list:

                    imagedownload.download(__profile__ + 'imgCache\\', str(elt['image'].cdata), str(elt['bgg_id']))
                    imagedownload.download(__profile__ + 'imgCache\\', str(elt['thumbnail'].cdata),
                                           str(elt['bgg_id']) + '_tn')

                    progress.update(100 * i / total_games,
                                    line1='Game ' + str(i) + ' of ' + str(total_games),
                                    line2=elt['name'])
                    i = i + 1

                    if progress.iscanceled():
                        break

                progress.update(100)
                progress.close()

            self.addControl(self.SortButton)
            self.addControl(self.FilterButton)
            self.addControl(self.videobutton)

            # Navigation between controls
            self.SortButton.controlRight(self.FilterButton)
            self.SortButton.controlLeft(self.FilterButton)
            self.FilterButton.controlRight(self.SortButton)
            self.FilterButton.controlLeft(self.SortButton)
            self.SortButton.controlDown(self.getControl(50))
            self.FilterButton.controlDown(self.getControl(50))
            self.getControl(50).controlLeft(self.FilterButton)
            self.getControl(50).controlRight(self.SortButton)

            self.setProperty('CollectionStats', user_name + '\'s collection: ' + str(self.table.total_owned)
                             + ' Boardgames / ' + str(self.table.total_exp) + ' Expansions')

        listitems = self.build_list(self.curFilter, self.curSort)

        self.clearList()
        self.addItems(listitems)

        xbmc.sleep(100)

        self.setFocusId(50)
        self.getControl(50).selectItem(self.CurIndex)

        # Window Already Initialized
        self.firstInit = False


if __name__ == '__main__':
    ui = GUI('bgglist.xml', CWD, 'default', '1080i', True, optional1='some data')
    ui.doModal()
    del ui
