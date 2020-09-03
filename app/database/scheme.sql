DROP TABLE IF EXISTS Admin;
DROP TABLE IF EXISTS Document CASCADE;
DROP TABLE IF EXISTS Party;
DROP TABLE IF EXISTS Legal_Text;
DROP TABLE IF EXISTS Separator CASCADE;
DROP TABLE IF EXISTS Sentence;

CREATE TABLE Admin (
  id SERIAL PRIMARY KEY,
  username TEXT UNIQUE NOT NULL,
  password TEXT NOT NULL
);

CREATE TABLE Document (
  id SERIAL PRIMARY KEY,
  file_number VARCHAR NOT NULL,
  decision_date VARCHAR,
  subject VARCHAR,
  principle VARCHAR
);

CREATE TABLE Party (
  id SERIAL,
  document_id INTEGER NOT NULL,
  party_name VARCHAR NOT NULL,
  FOREIGN KEY (document_id) REFERENCES Document (id) ON DELETE CASCADE,
  PRIMARY KEY (id, document_id, party_name)
);

CREATE TABLE Legal_Text (
  id SERIAL,
  document_id INTEGER NOT NULL,
  text VARCHAR NOT NULL,
  FOREIGN KEY (document_id) REFERENCES Document (id) ON DELETE CASCADE,
  PRIMARY KEY (id, document_id, text)
);

CREATE TABLE Separator (
  id SERIAL PRIMARY KEY,
  expression VARCHAR UNIQUE NOT NULL
);

CREATE TABLE Sentence (
  id SERIAL PRIMARY KEY,
  document_id INTEGER NOT NULL,
  separator_id INTEGER NOT NULL,
  position_ INTEGER NOT NULL,
  content VARCHAR NOT NULL,
  score FLOAT NOT NULL,
  included VARCHAR NOT NULL,
  FOREIGN KEY (document_id) REFERENCES Document (id) ON DELETE CASCADE,
  FOREIGN KEY (separator_id) REFERENCES Separator (id) ON DELETE CASCADE
);