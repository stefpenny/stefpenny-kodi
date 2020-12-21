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
class GameDetail(xbmcgui.WindowXML):

    def __init__(self, *args, **kwargs):
        self.mediapath = os.path.join(CWD, 'resources', 'skins', 'Default', 'media')
        self.gameid = kwargs['gameid']

    def onInit(self):
        self.setProperty('RatingIcon', 'rating.png')
        self.setProperty('RankIcon', 'star-icon.png')
        self.setProperty('TypeIcon', 'genius-icon.png')
        self.setProperty('LineSepV', 'linev.png')
        self.setProperty('LineSepH', 'lineh.png')

        # getting game details
        self.gamedetail = collection.Collection('')
        self.gamedetail.loadgame(self.gameid)

        file_name = self.gamedetail.game['image'].cdata.split('/')[-1]
        file_ext = file_name.split('.')[-1]

        self.setProperty('GameImage', str(__profile__ + str(self.gamedetail.game['bgg_id'] + '.' + file_ext)))
        self.setProperty('Name', self.gamedetail.game['name'] + ' (' + self.gamedetail.game['year_published'] + ')')
        self.setProperty('RatingValue', str(self.gamedetail.game['average_rating']))

        RankValue = 'RANK: '
        for rank in self.gamedetail.game['rank']:
            if rank == 'Not Ranked':
                RankValue = RankValue + '-- '
            elif rank == 'Board Game Rank':
                RankValue = RankValue + 'Overall '
            else:
                RankValue = RankValue + rank.replace('Rank', '') + ' '

        if self.gamedetail.game['type'] == 'boardgameexpansion':
            TypeValue = 'Expansion'
        elif self.gamedetail.game['type'] == 'boardgame':
            TypeValue = 'Boardgame'

        if self.gamedetail.game['min_players'] == self.gamedetail.game['max_players'] or self.gamedetail.game['max_players'] == -1:
            NumPlayers = str(self.gamedetail.game['min_players']) + ' Players'
        else:
            NumPlayers = str(self.gamedetail.game['min_players']) + '-' + str(self.gamedetail.game['max_players']) + ' Players'

        Age = 'Age: ' + str(self.gamedetail.game['minage']) + '+'
        Weight = 'Weight: ' + str(self.gamedetail.game['weight']) + ' / 5'
        Designer = 'Designer: ' + str(self.gamedetail.game['designer'])
        Artist = 'Artist: ' + str(self.gamedetail.game['artist'])
        Publisher = 'Publisher: ' + str(self.gamedetail.game['publisher'])
        Description = str(self.gamedetail.game['description'].cdata).replace('&#10;', '[CR]')

        if self.gamedetail.game['min_play_time'] == -1 and self.gamedetail.game['max_play_time'] == -1:
            PlayingTime = '-- Min'
        elif self.gamedetail.game['max_play_time'] == -1:
            PlayingTime = str(self.gamedetail.game['min_play_time']) + ' Min'
        else:
            PlayingTime = str(self.gamedetail.game['min_play_time']) + '-' + str(self.gamedetail.game['max_play_time']) + ' Min'

        self.setProperty('RankValue', RankValue)
        self.setProperty('TypeValue', TypeValue)
        self.setProperty('NumPlayers', NumPlayers)
        self.setProperty('PlayingTime', PlayingTime)
        self.setProperty('Age', Age)
        self.setProperty('Weight', Weight)
        self.setProperty('Designer', Designer)
        self.setProperty('Artist', Artist)
        self.setProperty('Publisher', Publisher)
        self.setProperty('Description', Description)

        self.videobutton = xbmcgui.ControlButton(220, 900, 270, 50, 'Videos (' + str(self.gamedetail.game['vidcount']) + ')', alignment=2
                                                  , focusTexture=os.path.join(self.mediapath, 'buttonhover.png')
                                                  , noFocusTexture=os.path.join(self.mediapath, 'button.png'))
        self.addControl(self.videobutton)

        self.forumbutton = xbmcgui.ControlButton(520, 900, 270, 50,
                                                 'Forums', alignment=2
                                                 , focusTexture=os.path.join(self.mediapath, 'buttonhover.png')
                                                 , noFocusTexture=os.path.join(self.mediapath, 'button.png'))
        self.addControl(self.forumbutton)

