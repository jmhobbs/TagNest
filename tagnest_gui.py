# -*- coding: utf-8 -*-

"""
Copyright (c) 2009 John Hobbs, Little Filament

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
"""

# Handy widget guide: http://www.informit.com/articles/article.aspx?p=1405224&seqNum=6


import sys
from PyQt4 import QtCore, QtGui

from multiprocessing import Process, freeze_support

import time

import tagnest_daemon
from tagnest import TagNestUtil

def daemon ():
	tagnest_daemon.run()

# Base window that doesn't exit the app when closed.
class BaseWindow ( QtGui.QWidget ):
	def __init__ ( self, parent=None ):
		QtGui.QWidget.__init__( self, parent );

	def closeEvent ( self, event ):
		self.hide();
		event.ignore();

class VBoxWrapper ( QtGui.QWidget ):
	def __init__ ( self, parent=None ):
		QtGui.QWidget.__init__( self, parent );
		self.vbox = QtGui.QVBoxLayout();
		self.setLayout( self.vbox );
		self.vbox.addStretch( 1 );

	def box ( self ):
		return self.vbox;

class LogWindow ( BaseWindow ):
	def __init__ ( self, parent=None ):
		BaseWindow.__init__( self, parent );

		self.hide()

		self.setWindowTitle( "TagNest - Log" );
		self.resize( 500, 300 );

		self.util = TagNestUtil( "tagnest.db3" ) # TODO: Config this?

		vbw = VBoxWrapper()
		vbw.show()

		self.scroll = QtGui.QScrollArea()
		self.scroll.setWidgetResizable( True );
		self.scroll.setVerticalScrollBarPolicy( QtCore.Qt.ScrollBarAlwaysOn );
		self.scroll.setHorizontalScrollBarPolicy( QtCore.Qt.ScrollBarAlwaysOff );
		self.scroll.setWidget( vbw )

		self.last_log = 0
		self.update_logs( True )

		vbox = QtGui.QVBoxLayout()
		vbox.addWidget( self.scroll )
		self.setLayout( vbox )

		self.timer = QtCore.QTimer()
		QtCore.QObject.connect( self.timer, QtCore.SIGNAL("timeout()"), self.update_logs )
		self.timer.start( 1000 )

	# TODO: On show/hide do a refresh?
	# TODO: How much to show at a time?

	def update_logs ( self, force=False ):
		if force or self.isVisible():
			entries = self.util.get_log_entries( 20, self.last_log )
			entries.reverse()
			for entry in entries:
				label = QtGui.QLabel( "%s | %s" % ( time.strftime( '%Y-%m-%d %H:%M:%S', time.localtime( entry[0] ) ), entry[1] ) )

				if entry[2] == self.util.LOG_INFO:
					label.setStyleSheet( "QWidget { background-color: #99FF99 }" )
				elif entry[2] == self.util.LOG_WARN:
					label.setStyleSheet( "QWidget { background-color: #FFFF99 }" )
				elif entry[2] == self.util.LOG_FATAL:
					label.setStyleSheet( "QWidget { background-color: #FF9999 }" )
				else:
					label.setStyleSheet( "QWidget { background-color: #FFCC99 }" )

				self.scroll.widget().box().insertWidget( 0, label );
				self.last_log = entry[0]

class SearchWindow ( BaseWindow ):
	def __init__ ( self, parent=None ):
		BaseWindow.__init__( self, parent );

		self.hide()

		self.setWindowTitle( "TagNest - Search" );
		self.resize( 500, 300 );

class NewWindow ( BaseWindow ):
	def __init__ ( self, parent=None ):
		BaseWindow.__init__( self, parent );

		self.hide()

		self.setWindowTitle( "TagNest - New" );
		self.resize( 500, 300 );

		self.util = TagNestUtil( "tagnest.db3" ) # TODO: Config this?

		vbw = VBoxWrapper()
		vbw.show()

		self.scroll = QtGui.QScrollArea()
		self.scroll.setWidgetResizable( True );
		self.scroll.setVerticalScrollBarPolicy( QtCore.Qt.ScrollBarAlwaysOn );
		self.scroll.setHorizontalScrollBarPolicy( QtCore.Qt.ScrollBarAlwaysOff );
		self.scroll.setWidget( vbw )

		self.update_list( True )

		vbox = QtGui.QVBoxLayout()
		vbox.addWidget( self.scroll )
		self.setLayout( vbox )

		self.timer = QtCore.QTimer()
		QtCore.QObject.connect( self.timer, QtCore.SIGNAL("timeout()"), self.update_list )
		self.timer.start( 1000 ) # TODO: Config this?

	def update_list ( self, force=False ):
		if force or self.isVisible():
			print "update list"
			#self.scroll.widget().box().insertWidget( 0, label );

class TagNest( QtGui.QApplication ):

	def __init__ ( self, args ):
		QtGui.QApplication.__init__( self, args )

		self.setWindowIcon( QtGui.QIcon( 'resource/icon.png' ) )

		self.daemon = None
		self.util = TagNestUtil( "tagnest.db3" ) # TODO: Config this?

		self.util.log( "GUI Started.", self.util.LOG_INFO )

		self.log_window = LogWindow()

		self.menu = QtGui.QMenu();

		self.daemon_control = self.menu.addAction( "" );
		self.connect( self.daemon_control, QtCore.SIGNAL( "triggered()" ), self.toggle_daemon );
		item = self.menu.addAction( "Search" );
		#self.connect( item, QtCore.SIGNAL( "triggered()" ), self.doTimeline );
		self.pending = self.menu.addAction( "Pending" );
		#self.connect( item, QtCore.SIGNAL( "triggered()" ), self.doTimeline );
		item = self.menu.addAction( "Log" );
		self.connect( item, QtCore.SIGNAL( "triggered()" ), self.log_window.show );
		exitAction = self.menu.addAction( "Exit" );
		self.connect( exitAction, QtCore.SIGNAL( "triggered()" ), self.quit_clean );

		# Tray icon
		self.tray = QtGui.QSystemTrayIcon( QtGui.QIcon( "resource/icon.png" ) );
		self.tray.setContextMenu( self.menu );
		self.tray.show();

		self.toggle_daemon()

		self.timer = QtCore.QTimer()
		QtCore.QObject.connect( self.timer, QtCore.SIGNAL("timeout()"), self.check_daemon )
		self.timer.start( 10000 )

	def check_daemon ( self ):
		if None != self.daemon and False == self.daemon.is_alive():
			self.util.log( "Daemon found dead!", self.util.LOG_FATAL )
			self.util.log( "Restarting daemon.", self.util.LOG_WARN )
			self.daemon = None
			self.start_daemon()

	def toggle_daemon ( self ):
		if None != self.daemon:
			self.stop_daemon()
		else:
			self.start_daemon()

	def stop_daemon ( self ):
		if None != self.daemon:
			self.daemon.terminate()
			self.daemon = None
			self.util.log( "Daemon stopped by GUI.", self.util.LOG_INFO )
		self.daemon_control.setText( "Start Daemon" )

	def start_daemon ( self ):
		if None == self.daemon:
			self.daemon = Process( target=daemon )
			self.daemon.start()
			self.util.log( "Daemon started by GUI.", self.util.LOG_INFO )
		self.daemon_control.setText( "Stop Daemon" )

	def quit_clean( self ):
		self.stop_daemon()
		self.util.log( "GUI Stopped", self.util.LOG_INFO )
		self.quit()

if __name__ == "__main__":
	app = TagNest( sys.argv );
	sys.exit( app.exec_() );