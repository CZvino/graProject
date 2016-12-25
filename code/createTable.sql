create table Artist
(
	artistId	char(15)	PRIMARY KEY,
	artistName	char(150)	NOT NULL,
)

create table Genre
(
	genreId		char(15)	PRIMARY KEY,
	genreName	char(15)	NOT NULL,
)

create table AppInformation
(
	trackId								char(15)		PRIMARY KEY,
	trackName							text			NOT NULL,
	trackCensoredName					text			NOT NULL,
	releaseDate							smalldatetime 	NOT NULL,
	primaryGenreId						char(15)		NOT NULL,
	genreIds							char(50)		NOT NULL,
	description							text,
	currency							char(10)		NOT NULL,
	price								smallmoney 		NOT NULL,
	isGameCenterEnabled					bit				NOT	NULL,
	fileSizeBytes						int				NOT NULL,
	languageCodesISO2A					text,
	userRatingCount						tinyint ,
	averageUserRating					float,
	trackContentRating					char(10),
	formattedPrice						char(50),
	wrapperType							char(20),
	supportedDevices					text,
	bundleId							char(200),
	minimumOsVersion					float,
	sellerName							char(100),
	artistId							char(15)		NOT NULL,
	contentAdvisoryRating				char(5),
	version								char(15),
	currentVersionReleaseDate			smalldatetime ,
	releaseNotes						text,
	userRatingCountForCurrentVersion	tinyint ,
	averageUserRatingForCurrentVersion	float,
	FOREIGN KEY(primaryGenreId)	REFERENCES Genre(genreId),
	FOREIGN KEY(artistId)	REFERENCES Artist(artistId),
)