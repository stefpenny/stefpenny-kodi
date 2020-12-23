# import the kodi python modules we are going to use
# see the kodi api docs to find out what functionality each module provides
import xbmc
import xbmcgui
import xbmcaddon
import json
import sys
import imagedownload
import BGGApi
import os
import gamedetail
import searchresults

# create a class for your addon, we need this to get info about your addon
ADDON = xbmcaddon.Addon()
CWD = ADDON.getAddonInfo('path').decode('utf-8')
__profile__ = xbmc.translatePath(ADDON.getAddonInfo('profile')).decode("utf-8")

class MyMonitor(xbmc.Monitor):
    def __init__(self, *args, **kwargs):
        xbmc.Monitor.__init__(self)
        self.action = kwargs['action']

    def onSettingsChanged(self):
        self.action()

# add a class to create your xml based window
class GUI(xbmcgui.WindowXML):

    def __init__(self, *args, **kwargs):
        self.mediapath = os.path.join(CWD, 'resources', 'skins', 'Default', 'media')
        self.SearchButton = xbmcgui.ControlButton(900, 30, 270, 50, 'Search Game', alignment=2
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
        self.listitems = []
        self.firstInit = True
        self.Monitor = MyMonitor(action=self.Init)

    def onClick(self, control):
        if control == 50:
            self.CurIndex = self.getCurrentListPosition()
            game_id = self.full_list[self.getCurrentListPosition()]['bgg_id']
            newWin = gamedetail.GameDetail('gamedetail.xml', CWD, 'default', '1080i', True, gameid=game_id)
            newWin.doModal()
            del newWin

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
                self.listitems = self.build_list(self.curFilter, self.curSort)
                self.addItems(self.listitems)
                self.setFocusId(50)

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
                self.listitems = self.build_list(self.curFilter, self.curSort)
                self.addItems(self.listitems)
                self.setFocusId(50)

        if control == self.SearchButton.getId():
            dialog = xbmcgui.Dialog()
            gamename = dialog.input("Search Game", type=xbmcgui.INPUT_ALPHANUM)
            if gamename != '':
                self.CurIndex = self.getCurrentListPosition()
                newWin = searchresults.Res('searchresults.xml', CWD, 'default', '1080i', True, searchquery=gamename)
                newWin.doModal()
                del newWin

    def build_list(self, mode, sort):
        self.listitems = []
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
            listitem = xbmcgui.ListItem(elt['name'] + ' (' + str(elt['year_published']) + ')')
            listitem.setIsFolder(True)

            if elt['image'] != 'no_img.jpg':
                file_name = elt['image'].cdata.split('/')[-1]
                file_ext = file_name.split('.')[-1]
                listitem.setArt({'icon': str(__profile__ + str(elt['bgg_id'] + '.' + file_ext))})
            else:
                listitem.setArt({'icon': str(elt['image'])})

            # Item properties
            listitem.setProperty('RatingValue', str(elt['rating']))
            listitem.setProperty('bggid', str(elt['bgg_id']))

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

            self.listitems.append(listitem)

        return self.listitems

        # until now we have a blank window, the onInit function will parse your xml file

    def onInit(self):
        self.Init()

    def Init(self):
        my_addon = xbmcaddon.Addon()

        if my_addon.getSetting('username') == '':
            xbmcaddon.Addon().openSettings()

        self.setProperty('RatingIcon', 'rating.png')
        self.setProperty('RankIcon', 'star-icon.png')
        self.setProperty('TypeIcon', 'genius-icon.png')
        self.setProperty('LineSepV', 'linev.png')
        self.setProperty('LineSepH', 'lineh.png')

        xbmc.executebuiltin('Container.SetViewMode(50)')
        user_name = my_addon.getSetting('username')

        if self.firstInit == True and user_name != '':
            self.curSort = int(my_addon.getSetting('default_sort'))
            self.curFilter = int(my_addon.getSetting('default_filter'))

            self.table = BGGApi.BGGApi()
            self.table.loadcollection(user_name)
            self.addControl(self.SearchButton)

            if my_addon.getSetting('refresh') == 'true':
                progress = xbmcgui.DialogProgress()
                progress.create('Refreshing database for user \"' + user_name + '\"')
                progress.update(0)

                total_games = int(self.table.total_owned) + int(self.table.total_exp) + int(self.table.total_wish_list)
                i = 1
                for elt in self.table.games:

                    imagedownload.download(__profile__, str(elt['image'].cdata), str(elt['bgg_id']))
                    imagedownload.download(__profile__, str(elt['thumbnail'].cdata),
                                           str(elt['bgg_id']) + '_tn')

                    progress.update(100 * i / total_games,
                                    line1='Game ' + str(i) + ' of ' + str(total_games),
                                    line2=elt['name'])
                    i = i + 1

                    if progress.iscanceled():
                        break

                for elt in self.table.expansions:

                    imagedownload.download(__profile__, str(elt['image'].cdata), str(elt['bgg_id']))
                    imagedownload.download(__profile__, str(elt['thumbnail'].cdata),
                                           str(elt['bgg_id']) + '_tn')

                    progress.update(100 * i / total_games,
                                    line1='Game ' + str(i) + ' of ' + str(total_games),
                                    line2=elt['name'])
                    i = i + 1

                    if progress.iscanceled():
                        break

                for elt in self.table.wish_list:

                    imagedownload.download(__profile__, str(elt['image'].cdata), str(elt['bgg_id']))
                    imagedownload.download(__profile__, str(elt['thumbnail'].cdata),
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

            # Navigation between controls
            self.SortButton.controlRight(self.SearchButton)
            self.SortButton.controlLeft(self.FilterButton)
            self.FilterButton.controlRight(self.SortButton)
            self.FilterButton.controlLeft(self.SearchButton)
            self.SearchButton.controlRight(self.FilterButton)
            self.SearchButton.controlLeft(self.SortButton)
            self.SearchButton.controlDown(self.getControl(50))
            self.SortButton.controlDown(self.getControl(50))
            self.FilterButton.controlDown(self.getControl(50))
            self.getControl(50).controlLeft(self.SearchButton)
            self.getControl(50).controlRight(self.SortButton)

            self.setProperty('CollectionStats', user_name + '\'s collection: ' + str(self.table.total_owned)
                             + ' Boardgames / ' + str(self.table.total_exp) + ' Expansions / ' + str(self.table.total_wish_list) + ' Wishes')

        if my_addon.getSetting('username') == '':
            self.setProperty('CollectionStats', 'BGG Username not set, go to addon settings')
        else:
            self.listitems = self.build_list(self.curFilter, self.curSort)

            self.clearList()
            self.addItems(self.listitems)

            xbmc.sleep(100)

            self.setFocusId(50)
            self.getControl(50).selectItem(self.CurIndex)

            # Window Already Initialized
            self.firstInit = False


if __name__ == '__main__':
    ui = GUI('bgglist.xml', CWD, 'default', '1080i', True, optional1='some data')
    ui.doModal()
    del ui
