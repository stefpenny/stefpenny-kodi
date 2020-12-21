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

# create a class for your addon, we need this to get info about your addon
ADDON = xbmcaddon.Addon()
CWD = ADDON.getAddonInfo('path').decode('utf-8')
__profile__ = xbmc.translatePath(ADDON.getAddonInfo('profile')).decode("utf-8")


# add a class to create your xml based window
class Res(xbmcgui.WindowXML):

    def __init__(self, *args, **kwargs):
        self.mediapath = os.path.join(CWD, 'resources', 'skins', 'Default', 'media')
        self.searchquery = kwargs['searchquery']
        self.table = []
        self.CurIndex = 0
        self.full_list = []
        self.listitems = []
        self.firstInit = True
        self.SearchButton = xbmcgui.ControlButton(900, 30, 270, 50, 'New Search', alignment=2
                                                  , focusTexture=os.path.join(self.mediapath, 'buttonhover.png')
                                                  , noFocusTexture=os.path.join(self.mediapath, 'button.png'))

    def onClick(self, control):
        if control == 50:
            self.CurIndex = self.getCurrentListPosition()
            game_id = self.full_list[self.getCurrentListPosition()]['bgg_id']
            newWin = gamedetail.GameDetail('gamedetail.xml', CWD, 'default', '1080i', True, gameid=game_id)
            newWin.doModal()
            del newWin

        if control == self.SearchButton.getId():
            dialog = xbmcgui.Dialog()
            gamename = dialog.input("Search Game", type=xbmcgui.INPUT_ALPHANUM)
            if gamename != '':
                self.searchquery = gamename
                self.newSearch()

    def newSearch(self):
        self.table = BGGApi.BGGApi()
        self.table.searchgames(self.searchquery)
        self.listitems = []
        self.full_list = []

        if len(self.table.games) == 0:
            self.setProperty('Results', 'No game found for the query \"' + self.searchquery + '\"')

        elif len(self.table.games) == 1:
            self.setProperty('Results',
                             str(len(self.table.games)) + ' Game found for the query \"' + self.searchquery + '\"')
        else:
            self.setProperty('Results',
                             str(len(self.table.games)) + ' Games found for the query \"' + self.searchquery + '\"')

        for elt in self.table.games:
            self.full_list.append(elt)
            listitem = xbmcgui.ListItem(elt['name'].encode('utf-8') + ' (' + str(elt['year_published']) + ')')
            listitem.setProperty('bggid', str(elt['bgg_id']))
            self.listitems.append(listitem)

        self.clearList()
        self.addItems(self.listitems)

        xbmc.sleep(100)

        self.setFocusId(50)
        self.getControl(50).selectItem(self.CurIndex)

    def onInit(self):
        my_addon = xbmcaddon.Addon()
        xbmc.executebuiltin('Container.SetViewMode(50)')

        self.newSearch()

        if self.firstInit == True:
            self.addControl(self.SearchButton)

        # Window Already Initialized
        self.firstInit = False

