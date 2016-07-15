"""
MojeTv Class
@Author: Filip "Raiper34" Gulan
@Website: http:www.raiper34.net
@Mail: raipergm34@gmail.com
"""

#Python libraries
import urllib
import urllib2
import cookielib
import xml.dom.minidom
#Xbmc libraries
import xbmc
import xbmcgui
import xbmcplugin
import xbmcaddon
import xbmcvfs

class ProfiProgram():

    """
    Constructor
    """
    def __init__(self, baseUrl, addonHandle, arguments):
        self.baseUrl = baseUrl
        self.addonHandle = addonHandle
        self.arguments = arguments

        settings = xbmcaddon.Addon()
        self.username = settings.getSetting('username')
        self.password = settings.getSetting('password')

        cookies = cookielib.CookieJar()
        self.opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cookies))

        self.addon = xbmcaddon.Addon()

    """
    Create xbmc url
    """
    def buildUrl(self, query):
        return self.baseUrl + '?' + urllib.urlencode(query)

    """
    Check if username and password is correct
    """
    def checkCredentials(self):
        page = self.opener.open('http://www.blem.cz/list/exportkodi/tv.php?' + urllib.urlencode({'mail': self.username, 'heslo': self.password}))
        pageContent = page.read()
        xmlDom = xml.dom.minidom.parseString(pageContent)

        # Results of logining
        xbmc.executebuiltin('Notification(%s, %s, %d)' % ('Info', xmlDom.getElementsByTagName('seznam')[0].getElementsByTagName('info')[0].firstChild.nodeValue.encode("utf-8"), 3000))
        return int(xmlDom.getElementsByTagName('seznam')[0].getElementsByTagName('id')[0].firstChild.nodeValue)

    """
    Create modes folders, live tv or archive tv
    """
    def createModes(self):
        if self.checkCredentials() != 1:
            return
        url = self.buildUrl({'mode': 'archive'})
        item = xbmcgui.ListItem("Archiv", iconImage="defaultFolder.png")
        xbmcplugin.addDirectoryItem(handle=self.addonHandle, url=url, listitem=item, isFolder=True)
        url = self.buildUrl({'mode': 'live'})
        item = xbmcgui.ListItem("Live", iconImage="defaultFolder.png")
        xbmcplugin.addDirectoryItem(handle=self.addonHandle, url=url, listitem=item, isFolder=True)
        xbmcplugin.endOfDirectory(self.addonHandle)

    """
    Create channels folder
    """
    def createChannels(self):
        page = self.opener.open('http://www.blem.cz/list/exportkodi/tv.php?' + urllib.urlencode({'mail': self.username, 'heslo': self.password}))
        pageContent = page.read()
        xmlDom = xml.dom.minidom.parseString(pageContent)

        #Search
        url = self.buildUrl({'mode': 'search'})
        item = xbmcgui.ListItem("HLEDAT", iconImage="defaultFolder.png")
        xbmcplugin.addDirectoryItem(handle=self.addonHandle, url=url, listitem=item, isFolder=True)

        for channel in xmlDom.getElementsByTagName('seznam')[0].getElementsByTagName('tv'):
            url = self.buildUrl({'mode': 'chanel', 'channelsId': channel.getElementsByTagName('id')[0].firstChild.nodeValue, 'channelsLogo': channel.getElementsByTagName('logo')[0].firstChild.nodeValue})
            item = xbmcgui.ListItem(channel.getElementsByTagName('nazev')[0].firstChild.nodeValue, iconImage=channel.getElementsByTagName('logo')[0].firstChild.nodeValue)
            xbmcplugin.addDirectoryItem(handle=self.addonHandle, url=url, listitem=item, isFolder=True)

        xbmcplugin.endOfDirectory(self.addonHandle)

    """
    Create dates folder
    """
    def createDates(self):
        page = self.opener.open('http://www.blem.cz/list/exportkodi/den.php?' + urllib.urlencode({'mail': self.arguments['channelsId'][0]}))
        pageContent = page.read()
        xmlDom = xml.dom.minidom.parseString(pageContent)

        for day in xmlDom.getElementsByTagName('seznam')[0].getElementsByTagName('den'):
            url = self.buildUrl({'mode': 'date', 'channelId': self.arguments['channelsId'][0], 'dayId': day.getElementsByTagName('datum')[0].firstChild.nodeValue})
            item = xbmcgui.ListItem(day.getElementsByTagName('tyden')[0].firstChild.nodeValue + ' | ' + day.getElementsByTagName('datum')[0].firstChild.nodeValue, iconImage=self.arguments['channelsLogo'][0])
            xbmcplugin.addDirectoryItem(handle=self.addonHandle, url=url, listitem=item, isFolder=True)

        xbmcplugin.endOfDirectory(self.addonHandle)

    """
    Create list of videos
    """
    def createVideos(self):
        page = self.opener.open('http://www.blem.cz/list/exportkodi/porady.php?' + urllib.urlencode({'id': self.arguments['channelId'][0], 'den': self.arguments['dayId'][0], 'mail': self.username, 'heslo': self.password}))
        pageContent = page.read()
        xmlDom = xml.dom.minidom.parseString(pageContent)

        for tvShow in xmlDom.getElementsByTagName('seznam')[0].getElementsByTagName('tv'):
            item = xbmcgui.ListItem(tvShow.getElementsByTagName('odhour')[0].firstChild.nodeValue + ' | ' + tvShow.getElementsByTagName('nazev')[0].firstChild.nodeValue, iconImage=tvShow.getElementsByTagName('screen')[0].firstChild.nodeValue)
            item.setLabel(tvShow.getElementsByTagName('odhour')[0].firstChild.nodeValue + ' | ' + tvShow.getElementsByTagName('nazev')[0].firstChild.nodeValue)
            item.setThumbnailImage(tvShow.getElementsByTagName('screen')[0].firstChild.nodeValue)
            item.setInfo('video', { 'duration': tvShow.getElementsByTagName('delka')[0].firstChild.nodeValue })
            xbmcplugin.addDirectoryItem(handle=self.addonHandle, url=tvShow.getElementsByTagName('url')[0].firstChild.nodeValue, listitem=item)

        xbmcplugin.endOfDirectory(self.addonHandle)

    """
    Search videos
    """
    def searchVideos(self):
        keyboard = xbmc.Keyboard('', 'Hledat')
        keyboard.doModal()
        if keyboard.isConfirmed():
            page = self.opener.open('http://www.blem.cz/list/exportkodi/search.php?' + urllib.urlencode({'co': keyboard.getText(), 'mail': self.username, 'heslo': self.password}))
            pageContent = page.read()
            xmlDom = xml.dom.minidom.parseString(pageContent)

            for tvShow in xmlDom.getElementsByTagName('seznam')[0].getElementsByTagName('tv'):
                item = xbmcgui.ListItem(tvShow.getElementsByTagName('odhour')[0].firstChild.nodeValue + ' | ' + tvShow.getElementsByTagName('nazev')[0].firstChild.nodeValue, iconImage=tvShow.getElementsByTagName('screen')[0].firstChild.nodeValue)
                item.setLabel(tvShow.getElementsByTagName('odhour')[0].firstChild.nodeValue + ' | ' + tvShow.getElementsByTagName('nazev')[0].firstChild.nodeValue)
                item.setThumbnailImage(tvShow.getElementsByTagName('screen')[0].firstChild.nodeValue)
                item.setInfo('video', { 'duration': tvShow.getElementsByTagName('delka')[0].firstChild.nodeValue })
                xbmcplugin.addDirectoryItem(handle=self.addonHandle, url=tvShow.getElementsByTagName('url')[0].firstChild.nodeValue, listitem=item)

        xbmcplugin.endOfDirectory(self.addonHandle)

    """
    Create live TV list
    """
    def createLiveTv(self):
        page = self.opener.open('http://www.blem.cz/list/exportkodi/live.php?' + urllib.urlencode({'mail': self.username, 'heslo': self.password}))
        pageContent = page.read()
        xmlDom = xml.dom.minidom.parseString(pageContent)

        for tvShow in xmlDom.getElementsByTagName('seznam')[0].getElementsByTagName('tv'):
            item = xbmcgui.ListItem(tvShow.getElementsByTagName('nazev')[0].firstChild.nodeValue, iconImage=tvShow.getElementsByTagName('logo')[0].firstChild.nodeValue)
            item.setLabel(tvShow.getElementsByTagName('nazev')[0].firstChild.nodeValue)
            item.setThumbnailImage(tvShow.getElementsByTagName('logo')[0].firstChild.nodeValue)
            #item.setInfo('video', {'duration': tvShow.getElementsByTagName('delka')[0].firstChild.nodeValue})
            xbmcplugin.addDirectoryItem(handle=self.addonHandle, url=tvShow.getElementsByTagName('url')[0].firstChild.nodeValue, listitem=item)

        xbmcplugin.endOfDirectory(self.addonHandle)

    """
    Pick mode, or decision what interface to generate
    """
    def pickMode(self):
        mode = self.arguments.get('mode', None)
        #Pick Mode
        if mode is None:
            self.createModes()
        #Pick TV Archive chanel
        elif mode[0] == 'archive':
            self.createChannels()
        #Pick TV live
        elif mode[0] == 'live':
            self.createLiveTv()
        #Pick Date
        elif mode[0] == 'chanel':
            self.createDates()
        #Pick TV show
        elif mode[0] == 'date':
            self.createVideos()
        #Search in TV shows
        elif mode[0] == 'search':
            self.searchVideos()

    """
    Start function, that generate xbmc interface
    """
    def start(self):
        #Username or Password is blank
        if self.password is "" or self.username is "":
            self.addon.openSettings()
            return

        xbmcplugin.setContent(self.addonHandle, 'movies')
        self.pickMode()
