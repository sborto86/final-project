CREATE TABLE IF NOT EXISTS `gvolume` (
  `query` VARCHAR(45) NOT NULL,
  `avgsearch` INT NOT NULL,
  `fromdate` DATE NOT NULL,
  `todate` DATE NOT NULL,
  `volumerank` TINYINT(1) NULL,
  PRIMARY KEY (`query`),
  UNIQUE INDEX `query_UNIQUE` (`query` ASC));