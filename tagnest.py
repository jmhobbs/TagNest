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

import hashlib
import mimetypes
import pyPdf
import sqlite3
import time

class TagNestUtil:

	def __init__ ( self, database ):
		self.connection = sqlite3.connect( database )
		self.cursor = self.connection.cursor()

		self.LOG_INFO = 0
		self.LOG_EVENT = 1
		self.LOG_WARN = 2
		self.LOG_FATAL = 3

	def hash_file ( self, file, path ):
		f = open( path + "/" + file, 'rb')
		h = hashlib.sha1()
		h.update( f.read() )
		hash = h.hexdigest()
		f.close()
		return hash

	def hash_dir ( self, files, dirs ):
		h = hashlib.sha1()
		for file in files:
			h.update( file )
		for dir in dirs:
			h.update( dir )
		return h.hexdigest()

	def log ( self, message, level ):
		when = time.time()
		#print "%s: %s" % ( when, message )
		self.cursor.execute( "INSERT INTO log ( [datetime], [message], [level] ) VALUES ( ?, ?, ? )", ( when, message, level ) )
		self.connection.commit()

	def get_log_entries ( self, count, last ):
		self.cursor.execute( "SELECT datetime, message, level FROM log WHERE datetime > ? ORDER BY datetime DESC LIMIT 0,?", ( last, count ) )
		return self.cursor.fetchall()

	def get_dir_hash ( self, path ):
		self.cursor.execute( "SELECT hash FROM directory WHERE path = ?", ( path, ) )
		row = self.cursor.fetchone()
		if None == row:
			return ''
		else:
			return row[0]

	def set_dir_hash ( self, path, hash ):
		self.cursor.execute( "DELETE FROM directory WHERE path = ?" , ( path, ) )
		self.cursor.execute( "INSERT INTO directory ( path, hash ) VALUES ( ?, ? )", ( path, hash ) )
		self.connection.commit()

	def get_file_hash( self, file, path ):
		self.cursor.execute( "SELECT hash FROM file WHERE path = ? AND filename = ?", ( path, file ) )
		row = self.cursor.fetchone()
		if None == row:
			return ''
		else:
			return row[0]

	def touch_file( self, file, path ):
		self.cursor.execute( "UPDATE file SET missing = 0 WHERE filename = ? AND path = ?", ( file, path ) )
		self.connection.commit()

	def new_file( self, file, path, hash ):
		self.cursor.execute( "INSERT INTO file ( filename, path, hash, is_new ) VALUES ( ?, ?, ?, 'Y' )", ( file, path, hash ) )
		self.connection.commit()

	def update_file_hash( self, file, path, hash ):
		self.cursor.execute( "UPDATE file SET hash = ?, fulltext_state = 'P' WHERE filename = ? AND path = ?", ( hash, file, path ) )
		self.connection.commit()

	def get_files_in_dir( self, path ):
		self.cursor.execute( "SELECT filename FROM file WHERE path = ?", ( path, ) )
		r = []
		for row in self.cursor:
			r.append( row[0] )
		return r

	def mark_file_as_missing( self, file, path ):
		self.cursor.execute( "SELECT missing FROM file WHERE filename = ? AND path = ?", ( file, path ) )
		row = self.cursor.fetchone()
		missingcount = 1
		if '' != row[0] and None != row[0]:
			missingcount = row[0] + 1
		self.cursor.execute( "UPDATE file SET missing = ? WHERE filename = ? AND path = ?", ( missingcount, file, path ) )
		self.connection.commit()

	def get_missing_files( self ):
		self.cursor.execute( "SELECT filename, path, id FROM file WHERE missing > 2" )
		return self.cursor.fetchall()

	def delete_file( self, id ):
		self.cursor.execute( "DELETE FROM file WHERE id = ?", ( id, ) )
		self.connection.commit()

	def find_file_matches( self, file, hash ):
		self.cursor.execute( "SELECT filename, path, id FROM file WHERE filename = ? AND hash = ?", ( file, hash ) )
		rows = self.cursor.fetchall()
		if 0 != len( rows ):
			return rows

		self.cursor.execute( "SELECT filename, path, id FROM file WHERE hash = ?", ( hash, ) )
		rows = self.cursor.fetchall()
		if 0 != len( rows ):
			return rows

		self.cursor.execute( "SELECT filename, path, id FROM file WHERE filename = ?", ( file, ) )
		rows = self.cursor.fetchall()
		if 0 != len( rows ):
			return rows

		return None

	def move_file( self, id, file, path, hash ):
		self.cursor.execute( "UPDATE file SET filename = ?, path = ?, hash = ?, missing = 'N' WHERE id = ?", ( file, path, hash, id ) )
		self.connection.commit()

	def get_files_needing_tags ( self ):
		self.cursor.execute( "SELECT id, filename, path FROM file WHERE is_new = 'Y'" )
		return self.cursor.fetchall()

	def get_fulltext_from_file ( self, filename ):

		t = mimetypes.guess_type( filename )[0]

		r = ''

		if "text/plain" == t:
			f = open( filename, 'r' )
			r = f.read()
			f.close()
		elif "application/pdf" == t:
			pdf = pyPdf.PdfFileReader( open( filename, "rb" ) )
			for page in pdf.pages:
				r = r + page.extractText()

		return r