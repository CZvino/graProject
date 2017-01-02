create table Artist
(
    artistId                            bigint          PRIMARY KEY,
    artistName                          nchar(150)      NOT NULL,
)

create table Genre
(
    genreId                             int             PRIMARY KEY,
    genreName                           nchar(50)       NOT NULL,
)

create table Advisory
(
    advisoryId                          int             PRIMARY KEY,
    advisoryContent                     nchar(150)      NOT NULL,
)

create table AppInformation
(
    trackId                             bigint          PRIMARY KEY,
    trackName                           nchar(150)      NOT NULL,
    bundleId                            nchar(150)      NOT NULL,

    keywords                            nchar(300),
	topic                               nchar(300),
    releaseDate                         smalldatetime   default '1970-01-01 00:00:00',
    userRatingCount                     bigint          default '0',
    averageUserRating                   decimal(2, 1)   default '0.0',

    currency                            char(5)         default 'None',
    formattedPrice                      nchar(50)       default 'None',
    price                               smallmoney      default '0',

    fileSizeBytes                       bigint             default '0',

    wrapperType                         nchar(20),
    isGameCenterEnabled                 bit             default 'False',
    isVppDeviceBasedLicensingEnabled    bit             default 'False',

    minimumOsVersion                    char(10)        default '0.0',
    supportedDevices                    text,

    primaryGenreId                      int             NOT NULL,
    genreIds                            char(50)        NOT NULL,

    description                         text,

    languageCodesISO2A                  text,

    version                             char(15),
    currentVersionReleaseDate           smalldatetime   default '1970-01-01 00:00:00',
    userRatingCountForCurrentVersion    int             default '0',
    averageUserRatingForCurrentVersion  decimal(2, 1)   default '0.0',
    releaseNotes                        text,
	
    artistId                            bigint          NOT NULL,
    sellerName                          nchar(150),

    trackCensoredName                   nchar(150)      NOT NULL,
    contentAdvisoryRating               char(5),
    trackContentRating                  char(5),
    advisories                          char(50),

    FOREIGN KEY(primaryGenreId)         REFERENCES Genre(genreId),
    FOREIGN KEY(artistId)               REFERENCES Artist(artistId),
)
