This repository contains commands used by the TinArrowss web api  

Make sure mysql server has been started

   On MAC:
      mysql.server start
      (brew services start mariadb)

How to create and setup mysql database

   On MAC:
      https://mariadb.com/kb/en/installing-mariadb-on-macos-using-homebrew/
      brew install mariadb

      mysql.server start
      (brew services start mariadb)

      ### these two steps may not work ###
      mysql_secure_installation -u YourUserName
      mysql -u YourUserName

      ### just use, instead ###
      mysql


      CREATE USER 'arrows'@localhost IDENTIFIED BY 'reaction';
      GRANT ALL PRIVILEGES ON *.* TO 'arrows'@localhost IDENTIFIED BY 'reaction';


      Download eric2.sql 

      mysql -u arrows -p
      create database TNT_Project;
      mysql -u arrows -p TNT_Project < eric2.sql


Needed open-babel programs:
	brew install open-babel

Needed python libraries:
        pip3 install flask
	pip3 install pyyaml
	pip3 install pymongo
	pip3 install numpy
	pip3 install tinydb
	pip3 install tinymongo
	pip3 install pexpect
	pip3 install pymysql
