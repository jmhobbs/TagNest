# -*- coding: utf-8 -*-

# Polling is the only thing we can do cross platform right now

# Psuedo-Code
#1) Walk tree
#2) Look for new files & changes to directories
#3) On new file or directory, look for matching hashes
#4) If you find a matching hash, check to see if it is still there
#5) If it is, then you flag a duplicate
#6) If it isn't, then execute a move
#7) Run through the DB and look for files marked for deletion, delete them
#7) Repeat

from tagnest import WalkerUtil
import time
import os

	walker = WalkerUtil( "tagnest.db3" )

#while True:
	for path, dirs, files in os.walk( 'files/' ):
		dh = walker.hash_dir( files, dirs )
		ch = walker.get_dir_hash( path )
		print "Checking hash for %s, db says it is %s" % ( path, ch )
		if dh != ch:
			print "Setting hash for %s to %s" % ( path, dh )
			walker.set_dir_hash( path, dh )

		FilesInDir = walker.get_files_in_dir( path )
		for file in files:
			try:
				FilesInDir.remove( file )
			except:
				pass
			fh = walker.hash_file( file, path )
			ch = walker.get_file_hash( file, path )
			print "%s - %s : %s" % ( file, fh, ch )
			if '' == ch:
				matches = walker.find_file_matches( file, fh )
				if None == matches:
					walker.new_file( file, path, fh )
				else:
					for pmatch in matches:
						if False == os.path.isfile( pmatch[1] + "/" + pmatch[0]):
							print "Found a moved copy of %s, moving it." % ( file )
							walker.move_file( pmatch[2], file, path, fh )
							break
			elif fh != ch:
				walker.update_file_hash( file, path, fh )
			else
				walker.touch_file( file, path )

		for file in FilesInDir:
			print "Missing file:", file
			walker.mark_file_as_missing( file, path )

	walker.clear_missing_files()