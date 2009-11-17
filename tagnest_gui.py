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

import sys
from PyQt4 import QtCore, QtGui

from multiprocessing import Process, freeze_support

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

class LogWindow ( BaseWindow ):
	def __init__ ( self, parent=None ):
		BaseWindow.__init__( self, parent );
		self.setWindowTitle( "TagNest Log" );
		aboutLabel = QtGui.QLabel();
		aboutLabel.setText( "Log!" );
		vbox = QtGui.QVBoxLayout();
		vbox.addWidget( aboutLabel )
		self.setLayout( vbox )

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