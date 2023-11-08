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
INSERT INTO surveys (title, descr) VALUES ('My Cool Survey', 'This is just a test...');
INSERT INTO questions (in_survey, position, title, descr, qtype, radio_options)
    VALUES (1, 0, 'What''s your favourite fruit?', 'Or vegetable...', 'RADIO', 'Apple;Banana;Cauliflower');
INSERT INTO questions (in_survey, position, title, descr, qtype)
    VALUES (1, 1, 'What''s your name?', 'First and last!', 'STRING');
INSERT INTO questions (in_survey, position, title, descr, qtype, integer_lb, integer_ub)
    VALUES (1, -1, 'How old are you?', 'In years.', 'INTEGER', 0, 150);
INSERT INTO surveys (title, descr) VALUES ('Another Survey', 'For some new information!');
INSERT INTO questions (in_survey, position, title, descr, qtype, radio_options)
    VALUES (2, 0, 'How much do you like this survey?', 'It''s okay, you can tell us.', 'RADIO', 'Not at all;It''s okay;What''s a survey?;I''ve never known anything to be as enjoyable!');