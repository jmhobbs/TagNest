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
from multiprocessing import Process, freeze_support
import ConfigParser
import time

from PyQt4 import QtCore, QtGui

import tagnest_daemon
from tagnest import TagNestUtil

def daemon ():
	tagnest_daemon.run( config )

# Base window that doesn't exit the app when closed.
class BaseWindow ( QtGui.QWidget ):
	def __init__ ( self, parent=None ):
		QtGui.QWidget.__init__( self, parent );

	def closeEvent ( self, event ):
		self.hide();
		event.ignore();

class VBoxWrapper ( QtGui.QWidget ):
	def __init__ ( self, parent=None ):
		QtGui.QWidget.__init__( self, parent )
		self.vbox = QtGui.QVBoxLayout()
		self.setLayout( self.vbox )
		self.vbox.addStretch( 1 )
		self.vbox.setSpacing( 0 )

	def box ( self ):
		return self.vbox

class LogWindow ( BaseWindow ):
	def __init__ ( self, parent=None ):
		BaseWindow.__init__( self, parent );

		self.hide()

		self.setWindowTitle( "TagNest - Log" );
		self.resize( 600, 300 );

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
		self.timer.start( config.getint( 'GUI', 'logrefresh' ) * 1000 )

	# TODO: On show/hide do a refresh?
	# TODO: How much to show at a time?

	def update_logs ( self, force=False ):
		if force or self.isVisible():
			entries = util.get_log_entries( 20, self.last_log )
			entries.reverse()
			for entry in entries:
				label = QtGui.QLabel( "%s | %s" % ( time.strftime( '%Y-%m-%d %H:%M:%S', time.localtime( entry[0] ) ), entry[1] ) )

				if entry[2] == util.LOG_INFO:
					label.setStyleSheet( "QWidget { background-color: #99FFFF; border-top: 1px solid #444444; }" )
				elif entry[2] == util.LOG_EVENT:
					label.setStyleSheet( "QWidget { background-color: #99FF99; border-top: 1px solid #444444; }" )
				elif entry[2] == util.LOG_WARN:
					label.setStyleSheet( "QWidget { background-color: #FFFF99; border-top: 1px solid #444444; }" )
				elif entry[2] == util.LOG_FATAL:
					label.setStyleSheet( "QWidget { background-color: #FF9999; border-top: 1px solid #444444; }" )
				else:
					label.setStyleSheet( "QWidget { background-color: #FFCC99; border-top: 1px solid #444444; }" )

				self.scroll.widget().box().insertWidget( 0, label );
				self.last_log = entry[0]

class SearchWindow ( BaseWindow ):
	def __init__ ( self, parent=None ):
		BaseWindow.__init__( self, parent );

		self.hide()

		self.setWindowTitle( "TagNest - Search" );
		self.resize( 500, 300 );

		hbox = QtGui.QHBoxLayout()
		vbox = QtGui.QVBoxLayout()
		vbox.addLayout( hbox )

		vbw = VBoxWrapper()
		vbw.show()

		self.scroll = QtGui.QScrollArea()
		self.scroll.setWidgetResizable( True );
		self.scroll.setVerticalScrollBarPolicy( QtCore.Qt.ScrollBarAlwaysOn );
		self.scroll.setHorizontalScrollBarPolicy( QtCore.Qt.ScrollBarAlwaysOff );
		self.scroll.setWidget( vbw )
		vbox.addWidget( self.scroll )

		self.button = QtGui.QPushButton( "Search" )
		hbox.addWidget( self.button )
		QtCore.QObject.connect( self.button, QtCore.SIGNAL( 'clicked()' ), self.search )

		self.query = QtGui.QLineEdit()
		hbox.addWidget( self.query )

		self.setLayout( vbox )

	def search ( self ):
		self.button.setEnabled( False )
		self.button.setText( "Searching..." )
		self.query.setEnabled( False )
		# TODO: Complete the searching piece here

class FileView ( QtGui.QVBoxLayout ):
	def __init__ ( self, args, row ):
		QtGui.QVBoxLayout.__init__( self, args )

		self.data = row

		self.nameLabel = QtGui.QLabel( row[1] )
		self.addWidget( self.nameLabel )
		self.pathLabel = QtGui.QLabel( row[2] )
		self.addWidget( self.pathLabel )

class NeedTagsWindow ( BaseWindow ):
	def __init__ ( self, parent=None ):
		BaseWindow.__init__( self, parent );

		self.hide()

		self.setWindowTitle( "TagNest - New" );
		self.resize( 500, 300 );

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
		self.timer.start( config.getint( 'GUI', 'needtagsrefresh' ) * 1000 )

	def update_list ( self, force=False ):
		if force or self.isVisible():
			pass
			#self.scroll.widget().box().insertWidget( 0, label );

class TagNest( QtGui.QApplication ):

	def __init__ ( self, args ):
		QtGui.QApplication.__init__( self, args )

		self.setWindowIcon( QtGui.QIcon( 'resource/icon.png' ) )

		self.daemon = None

		util.log( "GUI Started.", util.LOG_EVENT )
		util.log( "File root: %s" % ( config.get( 'Shared', 'fileroot' ) ), util.LOG_INFO )
		util.log( "Log refresh rate: %s" % ( config.getint( 'GUI', 'logrefresh' ) ), util.LOG_INFO )

		self.log_window = LogWindow()
		self.need_tags_window = NeedTagsWindow()
		self.search_window = SearchWindow()

		self.menu = QtGui.QMenu();

		self.daemon_control = self.menu.addAction( "" );
		self.connect( self.daemon_control, QtCore.SIGNAL( "triggered()" ), self.toggle_daemon );
		item = self.menu.addAction( "Search" );
		self.connect( item, QtCore.SIGNAL( "triggered()" ), self.search_window.show );
		item = self.menu.addAction( "Need Tags" );
		self.connect( item, QtCore.SIGNAL( "triggered()" ), self.need_tags_window.show );
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
			util.log( "Daemon found dead!", util.LOG_FATAL )
			util.log( "Restarting daemon.", util.LOG_WARN )
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
			util.log( "Daemon stopped by GUI.", util.LOG_EVENT )
		self.daemon_control.setText( "Start Daemon" )

	def start_daemon ( self ):
		if None == self.daemon:
			self.daemon = Process( target=daemon )
			self.daemon.start()
			util.log( "Daemon started by GUI.", util.LOG_EVENT )
		self.daemon_control.setText( "Stop Daemon" )

	def quit_clean( self ):
		self.stop_daemon()
		util.log( "GUI Stopped", util.LOG_EVENT )
		self.quit()

if __name__ == "__main__":

	config = ConfigParser.RawConfigParser()
	config.read( 'tagnest.config' )

	util = TagNestUtil( config.get( 'Shared', 'database' ) )

	app = TagNest( sys.argv );
	sys.exit( app.exec_() );