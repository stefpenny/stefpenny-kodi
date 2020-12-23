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
import re

# create a class for your addon, we need this to get info about your addon
ADDON = xbmcaddon.Addon()
CWD = ADDON.getAddonInfo('path').decode('utf-8')
__profile__ = xbmc.translatePath(ADDON.getAddonInfo('profile')).decode("utf-8")


# add a class to create your xml based window
class Art(xbmcgui.WindowXML):

    def __init__(self, *args, **kwargs):
        self.mediapath = os.path.join(CWD, 'resources', 'skins', 'Default', 'media')
        self.idLastElement = 0
        self.startitem = 1
        self.enditem = 50
        self.currenttotal = 0
        self.articles = []
        self.full_list_thread = []
        self.firstInit = True
        self.threadid = kwargs['threadid']
        self.setProperty('LineSepH', 'lineh.png')
        self.prevpageButton = xbmcgui.ControlButton(350, 80, 30, 30,'', alignment=2
                                          , focusTexture=os.path.join(self.mediapath, 'prev-iconh.png')
                                          , noFocusTexture=os.path.join(self.mediapath, 'prev-icon.png'))
        self.nextpageButton = xbmcgui.ControlButton(400, 80, 30, 30, '', alignment=2
                                                    , focusTexture=os.path.join(self.mediapath, 'next-iconh.png')
                                                    , noFocusTexture=os.path.join(self.mediapath, 'next-icon.png'))



    def onClick(self, control):
        if control == self.prevpageButton.getId() and int(self.idPage) > 1:
            self.startitem = int(self.startitem) - 50
            self.enditem = 50 * int(self.idPage)
            self.listArticles(self.idLastElement)
            self.setProperty('Pagecount',
                             'Showing ' + str(self.startitem) + '-' + str(self.enditem) + ' of ' + str(self.currenttotal))
        elif control == self.nextpageButton.getId() and int(self.enditem) < int(self.currenttotal):
            self.startitem = int(self.startitem) + 50
            if (int(self.enditem) + 50) > int(self.currenttotal):
                self.enditem = int(self.currenttotal)
            else:
                self.enditem = int(self.enditem) + 50
            self.listArticles(self.idLastElement)
            self.setProperty('Pagecount',
                             'Showing ' + str(self.startitem) + '-' + str(self.enditem) + ' of ' + str(self.currenttotal))

    def listArticles(self, minarticleid):
        self.articles = []

        self.gamedetail.loadarticles(self.threadid, minarticleid)

        self.currenttotal = int(int(self.gamedetail.total_articles) - 1)

        self.setProperty('Article', str(self.gamedetail.article).encode('utf-8'))

        for elt in self.gamedetail.articles:
            Content = self.ProcessArticleContent(elt['content'])
            listitem = xbmcgui.ListItem(Content)
            listitem.setArt({'icon': 'comment-icon.png'})
            #listitem.setProperty('numarticles', str(elt['numarticles']))
            listitem.setProperty('author', elt['username'])
            #calc nb days
            try:
                d0 = datetime.datetime.strptime(elt['postdate'][0:(len(elt['postdate']) - 6)], '%Y-%m-%dT%H:%M:%S')
                d1 = datetime.datetime.today()
                delta = d1 - d0
                if delta.days == 0:
                    listitem.setProperty('date', str(((delta.seconds//60) % 60)) + 'min')
                else:
                    listitem.setProperty('date', str(delta.days) + 'd')
            except:
                listitem.setProperty('date', 'unknown')

            self.idLastElement = elt['id']
            self.articles.append(listitem)


        self.clearList()
        self.addItems(self.articles)
        xbmc.sleep(100)
        self.setFocusId(50)


    def onInit(self):
        my_addon = xbmcaddon.Addon()
        xbmc.executebuiltin('Container.SetViewMode(50)')

        if self.firstInit == True:

            self.gamedetail = BGGApi.BGGApi()
            self.listArticles(0)

            if int(self.currenttotal) > 0:
                self.startitem = 1
            else:
                self.startitem = 0

            if int(self.currenttotal) < 50:
                self.enditem = self.currenttotal
            else:
                self.enditem = 50

            self.setProperty('Pagecount',
                             'Showing ' + str(self.startitem) + '-' + str(self.enditem) + ' of ' + str(
                                 self.currenttotal))

        # Window Already Initialized
        self.firstInit = False
        self.addControl(self.prevpageButton)
        self.addControl(self.nextpageButton)

    def ProcessArticleContent(self, Content):
        try:
            Content = Content.encode('ascii', 'ignore')
            Content = str(Content).replace('<br/> <br/>', '[CR]')
            Content = str(Content).replace('<br/><br/>', '[CR]')
            Content = str(Content).replace('<br/><br/><br/>', '[CR]')
            Content = str(Content).replace('<br/>', '[CR]')
            Content = str(Content).replace('<br />', '[CR]')
            Content = str(Content).replace('<b>', '[B]')
            Content = str(Content).replace('</b>', '[/B]')
            Content = str(Content).replace('<i>', '[I]')
            Content = str(Content).replace('</i>', '[/I]')
            Content = str(Content).replace('<i>', '[I]')
            Content = str(Content).replace('</i>', '[/I]')
            Content = str(Content).replace('</u>', '')
            Content = str(Content).replace('<u>', '')
            Content = str(Content).replace('<center>', '')
            Content = str(Content).replace('</center>', '')
            Content = str(Content).replace('</p>', '')
            Content = str(Content).replace('<p>', '')
            Content = str(Content).replace('</div></div></font>', '[/COLOR]')
            Content = str(Content).replace('</font>', '')
            Content = str(Content).replace('</div>', '')
            Content = str(Content).replace('<div class=\'quotebody\'>', '[COLOR cyan]')
            Content = re.sub(r'<(a|/a).*?>', '', Content, flags=re.MULTILINE)
            Content = re.sub(r'<img.*?>', '', Content, flags=re.MULTILINE)
            Content = re.sub(r'<div.*?>', '', Content, flags=re.MULTILINE)
            Content = re.sub(r'<font.*?>', '', Content, flags=re.MULTILINE)
            Content = str(Content).replace('[CR] [CR]', '[CR]')
            Content = str(Content).replace('[CR][CR]', '[CR]')
            Content = str(Content).replace('[CR][CR]', '[CR]')
            xbmc.log('Content : ' + str(Content))
        except:
            xbmc.log('Content Error : ' + str(Content).encode('utf8'))
        return Content

