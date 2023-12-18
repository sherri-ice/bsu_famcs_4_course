-- Creating the table for music artists
CREATE TABLE IF NOT EXISTS MusicArtists (
    ArtistID SERIAL PRIMARY KEY,
    ArtistName VARCHAR(255) NOT NULL,
    Country VARCHAR(255) NOT NULL,
    FormationYear DATE CHECK (FormationYear >= '1900-01-01' AND FormationYear <= CURRENT_DATE),
    RecordLabel VARCHAR(255)
);

-- Creating an index for the ArtistName field in the MusicArtists table
CREATE INDEX idx_artist_name ON MusicArtists (ArtistName);

-- Creating the table for music albums
CREATE TABLE IF NOT EXISTS MusicAlbums (
    AlbumID SERIAL PRIMARY KEY,
    AlbumName VARCHAR(255) NOT NULL,
    ArtistID SERIAL REFERENCES MusicArtists(ArtistID),
    ReleaseYear DATE CHECK (ReleaseYear >= '1900-01-01' AND ReleaseYear <= CURRENT_DATE) NOT NULL,
    Genre VARCHAR(255),
    Duration DECIMAL(5,2) CHECK (Duration > 0.)
);

-- Creating indexes for fields in the MusicAlbums table
CREATE INDEX idx_album_name ON MusicAlbums (AlbumName);
CREATE INDEX idx_release_year ON MusicAlbums (ReleaseYear);

-- Inserting data into the MusicArtists table
INSERT INTO MusicArtists (ArtistName, Country, FormationYear, RecordLabel)
VALUES
    ('Artist1', 'USA', '2000-01-01', 'Label1'),
    ('Artist2', 'France', '1995-03-15', 'Label2'),
    ('Artist3', 'Japan', '2005-07-20', 'Label3');

-- Inserting data into the MusicAlbums table
INSERT INTO MusicAlbums (AlbumName, ReleaseYear, ArtistID, Genre, Duration)
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

