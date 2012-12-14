import urllib, urllib2, re, sys, cookielib, os
import xbmc, xbmcgui, xbmcplugin, xbmcaddon
from xbmcgui import ListItem
import CommonFunctions
import simplejson as json

# plugin constants
version = "0.0.1"
plugin = "cultureunplugged.com - " + version

__settings__ = xbmcaddon.Addon(id='plugin.video.cultureunplugged')
rootDir = __settings__.getAddonInfo('path')
if rootDir[-1] == ';':
    rootDir = rootDir[0:-1]
rootDir = xbmc.translatePath(rootDir)
settingsDir = __settings__.getAddonInfo('profile')
settingsDir = xbmc.translatePath(settingsDir)
cacheDir = os.path.join(settingsDir, 'cache')
pluginhandle = int(sys.argv[1])
# For parsedom
common = CommonFunctions
common.plugin = plugin
common.dbg = False
common.dbglevel = 3

programs_thumb = os.path.join(__settings__.getAddonInfo('path'), 'resources', 'media', 'programs.png')
topics_thumb = os.path.join(__settings__.getAddonInfo('path'), 'resources', 'media', 'topics.png')
search_thumb = os.path.join(__settings__.getAddonInfo('path'), 'resources', 'media', 'search.png')
next_thumb = os.path.join(__settings__.getAddonInfo('path'), 'resources', 'media', 'next.png')
movies_thumb = os.path.join(__settings__.getAddonInfo('path'), 'resources', 'media', 'movies.jpg')
tv_thumb = os.path.join(__settings__.getAddonInfo('path'), 'resources', 'media', 'television.jpg')
shows_thumb = os.path.join(__settings__.getAddonInfo('path'), 'resources', 'media', 'shows.png')
video_thumb = os.path.join(__settings__.getAddonInfo('path'), 'resources', 'media', 'movies.png')



########################################################
## URLs
########################################################
BASE_URL = 'http://www.cultureunplugged.com%s'
PAGE1 = '/documentaries/watch-online/festival/films.php?view=list&listType=entries&tags=&id=1'
INFO_URL = 'http://www.cultureunplugged.com/ajax/getMovieInfo.php?movieId=%s&type='

########################################################
## Modes
########################################################
M_DO_NOTHING = 0
M_BROWSE = 10
M_CATEGORIES = 20
M_SEARCH = 30
M_PLAY = 40

class MediaItem:
    ##################
    ## Class for items
    ##################
    def __init__(self):
        self.ListItem = ListItem()
        self.Image = ''
        self.Url = ''
        self.Isfolder = False
        self.Mode = ''
        
def getURL(url):
    ## Get URL
    print plugin + ' getURL :: url = ' + url
    cj = cookielib.LWPCookieJar()
    opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
    opener.addheaders = [('User-Agent', 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.1; WOW64; Trident/4.0; SLCC2;)')]
    usock = opener.open(url)
    response = usock.read()
    usock.close()
    return response

def save_web_page(url, filename):
    # Save page locally
    f = open(os.path.join(cacheDir, filename), 'w')
    data = getURL(url)
    f.write(data)
    f.close()
    return data
    
def load_local_page(filename):
    # Read from locally save page
    f = open(os.path.join(cacheDir, filename), 'r')
    data = f.read()
    f.close()
    return data

def cleanHtml(dirty):
    # Remove HTML codes
    clean = re.sub('&quot;', '\"', dirty)
    clean = re.sub('&#039;', '\'', clean)
    clean = re.sub('&#215;', 'x', clean)
    clean = re.sub('&#038;', '&', clean)
    clean = re.sub('&#8216;', '\'', clean)
    clean = re.sub('&#8217;', '\'', clean)
    clean = re.sub('&#8211;', '-', clean)
    clean = re.sub('&#8220;', '\"', clean)
    clean = re.sub('&#8221;', '\"', clean)
    clean = re.sub('&#8212;', '-', clean)
    clean = re.sub('&amp;', '&', clean)
    clean = re.sub("`", '', clean)
    clean = re.sub('<em>', '[I]', clean)
    clean = re.sub('</em>', '[/I]', clean)
    clean = re.sub('<strong>', '', clean)
    clean = re.sub('</strong>', '', clean)
    clean = re.sub('<br />', '\n', clean)
    return clean


def Browse(Url=False):
    ########################################################
    ## Browse for videos
    ########################################################
    # set content type so library shows more views and info
    xbmcplugin.setContent(int(sys.argv[1]), 'movies')
    # Get website contents
    if not Url:
        Url = BASE_URL % PAGE1
        data = save_web_page(Url, 'cup.html')
    #data = load_local_page('channels.html')
    else:
        data = getURL(Url)
    Videos = common.parseDOM(data, "div", attrs={ "class": "listViewContainer"})
    
    MediaItems = []
    for item in Videos:
        #print item
        Mediaitem = MediaItem()
        hdr6 = common.parseDOM(item, "div", attrs={ "class": "hdr6" })[0]
        Title = common.parseDOM(hdr6, "a", ret="title")[0]
        #print Title
        
        previewplayer = common.parseDOM(item, "div", attrs={ "class": "preview-player" })[0]
        Mediaitem.Image = common.parseDOM(previewplayer, "img", ret="src")[0]
        href = common.parseDOM(previewplayer, "a", ret="href")[0]
        code = re.compile('play/([^/]+)/').findall(href)[0]
        Url = INFO_URL % code
        froM = common.parseDOM(item, "div", attrs={ "class": "from"})[0]
        Director = common.parseDOM(froM, "a")[0]
        
        Duration = common.parseDOM(item, "div", attrs={ "class": "duration"})[0]
        Genre = common.parseDOM(hdr6, "a", attrs={ "class": "dark"})[0]
        Plot = common.parseDOM(item, "div", attrs={ "class": "movieSummary" })[0]
        Plot = common.stripTags(Plot)
        #print Url
        Mediaitem.Mode = M_PLAY
        Title = Title.encode('utf-8')
        #print Title
        Mediaitem.Url = sys.argv[0] + "?url=" + urllib.quote_plus(Url) + "&mode=" + str(Mediaitem.Mode) + "&name=" + urllib.quote_plus(Title)
        Mediaitem.ListItem.setInfo('video', { 'Title': Title, 'Plot': Plot,
                                             'Director': Director, 'Duration': Duration,
                                             'Genre': Genre})
        Mediaitem.ListItem.setThumbnailImage(Mediaitem.Image)
        Mediaitem.ListItem.setLabel(Title)
        Mediaitem.ListItem.setProperty('IsPlayable', 'true')
        MediaItems.append(Mediaitem)
        
    Pagination = common.parseDOM(data, "div", attrs={ "class": "pagination" })[0]        
    NextPage = common.parseDOM(Pagination, "a", attrs={ "onmouseover": "rollOverInnerImage\(this\)",
                                                 "onmouseout": "normalInnerImage\(this\)"},
                               ret="href")
    if NextPage:
        #print str(len(NextPage))
        if len(NextPage) == 1:
            NP = NextPage[0]
        elif len(NextPage) == 2:
            NP = None
        elif len(NextPage) == 3:
            NP = NextPage[2]
        if NextPage:
            Mediaitem = MediaItem()
            Title = __settings__.getLocalizedString(30014)
            #print NP
            Url = BASE_URL % common.replaceHTMLCodes(NP)
            Mediaitem.Image = next_thumb
            Mediaitem.Mode = M_BROWSE
            Mediaitem.Url = sys.argv[0] + "?url=" + urllib.quote_plus(Url) + "&mode=" + str(Mediaitem.Mode) + "&name=" + urllib.quote_plus(Title)
            Mediaitem.ListItem.setInfo('video', { 'Title': Title})
            Mediaitem.ListItem.setThumbnailImage(Mediaitem.Image)
            Mediaitem.ListItem.setLabel(Title)
            Mediaitem.Isfolder = True
            MediaItems.append(Mediaitem)
    
    Menu = [(__settings__.getLocalizedString(30010), '', topics_thumb, M_CATEGORIES)]
    for Title, Url, Thumb, Mode in Menu:
        Mediaitem = MediaItem()
        Mediaitem.Url = sys.argv[0] + "?url=" + urllib.quote_plus(Url) + "&mode=" + str(Mode) + "&name=" + urllib.quote_plus(Title)
        Mediaitem.ListItem.setThumbnailImage(Thumb)
        Mediaitem.ListItem.setLabel(Title)
        Mediaitem.Isfolder = True
        MediaItems.append(Mediaitem)
    
    addDir(MediaItems)

    # End of Directory
    xbmcplugin.endOfDirectory(int(sys.argv[1]))
    SetViewMode()
   
 
def BrowseCategories():
    ###########################################################
    ## Mode == M_CATEGORIES
    ## BROWSE CATEGORIES
    ###########################################################   
    
    # Get featured homepage contents
    #data = save_web_page(Url, 'cat.html')
    data = load_local_page('cup.html')
    
    listBox = common.parseDOM(data, "div", attrs={ "class": "listBox"})[0]
    Categories = re.compile('href="(.+?)">(.+?)<').findall(listBox)
    
    MediaItems = []
    for href, Title in Categories:
        Mediaitem = MediaItem()
        Title = common.replaceHTMLCodes(Title)
        thumb = programs_thumb
	href = href.replace(' ', '%20')
        Url = BASE_URL % href
        #print Url
        Mediaitem.Image = thumb
        Mediaitem.Mode = M_BROWSE
        #print Url
        #Title = Title.encode('utf-8')
        #print Title
        Mediaitem.Url = sys.argv[0] + "?url=" + urllib.quote_plus(Url) + "&mode=" + str(Mediaitem.Mode) + "&name=" + urllib.quote_plus(Title)
        Mediaitem.ListItem.setInfo('video', { 'Title': Title })
        Mediaitem.ListItem.setThumbnailImage(Mediaitem.Image)
        Mediaitem.ListItem.setLabel(Title)
        Mediaitem.Isfolder = True
        MediaItems.append(Mediaitem)
                    
    addDir(MediaItems)

    # End of Directory
    xbmcplugin.endOfDirectory(int(sys.argv[1]))
    
    
def Play(Url):
    #data = save_web_page(Url, 'video.html')
    #data = load_local_page('video.html')
    data = getURL(Url)
    vidJson = json.loads(data)
    videoUrl = vidJson['url']
    if not videoUrl:
        xbmcplugin.setResolvedUrl(pluginhandle, False, xbmcgui.ListItem())
        print 'Video not found.'
        return
    else:
        #print videoUrl
        xbmcplugin.setResolvedUrl(pluginhandle, True, xbmcgui.ListItem(path=videoUrl))
    
def SetViewMode():
    # Set View Mode selected in the setting
    try:
        # if (xbmc.getSkinDir() == "skin.confluence"):
        if __settings__.getSetting('view_mode') == "1": # List
            xbmc.executebuiltin('Container.SetViewMode(502)')
        if __settings__.getSetting('view_mode') == "2": # Big List
            xbmc.executebuiltin('Container.SetViewMode(51)')
        if __settings__.getSetting('view_mode') == "3": # Thumbnails
            xbmc.executebuiltin('Container.SetViewMode(500)')
        if __settings__.getSetting('view_mode') == "4": # Poster Wrap
            xbmc.executebuiltin('Container.SetViewMode(501)')
        if __settings__.getSetting('view_mode') == "5": # Fanart
            xbmc.executebuiltin('Container.SetViewMode(508)')
        if __settings__.getSetting('view_mode') == "6":  # Media info
            xbmc.executebuiltin('Container.SetViewMode(504)')
        if __settings__.getSetting('view_mode') == "7": # Media info 2
            xbmc.executebuiltin('Container.SetViewMode(503)')
            
        if __settings__.getSetting('view_mode') == "0": # Media info for Quartz?
            xbmc.executebuiltin('Container.SetViewMode(52)')
    except:
        print "SetViewMode Failed: " + __settings__.getSetting('view_mode')
        print "Skin: " + xbmc.getSkinDir()

def get_params():
    ## Get Parameters
        param = []
        paramstring = sys.argv[2]
        if len(paramstring) >= 2:
                params = sys.argv[2]
                cleanedparams = params.replace('?', '')
                if (params[len(params) - 1] == '/'):
                        params = params[0:len(params) - 2]
                pairsofparams = cleanedparams.split('&')
                param = {}
                for i in range(len(pairsofparams)):
                        splitparams = {}
                        splitparams = pairsofparams[i].split('=')
                        if (len(splitparams)) == 2:
                                param[splitparams[0]] = splitparams[1]
        return param

def addDir(Listitems):
    if Listitems is None:
        return
    Items = []
    for Listitem in Listitems:
        Item = Listitem.Url, Listitem.ListItem, Listitem.Isfolder
        Items.append(Item)
    handle = pluginhandle
    xbmcplugin.addDirectoryItems(handle, Items)


if not os.path.exists(settingsDir):
    os.mkdir(settingsDir)
if not os.path.exists(cacheDir):
    os.mkdir(cacheDir)
                    
params = get_params()
url = None
name = None
mode = None
titles = None
try:
        url = urllib.unquote_plus(params["url"])
except:
        pass
try:
        name = urllib.unquote_plus(params["name"])
except:
        pass
try:
        mode = int(params["mode"])
except:
        pass
try:
        titles = urllib.unquote_plus(params["titles"])
except:
        pass

xbmc.log("Mode: " + str(mode))
#print "URL: " + str(url)
#print "Name: " + str(name)
#print "Title: " + str(titles)

if mode == None:
    Browse()
elif mode == M_DO_NOTHING:
    print 'Doing Nothing'
elif mode == M_BROWSE:
    Browse(url)
elif mode == M_CATEGORIES:
    BrowseCategories()
#elif mode == M_SEARCH:
#    Search(url)
elif mode == M_PLAY:
    Play(url)
