CREATE TABLE IF NOT EXISTS music_awards (
    record_id SERIAL PRIMARY KEY,
    award_name VARCHAR(255) NOT NULL,
    artist_id SERIAL REFERENCES music_artists(artist_id),
    date DATE CHECK (date >= '1900-01-01' AND date <= CURRENT_DATE) NOT NULL
);

INSERT INTO music_awards (award_name, artist_id, date)
VALUES
    ('Award1', 1, '2000-01-01'),
    ('Award2', 3, '2001-01-01'),
    ('Award3', 2, '2001-12-01');

INSERT INTO table_names_aliases (table_name, key_column, actual_name_column)
VALUES
    ('music_awards', 'record_id', 'award_name');