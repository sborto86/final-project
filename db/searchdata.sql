CREATE TABLE IF NOT EXISTS `searchdata` (
  `idsearch` INT AUTO_INCREMENT,
  `query` VARCHAR(45) NOT NULL,
  `date` DATE NOT NULL,
  `google` INT NULL,
  `nyt` INT NULL,
  `guardian` INT NULL,
  PRIMARY KEY (`idsearch`));