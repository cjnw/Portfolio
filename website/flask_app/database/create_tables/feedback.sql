CREATE TABLE IF NOT EXISTS `feedback` (
`comment_id`        int(11)       NOT NULL AUTO_INCREMENT	COMMENT 'The comment id',
`name`            varchar(100)       NOT NULL 				COMMENT 'The commentators name',
`email`              varchar(100)  NOT NULL					COMMENT 'the commentators email',
`comment`   varchar(500)  NOT NULL                 COMMENT 'the text of the comment',
PRIMARY KEY (`comment_id`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8mb4;