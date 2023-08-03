#
# How to compile: docker build -t tinyarrows .
#
# How to run: docker run -v /Users/bylaska/Public/mariadb:/var/lib/mysql -v /Users/bylaska/Public/TinyArrows/archive:/TinyArrows/archive -p 5001:5001 -p 3306:3306 tinyarrows
#
# How to run: docker run -v /Users/bylaska/Public/TinyArrows/archive:/TinyArrows/archive -p 5001:5001 -p 3306:3306 tinyarrows
#
# How to run: docker run -v /Users/bylaska/Public/mariadb:/var/lib/mysql -v /Users/bylaska/Public/TinyArrows/archive:/TinyArrows/archive tinyarrows
#
# How to stop:
#    docker ps
#    docker stop 7cf7c0ae34b6   ..... where the container ID is 7cf7c0ae34b6
#
# To remove all Docker images, you can use the docker rmi command with the -f (force) option 
# and the output of docker images -q (which lists only the IDs of all images). Here's how you can do it:
#  docker rmi -f $(docker images -q)

#bylaska@Erics-MacBook-Pro TinyArrows % docker images
#REPOSITORY              TAG       IMAGE ID       CREATED             SIZE
#tinyarrows              latest    801e0651d84c   34 minutes ago      2.16GB
#<none>                  <none>    a784918828d1   53 minutes ago      2.16GB
#mongo                   latest    9001035f35d3   11 days ago         624MB


# Use an official Python runtime as a base image
FROM python:3.9

WORKDIR /TinyArrows

COPY . .

RUN pip3 install -r requirements.txt

RUN apt-get update && apt-get install -y mariadb-server libmariadb3 libmariadb-dev openbabel gnuplot

COPY ./init.sql /docker-entrypoint-initdb.d/

EXPOSE 5001 3306

# Start MariaDB and the application
#CMD service mariadb start  && sleep 10 && mysql < /docker-entrypoint-initdb.d/init.sql && python3 Public/app3.py
CMD service mariadb start && (sleep 10 && mysql < /docker-entrypoint-initdb.d/init.sql && python3 Public/app3.py)



