CREATE TABLE IF NOT EXISTS `experiences` (
`experience_id`        int(11)       NOT NULL AUTO_INCREMENT	COMMENT 'The experience id',
`position_id`            int(11)       NOT NULL 				COMMENT 'FK:The position id',
`name`              varchar(100)  NOT NULL					COMMENT 'the name of that experience',
`description`   varchar(1000)  NOT NULL                 COMMENT 'a description of that experience',
`hyperlink`         varchar(500)          NOT NULL                 COMMENT 'a link where people can learn more about the experience',
`start_date`           date          DEFAULT NULL             COMMENT 'The start date for the experience',
`end_date`           date          DEFAULT NULL             COMMENT 'The end date of the experience',
PRIMARY KEY (`experience_id`),
FOREIGN KEY (position_id) REFERENCES positions(position_id)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8mb4 COMMENT="Experiences I have had";