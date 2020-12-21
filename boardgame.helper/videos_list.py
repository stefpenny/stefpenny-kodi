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

# create a class for your addon, we need this to get info about your addon
ADDON = xbmcaddon.Addon()
CWD = ADDON.getAddonInfo('path').decode('utf-8')
__profile__ = xbmc.translatePath(ADDON.getAddonInfo('profile')).decode("utf-8")


# add a class to create your xml based window
class Vid(xbmcgui.WindowXML):

    def __init__(self, *args, **kwargs):
        self.mediapath = os.path.join(CWD, 'resources', 'skins', 'Default', 'media')
        self.CurIndex = 0
        self.viditems = []
        self.full_list_vid = []
        self.firstInit = True
        self.gameid = kwargs['gameid']
        self.currentcat = 'all'
        self.catButtons = []

    def onClick(self, control):

        if control == 50:
            self.CurIndex = self.getCurrentListPosition()
            vid_id = str(self.full_list_vid[self.getCurrentListPosition()]['extvideoid'])

            xbmc.executebuiltin("RunPlugin(plugin://plugin.video.youtube/play/?video_id=" + vid_id + "&incognito=true)")

        else:
            if type(self.getControl(control)) is xbmcgui.ControlButton:
                for i in self.catButtons:
                    if i['id'] == control:
                        self.currentcat = str(i['category'])
                        self.listVideos()

    def listCategories(self):
        top = 120
        for elt in self.gamedetail.categories:
            CatButton = xbmcgui.ControlButton(20, top, 270, 50, elt['name'].encode('utf-8'), alignment=2
                                                    , focusTexture=os.path.join(self.mediapath, 'buttonhover.png')
                                                    , noFocusTexture=os.path.join(self.mediapath, 'button.png'))

            top = top + 70
            self.addControl(CatButton)

            _tmp = {'id': CatButton.getId(),
                    'category': elt['type']}
            self.catButtons.append(_tmp)

    def listVideos(self):
        self.viditems = []
        self.full_list_vid = []

        for elt in self.gamedetail.videos:
            if str(elt['videohost']) == 'youtube':
                if self.currentcat == 'all' or str(elt['category']) == self.currentcat:
                    self.full_list_vid.append(elt)
                    listitem = xbmcgui.ListItem(elt['title'].encode('utf-8'))
                    listitem.setArt({'icon': elt['image']})
                    self.viditems.append(listitem)

        self.clearList()
        self.addItems(self.viditems)
        xbmc.sleep(100)

        self.setFocusId(50)
        self.getControl(50).selectItem(self.CurIndex)

    def onInit(self):
        my_addon = xbmcaddon.Addon()
        xbmc.executebuiltin('Container.SetViewMode(50)')

        self.gamedetail = BGGApi.BGGApi()
        self.gamedetail.loadvideos(self.gameid)

        self.listCategories()
        self.listVideos()

        # Window Already Initialized
        self.firstInit = False

