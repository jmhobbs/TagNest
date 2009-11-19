# -*- coding: utf-8 -*-

class Directory:

	def __init__ ( self, path ):
		self.path = path

	def get_stored_hash ( self, path ):
		self.cursor.execute( "SELECT hash FROM directory WHERE path = ?", ( path, ) )
		row = self.cursor.fetchone()
		if None == row:
			return ''
		else:
			return row[0]

	def set_stored_hash ( self, path, hash ):
		self.cursor.execute( "DELETE FROM directory WHERE path = ?" , ( path, ) )
		self.cursor.execute( "INSERT INTO directory ( path, hash ) VALUES ( ?, ? )", ( path, hash ) )
		self.connection.commit()

	def get_files_in_dir( self, path ):
		self.cursor.execute( "SELECT filename FROM file WHERE path = ?", ( path, ) )
		r = []
		for row in self.cursor:
			r.append( row[0] )
		return r

class File:

	def __init__ ( self, filename, path ):
		self.filename = filename
		self.path = path
		self.fullpath = path + '/' + filename

	def get_stored_hash( self, file, path ):
		self.cursor.execute( "SELECT hash FROM file WHERE path = ? AND filename = ?", ( path, file ) )
		row = self.cursor.fetchone()
		if None == row:
			return ''
		else:
			return row[0]

	def set_stored_hash ( self, file, path, hash ):
		self.cursor.execute( "UPDATE file SET hash = ?, fulltext_state = 'P' WHERE filename = ? AND path = ?", ( hash, file, path ) )
		self.connection.commit()

	def touch ( self, file, path ):
		self.cursor.execute( "UPDATE file SET missing = 0 WHERE filename = ? AND path = ?", ( file, path ) )
		self.connection.commit()

	def save ( self, file, path, hash ):
		self.cursor.execute( "INSERT INTO file ( filename, path, hash, is_new ) VALUES ( ?, ?, ?, 'Y' )", ( file, path, hash ) )
		self.connection.commit()

	def mark_missing ( self, file, path ):
		self.cursor.execute( "SELECT missing FROM file WHERE filename = ? AND path = ?", ( file, path ) )
		row = self.cursor.fetchone()
		missingcount = 1
		if '' != row[0] and None != row[0]:
			missingcount = row[0] + 1
		self.cursor.execute( "UPDATE file SET missing = ? WHERE filename = ? AND path = ?", ( missingcount, file, path ) )
		self.connection.commit()

	@staticmethod
	def get_missing_files( self ):
		self.cursor.execute( "SELECT filename, path, id FROM file WHERE missing > 2" )
		return self.cursor.fetchall()

	def delete ( self, id ):
		self.cursor.execute( "DELETE FROM file WHERE id = ?", ( id, ) )
		self.connection.commit()

	def find_similar ( self, file, hash ):
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

	def move ( self, id, file, path, hash ):
		self.cursor.execute( "UPDATE file SET filename = ?, path = ?, hash = ?, missing = 'N' WHERE id = ?", ( file, path, hash, id ) )
		self.connection.commit()

	@staticmethod
	def get_files_needing_tags ( self ):
		self.cursor.execute( "SELECT id, filename, path FROM file WHERE is_new = 'Y'" )
		ret = []
		for row in self.cursor.fetchall():
			ret.append( { 'id': row[0], 'filename': row[1], 'path': row[2], 'tags': [] } )
		return ret

	def search_for_files ( self, query ):
		words = str( query ).split( ' ' )
		t = []
		q = "SELECT id, filename, path FROM file WHERE "
		for word in words:
			if '' == word:
				continue
			q = q + "filename LIKE ? OR "
			t.append( '%' + word + '%' )

		q = q[:-3]

		self.cursor.execute( q, t )
		ret = []
		for row in self.cursor.fetchall():
			ret.append( { 'id': row[0], 'filename': row[1], 'path': row[2], 'tags': [] } )

		return ret

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