-- Creating the table for valid countries
CREATE TABLE IF NOT EXISTS Countries (
    CountryID SERIAL PRIMARY KEY,
    CountryName VARCHAR(255) UNIQUE NOT NULL
);

-- Inserting some sample countries into the Countries table
INSERT INTO Countries (CountryName) VALUES
    ('Country1'),
    ('Country2'),
    ('Country3');

CREATE TABLE IF NOT EXISTS Genres (
    GenreID SERIAL PRIMARY KEY,
    GenreName VARCHAR(255) UNIQUE NOT NULL
);

INSERT INTO Genres (GenreName) VALUES
    ('Hip-hop'),
    ('Rock'),
    ('Classic');

-- Creating the table for music artists
CREATE TABLE IF NOT EXISTS MusicArtists (
    ArtistID SERIAL PRIMARY KEY,
    ArtistName VARCHAR(255) NOT NULL,
    CountryID INTEGER REFERENCES Countries(CountryID),
    FormationYear DATE CHECK (FormationYear >= '1900-01-01' AND FormationYear <= CURRENT_DATE),
    RecordLabel VARCHAR(255)
);

-- Creating an index for the ArtistName field in the MusicArtists table
CREATE INDEX idx_artist_name ON MusicArtists (ArtistName);

-- Creating the table for music albums
CREATE TABLE IF NOT EXISTS MusicAlbums (
    AlbumID SERIAL PRIMARY KEY,
    AlbumName VARCHAR(255) NOT NULL,
    ReleaseYear DATE CHECK (ReleaseYear >= '1900-01-01' AND ReleaseYear <= CURRENT_DATE) NOT NULL,
    GenreID INTEGER REFERENCES Genres(GenreID),
    Duration DECIMAL(5,2) CHECK (Duration > 0.)
);

-- Creating indexes for fields in the MusicAlbums table
CREATE INDEX idx_album_name ON MusicAlbums (AlbumName);
CREATE INDEX idx_release_year ON MusicAlbums (ReleaseYear);

-- Creating the junction table for the many-to-many relationship
CREATE TABLE IF NOT EXISTS ArtistAlbumRelationship (
    RelationshipID SERIAL PRIMARY KEY,
    ArtistID INTEGER REFERENCES MusicArtists(ArtistID) ON DELETE CASCADE,
    AlbumID INTEGER REFERENCES MusicAlbums(AlbumID) ON DELETE CASCADE
);

-- Creating indexes for fields in the ArtistAlbumRelationship table
CREATE INDEX idx_artist_relationship ON ArtistAlbumRelationship (ArtistID);
CREATE INDEX idx_album_relationship ON ArtistAlbumRelationship (AlbumID);

-- Inserting data into the MusicArtists table
INSERT INTO MusicArtists (ArtistName, CountryID, FormationYear, RecordLabel)
VALUES
    ('Artist1', 1, '2000-01-01', 'Label1'),
    ('Artist2', 2, '1995-03-15', 'Label2'),
    ('Artist3', 3, '2005-07-20', 'Label3');

-- Inserting data into the MusicAlbums table
INSERT INTO MusicAlbums (AlbumName, ReleaseYear, GenreID, Duration)
VALUES
    ('Album1', '2002-05-10', 1, 45.5),
    ('Album2', '1998-11-22', 1, 30.8),
    ('Album3', '2007-08-14', 2, 52.2);

-- Inserting data into the ArtistAlbumRelationship table
INSERT INTO ArtistAlbumRelationship (ArtistID, AlbumID)
VALUES
    (1, 1),
    (2, 2),
    (3, 3);
