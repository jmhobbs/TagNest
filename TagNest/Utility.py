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
import os

class Logger:

	def __init__ ( self, database ):
		self.connection = sqlite3.connect( database )
		self.cursor = self.connection.cursor()

		self.LOG_INFO = 0
		self.LOG_EVENT = 1
		self.LOG_WARN = 2
		self.LOG_FATAL = 3

	def log ( self, message, level ):
		when = time.time()
		self.cursor.execute( "INSERT INTO log ( [datetime], [message], [level] ) VALUES ( ?, ?, ? )", ( when, message, level ) )
		self.connection.commit()

	def get_entries ( self, count, last ):
		self.cursor.execute( "SELECT datetime, message, level FROM log WHERE datetime > ? ORDER BY datetime DESC LIMIT 0,?", ( last, count ) )
		return self.cursor.fetchall()

def Hash ( path ):
	if os.path.isfile( path ):
		f = open( path, 'rb')
		h = hashlib.sha1()
		h.update( f.read() )
		hash = h.hexdigest()
		f.close()
		return hash
	else:
		h = hashlib.sha1()
		h.update( path )
		for entry in os.listdir( path ):
			h.update( entry )
		return h.hexdigest()
