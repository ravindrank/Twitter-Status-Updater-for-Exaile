#!/usr/bin/env python
# -*- coding: utf-8 -*-

import dbus, gobject, gtk, os
from gettext import gettext as _
import xl.plugins as plugins
import twitter

# Plugin description
PLUGIN_NAME        = _('Twitter Status Updater')
PLUGIN_ICON        = None
PLUGIN_ENABLED     = True
#PLUGIN_ENABLED     = False
PLUGIN_AUTHORS     = ['Ravindran K. <ravindran.k#G-mail.com ; Ingelrest François <Athropos#g-mail.com> for Original IM status Plugin ']
PLUGIN_VERSION     = '0.4.1a'
#Uses Python python-twitter==0.6-devel coz of SetSource() API
PLUGIN_DESCRIPTION = _(r""" Update Twitter Status from Exaile now playing track""")

#control the plugin actions
CONNS = plugins.SignalContainer()

# Possible actions when Exaile quits or stops playing
(
    DO_NOTHING,
    CHANGE_STATUS
) = range(2)

# Constants
PID                     = plugins.name(__file__)
TRACK_FIELDS            = ('album', 'artist', 'bitrate', 'genre', 'length', 'rating', 'title', 'track', 'year')
DEFAULT_STOP_ACTION     = DO_NOTHING
DEFAULT_STOP_STATUS     = _('Exaile is stopped')
DEFAULT_USERNAME     	= _('TwitterUsername')
DEFAULT_PASSWORD     	= _('TwitterPassword')

# TRANSLATORS: IMStatus plugin default status format
DEFAULT_STATUS_FORMAT   = _('♫ {artist} - {album} - {title}')
DEFAULT_UPDATE_ON_PAUSE = False
mUSERNAME		= ''
mPASSWORD		= ''

# Global variables
mNowPlaying         = ''                         # The currently used status message
mCurrentTrack       = None                       # The track currently being played

##############################################################################

def setStatusMsg(nowPlaying) :
	global mNowPlaying
        global api1
	#print "setstatus called"
	#print "now playing"
	#print nowPlaying
	mUSERNAME = APP.settings.get_str('username', default=DEFAULT_USERNAME, plugin=PID)
	mPASSWORD = APP.settings.get_str('password', default=DEFAULT_PASSWORD, plugin=PID)
	api1 = twitter.Api(username=mUSERNAME,password=mPASSWORD)
	api1.SetSource('TwitterStatusUpdaterForExaile')
	api1.SetUserAgent('TwitterStatusUpdaterForExaile')
	api1.SetXTwitterHeaders('TwitterStatusUpdaterForExaile', 'http://ravindran.k.googlepages.com/twitter.xml', PLUGIN_VERSION)
	api1.PostUpdate(nowPlaying)
	mNowPlaying = nowPlaying
	#print "setstatus end"

def updateStatus() :
    """
        Information about the current track has changed
    """
    global mCurrentTrack
    mCurrentTrack = APP.player.current
    # Construct the new status message
    nowPlaying = APP.settings.get_str('format', DEFAULT_STATUS_FORMAT, PID)
    for field in TRACK_FIELDS :
        nowPlaying = nowPlaying.replace('{%s}' % field, unicode(getattr(mCurrentTrack, field)))

    # And try to update the twitter status
    #print "update status called"
    setStatusMsg(nowPlaying)
    #print "update status end"	

def play_track(exaile, track) :
    global mCurrentTrack
    #print "start track called"
    mCurrentTrack = APP.player.current
    updateStatus()
    gobject.timeout_add(1000, onStopTimer)
    #print "start track end"

def pause_toggled(exaile, track):
    """
        Do nothing when paused
    """

def stop_track(exaile, track) :
    """
        Called when Exaile quits or when playback stops
    """
    global mCurrentTrack
    #print "stop track called"
    mCurrentTrack = None
    # Stop event is sent also when a track is finished, even if Exaile is going to play the next one
    # Since we don't want to change the status between each track, we add a delay of 1 sec. before doing anything
    # updateStatus()
    gobject.timeout_add(1000, onStopTimer)
    #print "stop track end"

def onStopTimer() :
    """
        Called 1 sec. after the reception of a stop event
    """
    global mNowPlaying

    # If mCurrentTrack is still None, it means that Exaile has not started to play another track
    # In this case, we may assume that it is really stopped
    if mCurrentTrack is None :
        mNowPlaying = ''
    return False


def initialize(self = None):
	global api1
	#print "Initialising Twitter Status Plugin ..."
	#mUSERNAME = APP.settings.get_str('username', default=DEFAULT_USERNAME, plugin=PID)
	#mPASSWORD = APP.settings.get_str('password', default=DEFAULT_PASSWORD, plugin=PID)
	api1 = twitter.Api(username=APP.settings.get_str('username', default=DEFAULT_USERNAME, plugin=PID),password=APP.settings.get_str('password', default=DEFAULT_PASSWORD, plugin=PID))
	api1.SetUserAgent('TwitterStatusUpdaterForExaile')
	api1.SetXTwitterHeaders('TwitterStatusUpdaterForExaile', 'http://ravindran.k.googlepages.com/twitter.xml', PLUGIN_VERSION)
	api1.SetSource('TwitterStatusUpdaterForExaile')
        api1.PostUpdate("""Twitter Status Updater v0.4.1a for Exaile http://ravindran.k.googlepages.com/twitterstatusupdaterforexaile """)
	#print "Initialising Twitter Status Plugin .. Done"
        CONNS.connect(APP.player, 'play_track', play_track)
        CONNS.connect(APP.player, 'stop_track', stop_track)
        CONNS.connect(APP.player, 'pause_toggled', pause_toggled)
	#print "Initialising Twitter Status Plugin .. Done"

def destroy() :
    """
        Called when the plugin is disabled
    """
    CONNS.disconnect_all()
    #print "Twitter status plugin unloaded"

def showHelp(widget, data=None) :
    """
        Display a dialog box with some help about status format
    """
    msg = _('Any field of the form <b>{field}</b> will be replaced by the '
        'corresponding value.\n\nAvailable fields are ')
    for field in TRACK_FIELDS :
        msg = msg + '<i>' + field + '</i>, '
    dlg = gtk.MessageDialog(None, gtk.DIALOG_MODAL, gtk.MESSAGE_INFO, gtk.BUTTONS_OK)
    dlg.set_markup(msg[:-2])
    dlg.run()
    dlg.destroy()

def configure() :
    """
        Called when the user wants to configure the plugin
    """
    dlg = plugins.PluginConfigDialog(APP.window, PLUGIN_NAME)

    align = gtk.Alignment()
    align.set_padding(5, 5, 5, 5)
    dlg.get_child().add(align)
    mainBox = gtk.VBox()
    mainBox.set_spacing(5)
    align.add(mainBox)

    # Upper part: status format		
    frame = gtk.Frame('')
    frame.get_label_widget().set_markup(_('<b> Status message: </b>'))
    mainBox.pack_start(frame, True, True, 0)
    align = gtk.Alignment(0, 0, 1, 1)
    align.set_padding(5, 5, 5, 5)
    frame.add(align)
    tmpBox = gtk.HBox()
    tmpBox.set_spacing(5)
    entryFormat = gtk.Entry()
    entryFormat.set_text(APP.settings.get_str('format', DEFAULT_STATUS_FORMAT, PID))
    button = gtk.Button(_('Help'), gtk.STOCK_HELP)
    tmpBox.pack_start(entryFormat, True, True)
    tmpBox.pack_start(button)
    button.connect('clicked', showHelp)
    align.add(tmpBox)

    # Lower part: Twitter Username, Password
    frame = gtk.Frame('')
    frame.get_label_widget().set_markup(_('<b>Username:  </b>'))
    mainBox.pack_start(frame, False, False, 0)

    tmpBox = gtk.VBox()
    tmpBox.set_spacing(5)
	
    inputUsername = gtk.Entry()
    inputUsername.set_text(APP.settings.get_str('username', default=DEFAULT_USERNAME, plugin=PID))
    frame.add(inputUsername)		

    frame = gtk.Frame('')
    frame.get_label_widget().set_markup(_('<b>Password:  </b>'))
    mainBox.pack_start(frame, False, False, 0)
    tmpBox = gtk.VBox()
    tmpBox.set_spacing(5)

    inputPassword = gtk.Entry()
    inputPassword.set_text(APP.settings.get_str('password', default=DEFAULT_PASSWORD, plugin=PID))    
    frame.add(inputPassword)

    frame = gtk.Frame('')
    frame.get_label_widget().set_markup(_('<b> Miscellaneous: </b>'))
    mainBox.pack_start(frame, False, False, 0)
    tmpBox = gtk.VBox()
    tmpBox.set_spacing(5)
    align = gtk.Alignment()
    align.set_padding(5, 5, 5, 5)
    frame.add(align)
    align.add(tmpBox)

    resetButton = gtk.Button(_('Reset'))
    tmpBox.pack_start(resetButton, False, False, 0)
    resetButton.connect('clicked', initialize)

    dlg.show_all()
    result = dlg.run()
    dlg.hide()
    if result == gtk.RESPONSE_OK :
    	APP.settings.set_str('format',	entryFormat.get_text(),   PID)
    	APP.settings.set_str('username',inputUsername.get_text(), PID)
    	APP.settings.set_str('password',inputPassword.get_text(), PID)

