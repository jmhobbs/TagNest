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

# Hello intrepid source reader! Just wanted to let you know, that it seems like
# polling is the only thing we can do cross platform right now. If you have
# suggestions or patches, please get in touch!

# Update: QFileSystemWatcher?

from tagnest import TagNestUtil
import time
import os
import ConfigParser

def run ( config ):

	util = TagNestUtil( config.get( 'Shared', 'database' ) )

	util.log( "Index Daemon: File root: %s" % ( config.get( 'Shared', 'fileroot' ) ), util.LOG_INFO )
	util.log( "Index Daemon: Refresh interval: %s" % ( config.getint( 'IndexDaemon', 'sleep' ) ), util.LOG_INFO )

	while True:
		pending = util.get_files_pending_index()

		for row in pending:
			print '-----[ %s/%s ]-----' % ( row['path'], row['filename'] )
			ft = util.get_fulltext_from_file( '%s/%s' % ( row['path'], row['filename'] ) )
			if None == ft:
				util.mark_file_as_bad_mime_type( row['id'] )
			else:
				ftlist = ft.split( ' ' )
				del ft
				rtlist = [item for item in ftlist if len( item ) > 5]
				# TODO: All kinds of super awesome filtering here!
				del ftlist
				ft = ' '.join( rtlist )
				del rtlist
				util.set_file_fulltext( row['id'], ft )

		time.sleep( config.getint( 'IndexDaemon', 'Sleep' ) )

if __name__ == "__main__":
	config = ConfigParser.RawConfigParser()
	config.read( 'tagnest.config' )
	run( config )
