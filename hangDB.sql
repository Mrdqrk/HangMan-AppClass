use hangDb;
-- Players table 
CREATE TABLE players (
    playerId INT PRIMARY KEY AUTO_INCREMENT,
    playerName VARCHAR(100) NOT NULL,
    Comp BOOLEAN DEFAULT FALSE
);

-- Phrases table 
CREATE TABLE phrases (
    phraseId INT PRIMARY KEY AUTO_INCREMENT,
    phraseText VARCHAR(255) NOT NULL,
    category VARCHAR(100),
    difficulty ENUM('easy','medium','hard') DEFAULT 'medium'
);

-- Games table 
CREATE TABLE games (
    gameId INT PRIMARY KEY AUTO_INCREMENT,
    phraseId INT NOT NULL,
    startTime TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    endTime TIMESTAMP NULL,
    status ENUM('in_progress','won','lost','draw') DEFAULT 'in_progress',
    bodyParts INT DEFAULT 0,   -- how many parts are currently drawn
    FOREIGN KEY (phraseId) REFERENCES phrases(phraseId)
);

-- GamePlayers table 
CREATE TABLE gamePlayers (
    gamePlayerId INT PRIMARY KEY AUTO_INCREMENT,
    gameId INT NOT NULL,
    playerId INT NOT NULL,
    score INT DEFAULT 0,
    FOREIGN KEY (gameId) REFERENCES games(gameId),
    FOREIGN KEY (playerId) REFERENCES players(playerId)
);

-- Guesses table 
CREATE TABLE guesses (
    guessId INT PRIMARY KEY AUTO_INCREMENT,
    gameId INT NOT NULL,
    playerId INT NOT NULL,
    guessedLetter CHAR(1) NOT NULL,
    correct BOOLEAN NOT NULL,
    streakCount INT DEFAULT 0,  -- track consecutive correct guesses
    guessTime TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (gameId) REFERENCES games(gameId),
    FOREIGN KEY (playerId) REFERENCES players(playerId)
);

--  PowerMoves table (when streakCount = 2, player can add/remove a body part)
CREATE TABLE powerMoves (
    powerId INT PRIMARY KEY AUTO_INCREMENT,
    gameId INT NOT NULL,
    playerId INT NOT NULL,
    action ENUM('add','remove') NOT NULL,
    partAffected VARCHAR(50),
    moveTime TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (gameId) REFERENCES games(gameId),
    FOREIGN KEY (playerId) REFERENCES players(playerId)
);

--  BodyParts reference table
CREATE TABLE bodyParts (
    partId INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(50) NOT NULL
);

-- Insert default body parts
INSERT INTO bodyParts (name) VALUES
('head'),('torso'),('leftArm'),('rightArm'),('leftLeg'),('rightLeg');

-- Insert default players 
INSERT INTO players (playerName, Comp) VALUES
('Human Player', FALSE),
('Computer Opponent', TRUE);

-- Insert sample phrases
INSERT INTO phrases (phraseText, category, difficulty) VALUES
('May the Force be with you', 'pixar', 'easy');
