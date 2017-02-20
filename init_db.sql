DROP DATABASE IF EXISTS TrashNetwork;
CREATE DATABASE TrashNetwork DEFAULT CHARACTER SET utf8;

CREATE USER 'TrashNetwork'@'localhost' IDENTIFIED BY '4f5100635dc64621aa4ae256daae80046833ce8f';
GRANT ALL ON TrashNetwork.* TO 'TrashNetwork'@'localhost';
