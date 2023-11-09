DROP TABLE IF EXISTS surveys;
DROP TABLE IF EXISTS last_response_set;

DROP TABLE IF EXISTS questions;
DROP TABLE IF EXISTS responses;

CREATE TABLE surveys (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    descr TEXT
);

CREATE TABLE questions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    in_survey INTEGER NOT NULL, -- The ID of the survey which this question is in
    position INTEGER NOT NULL,

    title TEXT NOT NULL,
    descr TEXT,

    qtype TEXT NOT NULL, -- RADIO, INTEGER, STRING, COUNTRY

    -- qtype specifics
    radio_options TEXT,
    integer_lb INTEGER, -- lower bound
    integer_ub INTEGER -- upper bound
);

CREATE TABLE responses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    question_id INTEGER NOT NULL, -- The ID of the question to which this is a response
    response_set INTEGER NOT NULL, -- Sort of like a session id

    answer TEXT
);

CREATE TABLE last_response_set (id INTEGER);

INSERT INTO last_response_set (id) VALUES (0);
INSERT INTO surveys (title, descr) VALUES ('Test Survey 1', 'This is the description of the survey. You can write anything here that you want!');
INSERT INTO questions (in_survey, position, title, descr, qtype, radio_options)
    VALUES (1, 0, 'What''s your favourite of these foods?', 'Or vegetable...', 'RADIO', 'Apple;Banana;Cauliflower;Potato;Chips');
INSERT INTO questions (in_survey, position, title, descr, qtype)
    VALUES (1, 1, 'What''s your name?', 'First and last!', 'STRING');
INSERT INTO questions (in_survey, position, title, descr, qtype, integer_lb, integer_ub)
    VALUES (1, -1, 'How old are you?', 'In years.', 'INTEGER', 0, 150);
INSERT INTO surveys (title, descr) VALUES ('Another Survey', 'This survey is a bit shorter than the other one...');
INSERT INTO questions (in_survey, position, title, descr, qtype, radio_options)
    VALUES (2, 0, 'How much do you like this survey?', 'It''s okay, you can tell us.', 'RADIO', 'Not at all;It''s okay;Somewhat;Very fun!');
