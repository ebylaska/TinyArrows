CREATE DATABASE IF NOT EXISTS TNT_Project;

USE TNT_Project;

-- Create the 'arrows' user if it doesn't exist
CREATE USER IF NOT EXISTS 'arrows'@'%' IDENTIFIED BY 'reaction';

-- Grant all privileges to the 'arrows' user on the 'TNT_Project' database
GRANT ALL PRIVILEGES ON TNT_Project.* TO 'arrows'@'%';

-- Flush privileges to apply the changes
FLUSH PRIVILEGES;

-- Load the eric3.sql backup file only if the database is newly created
-- You may modify the path accordingly based on the actual location of the file
SOURCE /docker-entrypoint-initdb.d/backup/eric3.sql;

-- Optionally, set a password for the 'root' user
ALTER USER 'root'@'%' IDENTIFIED BY '05291999';

