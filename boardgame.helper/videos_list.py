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
        self.currentlang = 'All'
        self.currentlangid = 'all'
        self.catButtons = []

        self.language = xbmc.getLanguage(xbmc.ENGLISH_NAME)

    def onClick(self, control):

        if control == 50:
            self.CurIndex = self.getCurrentListPosition()
            vid_id = str(self.full_list_vid[self.getCurrentListPosition()]['extvideoid'])

            xbmc.executebuiltin("RunPlugin(plugin://plugin.video.youtube/play/?video_id=" + vid_id + "&incognito=true)")

        elif control == self.LangButton.getId():
            dialog = xbmcgui.Dialog()
            entries = []
            for lang in self.gamedetail.vidlang:
                entries.append(lang['name'])
            nr = dialog.select("Video language", entries)
            if nr >= 0:
                self.currentlangid = self.gamedetail.vidlang[nr]['id']
                self.currentlang = self.gamedetail.vidlang[nr]['name']
                self.listVideos()
                self.LangButton.setLabel('Language (' + self.currentlang + ')', 'font10', '0xFFFFFFFF',
                                                  '0xFFFF3300',
                                                  '0xFF000000')

                for elt in self.catButtons:
                    num = 0
                    for vid in self.gamedetail.videos:
                        if (str(vid['category']) == elt['category'] or elt['category'] == 'all') and (
                                self.currentlangid == 'all' or vid['languageid'] == self.currentlangid):
                            num += 1

                    color = 'OxFFFFFFFF'
                    if self.currentcat == elt['category']:
                        color = '0xFF7FC9FF'
                    self.getControl(elt['id']).setLabel(elt['catlabel'].encode('utf-8') + ' (' + str(num) + ')', 'font20_title', color,
                                    '0xFFFF3300', '0xFF000000')

        else:
            if type(self.getControl(control)) is xbmcgui.ControlButton:
                for i in self.catButtons:
                    if i['id'] == control:
                        self.currentcat = str(i['category'])
                        self.listVideos()
                        self.getControl(control).setLabel(self.getControl(control).getLabel(), 'font20_title', '0xFF7FC9FF', '0xFFFF3300',
                                           '0xFF000000')
                    else:
                        self.getControl(i['id']).setLabel(self.getControl(i['id']).getLabel(), 'font20_title', '0xFFFFFFFF',
                                                          '0xFFFF3300',
                                                          '0xFF000000')

    def listCategories(self):
        top = 120
        for elt in self.gamedetail.categories:
            CatButton = xbmcgui.ControlButton(20, top, 270, 45, elt['name'].encode('utf-8'), alignment=2
                                                    , focusTexture=os.path.join(self.mediapath, 'buttonhover.png')
                                                    , noFocusTexture=os.path.join(self.mediapath, 'button.png'))

            #get vid count for the category
            num = 0
            for vid in self.gamedetail.videos:
                if (str(vid['category']) == elt['type'] or top == 120) and (self.currentlangid == 'all' or vid['languageid'] == self.currentlangid):
                    num += 1

            if top == 120:
                CatButton.setLabel(elt['name'].encode('utf-8') + ' (' + str(num) + ')', 'font20_title', '0xFF7FC9FF', '0xFFFF3300', '0xFF000000')
            else:
                CatButton.setLabel(elt['name'].encode('utf-8') + ' (' + str(num) + ')', 'font20_title', '0xFFFFFFFF', '0xFFFF3300', '0xFF000000')

            top = top + 65
            self.addControl(CatButton)

            _tmp = {'id': CatButton.getId(),
                    'category': elt['type'],
                    'catlabel': elt['name']}
            self.catButtons.append(_tmp)



    def listVideos(self):
        self.viditems = []
        self.full_list_vid = []

        for elt in self.gamedetail.videos:
            if str(elt['videohost']) == 'youtube':
                if self.currentcat == 'all' or str(elt['category']) == self.currentcat:
                    if self.currentlangid == 'all' or elt['languageid'] == self.currentlangid:
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

        if self.firstInit == True:

            self.gamedetail = BGGApi.BGGApi()
            self.gamedetail.loadvideos(self.gameid)

            if my_addon.getSetting('default_lang') == 'true':
                xbmc.log('lang : ' + self.language)
                for lang in self.gamedetail.vidlang:
                    xbmc.log('langn : ' + lang['name'])
                    if lang['name'] == self.language:
                        self.currentlang = lang['name']
                        self.currentlangid = lang['id']

            self.LangButton = xbmcgui.ControlButton(1550, 30, 320, 50, 'Language (' + self.currentlang + ')',
                                                    alignment=2
                                                    , focusTexture=os.path.join(self.mediapath, 'buttonhover.png')
                                                    , noFocusTexture=os.path.join(self.mediapath, 'button.png'))
            self.addControl(self.LangButton)
            self.listCategories()

        self.listVideos()

        # Window Already Initialized
        self.firstInit = False

        self.getControl(50).controlLeft(self.catButtons[0])
        self.getControl(50).controlRight(self.LangButton)



