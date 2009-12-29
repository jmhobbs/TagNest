BEGIN TRANSACTION;
CREATE TABLE directory ( path, hash );
/*! fulltext_state flags: P - Pending, C - Complete, B - Bad MIME Type */
CREATE TABLE file ( id INTEGER PRIMARY KEY, hash, filename, path, has_clones, is_new, fulltext_state, missing );
CREATE TABLE fulltext ( file_id , fulltext );
CREATE TABLE tag ( file_id, tag );
CREATE TABLE [log] ( [id] INTEGER PRIMARY KEY, [datetime], [message], [level] );
COMMIT;
