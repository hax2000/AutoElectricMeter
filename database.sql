DROP DATABASE IF EXISTS elmeterdb;
create database elmeterdb;
use elmeterdb;

DROP TABLE IF EXISTS `records`;
CREATE TABLE `records` (
   `id` mediumint not null auto_increment, 
   `daterecord` text not null,
   `consumption` real not null,
   primary key(`id`)
) DEFAULT CHARSET=utf8;

create user bazauser@localhost identified by '123456789q';
grant all privileges on *.* to bazauser@localhost;
