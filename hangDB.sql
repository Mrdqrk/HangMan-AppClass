CREATE DATABASE hangDb; 

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
('Hog killing time','cowboy','easy'),
('This town aint big enough for the two of us','cowboy','hard'),
('Hi-yo Sivler! Away','cowboy', 'hard'),
('Dumber than a box of rocks', 'cowboy', 'medium'),
('Vengence is an idiots game', 'cowboy', 'hard'),
('Git along now', 'cowboy', 'medium'),
('Much obliged, partner', 'cowboy', 'easy'),
('Easy pickings', 'cowboy', 'easy'),
('Hold your horses', 'cowboy', 'easy'),
('Saddle up', 'cowboy', 'easy')
('Yeehaw', 'cowboy', 'easy')
('Theres a snake in my boot', 'pixar', 'easy'),
('I am speed', 'pixar', 'easy'),
('Just keep swimming', 'pixar', 'easy'),
('To infinity, and beyond','pxiar','easy'),
('I’ll be shooting for my own hand', 'pixar', 'hard'),
('He touched the butt', 'pixar', 'medium'),
('Adventure is out there', 'pixar', 'medium'),
('No capes','pixar', 'easy'),
('Where is my super suit?', 'pixar', 'medium'),
('Anyone can cook', 'pixar', 'hard'),
('This is falling with style', 'pixar', 'hard'),
('You are a toy', 'pixar', 'medium'),
('You’re my favorite deputy', 'pixar', 'easy'),
('Reach for the sky', 'pixar', 'medium'),
('The claw','pixar', 'easy'),
('I’m watching you, Wazowski','pixar', 'medium'),
('The wilderness must be explored','pixar', 'hard'),
('Silencio Bruno', 'pixar', 'hard'),
('I’m a beautiful butterfly', 'pixar', 'hard'),
('The circle of life', 'pixar', 'medium'),
('Long live the king','pixar','medium'),
('TLDR', 'social', 'easy'),
('Keyboard Cat', 'social', 'easy'),
('Mama a girl behind you','social','easy'),
('Do not come to my town','social','hard'),
('Oh man not my house','social','hard'),
('What did I do','social','medium'),
('It’s giving','social','easy'),
('Main character energy','social','medium'),
('Girl dinner','social','medium'),
('She ate','social','medium'),
('Left no crumbs','social', 'medium'),
('It’s corn!','social','easy'),
('Let him cook','social', 'medium'),
('Delulu','social', 'easy'),
('Not the vibe','social','hard'),
('You understood the assignment','social','medium'),
('That’s cap','social','easy'),
('Periodt','social','easy'),
('I am kenough','social','medium'),
('Out of pocket','social','hard'),
('That’s suspicious','social','easy'),
('Bombastic side eye','social','hard'),
('Sheesh','social','easy'),
('Five big booms','social','medium'),
('I’m baby','social','medium'),
('Touch grass','social','easy'),
('Like a Cowboy','music','hard'),
('I’m Still Standing','music','medium'),
('Never Gonna Give You Up','music','easy'),
('Everyday I’m Shufflin','music','easy'),
('How Life Goes','music','medium')
('Hello, from the other side','music','medium'),
('Can you pay my automobile bills','music','hard'),
('You need some loving, TLC','music','medium'),
('I’ve been afraid of changing','music','hard'),
('Made from love','music','medium'),
('Young and sweet, only seventeen','music','medium'),
('Let’s have a party','music','easy'),
('Take me home, country road','music','easy'),
('I can breathe for the first time','music','medium'),
('Wake me up before you go-go','music','easy'),
('Life in plastic, it’s fantastic','music','medium'),
('Hey now, you’re an all-star','music','easy'),
('You’re like pelican fly','music','hard'),
('Hold on to the feeling','music','easy'),
('In an earlier round','music','hard'),
('It was only a kiss','music','medium'),
('I wanna be close to you','music','medium'),
('Cry because it’s over','music','medium'),
('Like I’m born to be','music','medium'),
('You can take me hot to go','music','medium'),
('We should stick together','music','medium');
