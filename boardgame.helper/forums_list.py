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
import datetime
import article

# create a class for your addon, we need this to get info about your addon
ADDON = xbmcaddon.Addon()
CWD = ADDON.getAddonInfo('path').decode('utf-8')
__profile__ = xbmc.translatePath(ADDON.getAddonInfo('profile')).decode("utf-8")


# add a class to create your xml based window
class Vid(xbmcgui.WindowXML):

    def __init__(self, *args, **kwargs):
        self.mediapath = os.path.join(CWD, 'resources', 'skins', 'Default', 'media')
        self.CurIndex = 0
        self.idPage = 1
        self.startitem = 1
        self.enditem = 50
        self.currenttotal = 0
        self.threaditems = []
        self.full_list_thread = []
        self.firstInit = True
        self.gameid = kwargs['gameid']
        self.currentforum = ''
        self.catButtons = []
        self.setProperty('LineSepH', 'lineh.png')
        self.language = xbmc.getLanguage(xbmc.ENGLISH_NAME)
        self.prevpageButton = xbmcgui.ControlButton(620, 80, 30, 30,'', alignment=2
                                          , focusTexture=os.path.join(self.mediapath, 'prev-iconh.png')
                                          , noFocusTexture=os.path.join(self.mediapath, 'prev-icon.png'))
        self.nextpageButton = xbmcgui.ControlButton(670, 80, 30, 30, '', alignment=2
                                                    , focusTexture=os.path.join(self.mediapath, 'next-iconh.png')
                                                    , noFocusTexture=os.path.join(self.mediapath, 'next-icon.png'))

        self.addControl(self.prevpageButton)
        self.addControl(self.nextpageButton)
        self.prevpageButton.setVisible(False)
        self.nextpageButton.setVisible(False)

    def onClick(self, control):
        if control == 50:
            self.CurIndex = self.getCurrentListPosition()
            if int(self.full_list_thread[self.getCurrentListPosition()]['numarticles']) > 1:
                threadid = self.full_list_thread[self.getCurrentListPosition()]['id']
                newWin = article.Art('article.xml', CWD, 'default', '1080i', True, threadid=threadid)
                newWin.doModal()
                del newWin
        elif control == self.prevpageButton.getId() and int(self.idPage) > 1:
            self.idPage = int(self.idPage) - 1
            self.startitem = int(self.startitem) - 50
            self.enditem = 50 * int(self.idPage)
            self.listThreads(self.currentforum, self.idPage)
            self.setProperty('Pagecount',
                             'Showing ' + str(self.startitem) + '-' + str(self.enditem) + ' of ' + str(self.currenttotal))
        elif control == self.nextpageButton.getId() and int(self.enditem) < int(self.currenttotal):
            self.idPage = int(self.idPage) + 1
            self.startitem = int(self.startitem) + 50
            if (int(self.enditem) + 50) > int(self.currenttotal):
                self.enditem = int(self.currenttotal)
            else:
                self.enditem = int(self.enditem) + 50
            self.listThreads(self.currentforum, self.idPage)
            self.setProperty('Pagecount',
                             'Showing ' + str(self.startitem) + '-' + str(self.enditem) + ' of ' + str(self.currenttotal))
        else:
            if type(self.getControl(control)) is xbmcgui.ControlButton:
                for i in self.catButtons:
                    if i['id'] == control:
                        self.currentforum = str(i['forumid'])
                        self.currenttotal = i['count']
                        self.idPage = 1
                        if int(self.currenttotal) > 0:
                            self.startitem = 1
                        else:
                            self.startitem = 0

                        if int(self.currenttotal) < 50:
                            self.enditem = self.currenttotal
                        else:
                            self.enditem = 50

                        self.listThreads(self.currentforum, self.idPage)
                        self.getControl(control).setLabel(self.getControl(control).getLabel(), 'font20_title', '0xFF7FC9FF', '0xFFFF3300',
                                           '0xFF000000')

                        self.setProperty('Pagecount', 'Showing ' + str(self.startitem) + '-' + str(self.enditem) + ' of ' + str(self.currenttotal))
                        self.prevpageButton.setVisible(True)
                        self.nextpageButton.setVisible(True)
                    else:
                        self.getControl(i['id']).setLabel(self.getControl(i['id']).getLabel(), 'font20_title', '0xFFFFFFFF',
                                                          '0xFFFF3300',
                                                          '0xFF000000')

        xbmc.log('trace : ' + str(self.idPage) + ' / ' + str(self.startitem) + ' / ' + str(self.enditem) + ' / ' + str(
            self.currenttotal))

    def listForums(self):
        top = 120
        for elt in self.gamedetail.forums:
            CatButton = xbmcgui.ControlButton(20, top, 270, 45, '', alignment=2
                                                    , focusTexture=os.path.join(self.mediapath, 'buttonhover.png')
                                                    , noFocusTexture=os.path.join(self.mediapath, 'button.png'))

            CatButton.setLabel(elt['title'].encode('utf-8') + ' (' + str(elt['threads']) + ')', 'font20_title', '0xFFFFFFFF',
                               '0xFFFF3300', '0xFF000000')

            top = top + 65
            self.addControl(CatButton)

            _tmp = {'id': CatButton.getId(),
                    'forumid': elt['id'],
                    'title': elt['title'],
                    'count': str(elt['threads'])}
            self.catButtons.append(_tmp)

    def listThreads(self, idForum, idPage):
        self.threaditems = []
        self.full_list_thread = []

        self.gamedetail.loadthreads(idForum, idPage)

        for elt in self.gamedetail.threads:
            self.full_list_thread.append(elt)
            listitem = xbmcgui.ListItem(elt['subject'].encode('utf-8'))
            listitem.setArt({'icon': 'comment-icon.png'})
            listitem.setProperty('numarticles', str(int(elt['numarticles']) - 1))
            listitem.setProperty('author', elt['author'])
            #calc nb days
            try:
                d0 = datetime.datetime.strptime(elt['lastpostdate'][0:(len(elt['lastpostdate']) -6)], '%a, %d %b %Y %H:%M:%S')
                d1 = datetime.datetime.today()
                delta = d1 - d0
                if delta.days == 0:
                    listitem.setProperty('date', str(((delta.seconds//60) % 60)) + 'min')
                else:
                    listitem.setProperty('date', str(delta.days) + 'd')
            except:
                listitem.setProperty('date', 'unknown')

            self.threaditems.append(listitem)


        self.clearList()
        self.addItems(self.threaditems)
        xbmc.sleep(100)

        self.setFocusId(50)
        self.getControl(50).selectItem(self.CurIndex)

    def onInit(self):
        my_addon = xbmcaddon.Addon()
        xbmc.executebuiltin('Container.SetViewMode(50)')

        if self.firstInit == True:

            self.gamedetail = BGGApi.BGGApi()
            self.gamedetail.loadforums(self.gameid)
            self.listForums()

        if self.currentforum != '':
            self.listThreads(self.currentforum, self.idPage)

        # Window Already Initialized
        self.firstInit = False
        self.setFocusId(self.catButtons[0]['id'])

