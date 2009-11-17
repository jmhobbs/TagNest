BEGIN TRANSACTION;
CREATE TABLE directory ( path, hash );
CREATE TABLE file ( id INTEGER PRIMARY KEY, hash, filename, path, has_clones, is_new, fulltext_state, missing );
CREATE TABLE fulltext ( file_id , fulltext );
CREATE TABLE tag ( file_id, tag );
COMMIT;
