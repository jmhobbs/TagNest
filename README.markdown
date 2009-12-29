# TagNest #
TagNest is an experimental project to monitor, tag, and search files in a directory.

I am writing this for personal use, but feel free to tinker, use and contribute.

TagNest will not edit your files or directories, it just sets up a database that monitors and tags/indexes them for you to search.

## Status ##
TagNest currently has a working release, at commit <tt>fa5008920dcace5a23e77e3113149f9aba509149</tt>.  Content indexing is not active in this release, but tagging is.

## Screen Shots ##

### Log Window ###
![v0.1 Log Window](http://github.com/jmhobbs/TagNest/raw/master/screens/0.1/log.jpg)

### System Tray ###
![v0.1 System Tray](http://github.com/jmhobbs/TagNest/raw/master/screens/0.1/tray.jpg)

### Files Needing Tags ###
![v0.1 Files Needing Tags](http://github.com/jmhobbs/TagNest/raw/master/screens/0.1/new.jpg)

### Search ###
![v0.1 Search](http://github.com/jmhobbs/TagNest/raw/master/screens/0.1/search.jpg)

## Design ##

TagNest is implemented in two pieces, the daemon and the GUI.

The daemon can run stand alone, or as a child of the GUI. It indexes the files, watching for changes in content and location.

The daemon marks files for the GUI to display as needing tag information.

All indexing is done with SHA1 hashes of the file or directory structure. This is pretty fast, which is important because at the moment I am using brute-force timed polling.

In the future I plan to add a full-text search feature for various file types. Some of this is already in place.

## What it runs on ##
TagNest should run on anything that supports PyQt4. So Mac, Windows and Linux.

TagNest currently depends on:

  - Python (with sqlite3)
  - PyQt4
  - pyPdf
