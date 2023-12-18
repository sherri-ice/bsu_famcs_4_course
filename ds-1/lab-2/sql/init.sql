-- Creating the table for music artists
CREATE TABLE IF NOT EXISTS music_artists (
    artist_id SERIAL PRIMARY KEY,
    artist_name VARCHAR(255) NOT NULL,
    country VARCHAR(255) NOT NULL,
    formation_year DATE CHECK (formation_year >= '1900-01-01' AND formation_year <= CURRENT_DATE),
    record_label VARCHAR(255)
);

CREATE INDEX idx_artist_name ON music_artists (artist_name);

-- Creating the table for music albums
CREATE TABLE IF NOT EXISTS music_albums (
    album_id SERIAL PRIMARY KEY,
    album_name VARCHAR(255) NOT NULL,
    artist_id SERIAL REFERENCES music_artists(artist_id),
    release_year DATE CHECK (release_year >= '1900-01-01' AND release_year <= CURRENT_DATE) NOT NULL,
    genre VARCHAR(255),
    duration DECIMAL(5,2) CHECK (duration > 0.)
);

CREATE INDEX idx_album_name ON music_albums (album_name);

-- Inserting data into the MusicArtists table
INSERT INTO music_artists (artist_name, country, formation_year, record_label)
VALUES
    ('Artist1', 'USA', '2000-01-01', 'Label1'),
    ('Artist2', 'France', '1995-03-15', 'Label2'),
    ('Artist3', 'Japan', '2005-07-20', 'Label3');

-- Inserting data into the MusicAlbums table
INSERT INTO music_albums (album_name, release_year, artist_id, Genre, Duration)
VALUES
    ('Album1', '2002-05-10', 1, 'Hip-Hop', 45.5),
    ('Album2', '1998-11-22', 2, 'Rock', 30.8),
    ('Album3', '2007-08-14', 3, 'Pop', 52.2);


CREATE VIEW foreign_key_info_view AS
SELECT
    conname AS constraint_name,
    conrelid::regclass AS table_name,
    a.attname AS column_name,
    confrelid::regclass AS foreign_table_name,
    af.attname AS foreign_column_name
FROM
    pg_constraint c
JOIN
    pg_attribute a ON a.attnum = ANY(c.conkey) AND a.attrelid = c.conrelid
JOIN
    pg_attribute af ON af.attnum = ANY(c.confkey) AND af.attrelid = c.confrelid;


CREATE VIEW public_tables_view AS
SELECT table_name
FROM information_schema.tables
WHERE table_schema = 'public' AND table_type = 'BASE TABLE';

CREATE TABLE table_names_aliases (
    table_name VARCHAR(255) NOT NULL,
    key_column VARCHAR(255) NOT NULL,
    actual_name_column VARCHAR(255) NOT NULL
);

INSERT INTO table_names_aliases (table_name, key_column, actual_name_column)
VALUES
    ('music_albums', 'album_id', 'album_name'),
    ('music_artists', 'artist_id', 'artist_name');