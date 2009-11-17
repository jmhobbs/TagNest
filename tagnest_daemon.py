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

from tagnest import TagNestUtil
import time
import os


def run():
	util = TagNestUtil( "tagnest.db3" ) # TODO: Config this?
	while True:
		start_time = time.time()
		for path, dirs, files in os.walk( 'files/' ):
			dh = util.hash_dir( files, dirs )
			ch = util.get_dir_hash( path )
			if dh != ch:
				util.log( "Daemon: Directory has changed, " + path, util.LOG_INFO )
				util.set_dir_hash( path, dh )

			FilesInDir = util.get_files_in_dir( path )
			for file in files:
				try:
					FilesInDir.remove( file )
				except:
					pass
				fh = util.hash_file( file, path )
				ch = util.get_file_hash( file, path )
				if '' == ch:
					matches = util.find_file_matches( file, fh )
					if None == matches:
						util.log( "Daemon: New file, %s/%s" % ( path, file ), util.LOG_INFO )
						util.new_file( file, path, fh )
					else:
						for pmatch in matches:
							if False == os.path.isfile( pmatch[1] + "/" + pmatch[0]):
								util.log( "Daemon: Moving %s from %s/%s to %s/%s." % ( pmatch[2], pmatch[1], pmatch[0], path, file ), util.LOG_WARN )
								util.move_file( pmatch[2], file, path, fh )
								break
				elif fh != ch:
					util.update_file_hash( file, path, fh )
				else:
					util.touch_file( file, path )

			for file in FilesInDir:
				util.log( "Daemon: Missing file, %s/%s" % ( path, file ), util.LOG_WARN )
				util.mark_file_as_missing( file, path )

		missing = util.get_missing_files()
		for file in missing:
			if False == os.path.isfile( pmatch[1] + pmatch[0]):
				util.log( "Daemon: Deleting entry for missing file, %s/%s" % ( pmatch[1], pmatch[0] ), util.LOG_WARN )
				util.delete_file( pmatch[2] )
			else:
				util.touch_file( file, path )

		end_time = time.time()
		util.log( "Daemon: Finished walk in %s seconds." % ( end_time - start_time ), util.LOG_INFO )

		time.sleep( 60 ) # TODO: Config this

if __name__ == "__main__":
	run()