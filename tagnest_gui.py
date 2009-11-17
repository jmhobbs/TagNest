# -*- coding: utf-8 -*-

# GUI Has 3 Modes, Minimize to tray
# 1) Search
# 2) Items needing attention (duplicates & new )
# 3) Log

import sys
from PyQt4 import QtCore, QtGui

from multiprocessing import Process, freeze_support

def daemon ():
	opb_web.app.run()
 self.process = Process( target=server_process, args=( self.theme_combo.get_active_text(), ) )
self.process.start()
if None != self.process:

class TagNest( QtGui.QApplication ):

	def __init__ ( self, args ):
		QtGui.QApplication.__init__( self, args )

		self.daemon = None

		self.menu = QtGui.QMenu();
		self.daemonControl = self.menu.addAction( "Stop Daemon" );
		#self.connect( self.tweetAction, QtCore.SIGNAL( "triggered()" ), self.tweetDialog.show );
		item = self.menu.addAction( "Search" );
		#self.connect( item, QtCore.SIGNAL( "triggered()" ), self.doTimeline );
		self.pending = self.menu.addAction( "Pending" );
		#self.connect( item, QtCore.SIGNAL( "triggered()" ), self.doTimeline );
		item = self.menu.addAction( "Log" );
		#self.connect( item, QtCore.SIGNAL( "triggered()" ), self.doTimeline );
		exitAction = self.menu.addAction( "Exit" );
		self.connect( exitAction, QtCore.SIGNAL( "triggered()" ), self.quit );

		# Tray icon
		self.tray = QtGui.QSystemTrayIcon( QtGui.QIcon( "resource/icon.png" ) );
		self.tray.setContextMenu( self.menu );
		#self.connect( self.tray, QtCore.SIGNAL( "activated( QSystemTrayIcon::ActivationReason )" ), self.__icon_activated );
		self.tray.show();

	## Catch icon double click and show dialog or window
	#def __icon_activated ( self, reason ):
		#if reason == QtGui.QSystemTrayIcon.DoubleClick:
			#print "yeah!"
			##if self.Locked:
				##return;
			##if None != self.user:
				##if self.timelineWindow.isVisible():
					##self.timelineWindow.hide();
				##else:
					##self.timelineWindow.show();
			##else:
				##if self.loginDialog.isVisible():
					##self.loginDialog.hide();
				##else:
					##self.loginDialog.show();

if __name__ == "__main__":
	gtk.window_set_default_icon_from_file( 'resource/icon.png' )
	app = TagNest( sys.argv );
	sys.exit( app.exec_() );