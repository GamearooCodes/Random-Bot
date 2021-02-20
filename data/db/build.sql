CREATE TABLE IF NOT EXISTS exp (
	UserID integer PRIMARY KEY,
	Username text DEFAULT NULL,
	XP integer DEFAULT 0,
	Level integer DEFAULT 0,
	XPLock text DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS Guilds (
    guildId VARCHAR(100) NOT NULL PRIMARY KEY,
    guildName VARCHAR(100) DEFAULT NULL,
	prefix VARCHAR(10) DEFAULT NULL
);
