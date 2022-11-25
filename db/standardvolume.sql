CREATE TABLE IF NOT EXISTS `standardvolume` (
  `idstandarvolume` INT AUTO_INCREMENT,
  `date` DATE NOT NULL,
  `searchvolume` INT NOT NULL,
  `query` VARCHAR(45) NOT NULL,
  PRIMARY KEY (`idstandarvolume`),
  INDEX `fk_standardvolume_gvolume_idx` (`query` ASC),
  CONSTRAINT `fk_standardvolume_gvolume`
    FOREIGN KEY (`query`)
    REFERENCES `gvolume` (`query`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION);