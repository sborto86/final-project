CREATE TABLE IF NOT EXISTS `nytarchive` (
  `idnyt` INT AUTO_INCREMENT,
  `date` DATE NOT NULL,
  `text` TEXT NOT NULL,
  PRIMARY KEY (`idnyt`));