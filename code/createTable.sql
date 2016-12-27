create table Artist
(
    artistId                            char(15)        PRIMARY KEY,
    artistName                          char(150)       NOT NULL,
)

create table Genre
(
    genreId                             char(4)         PRIMARY KEY,
    genreName                           char(15)        NOT NULL,
)

create table Advisory
(
    advisoryId                          char(4)         PRIMARY KEY,
    advisoryContent                     text            NOT NULL,
)

create table AppInformation
(
    trackId                             char(15)        PRIMARY KEY,
    trackName                           nchar(150)      NOT NULL,
    bundleId                            char(150)       NOT NULL,

    releaseDate                         smalldatetime   default '1970-01-01 00:00:00',
    userRatingCount                     int             default '0',
    averageUserRating                   decimal(2, 1)   default '0.0',

    currency                            char(5)         default 'None',
    formattedPrice                      char(50)        default 'None',
    price                               smallmoney      default '0',

    fileSizeBytes                       int             default '0',

    wrapperType                         char(20),
    isGameCenterEnabled                 bit             default 'False',
    isVppDeviceBasedLicensingEnabled    bit             default 'False',

    minimumOsVersion                    char(10)        default '0.0',
    supportedDevices                    text,

    primaryGenreId                      char(4)         NOT NULL,
    genreIds                            char(50)        NOT NULL,

    description                         text,

    languageCodesISO2A                  text,

    version                             char(15),
    currentVersionReleaseDate           smalldatetime   default '1970-01-01 00:00:00',
    userRatingCountForCurrentVersion    int             default '0',
    averageUserRatingForCurrentVersion  decimal(2, 1)   default '0.0',
    releaseNotes                        text,
	
    artistId                            char(15)        NOT NULL,
    sellerName                          char(150),

    trackCensoredName                   nchar(150)      NOT NULL,
    contentAdvisoryRating               char(5),
    trackContentRating                  char(5),
    advisories                          char(50),

    FOREIGN KEY(primaryGenreId)         REFERENCES Genre(genreId),
    FOREIGN KEY(artistId)               REFERENCES Artist(artistId),
)
