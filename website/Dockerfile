# Author  : Prof. MM Ghassemi <ghassem3@msu.edu>
# Access instance using `docker exec -it hw3-container_flask-app bash`

# Instantiate Ubuntu 20.04
FROM ubuntu:20.04
LABEL maintainer "Mohammad Ghassemi <ghassem3@msu.edu>"
LABEL description="This is custom Docker Image for Dr. Ghassemi's Web Application Course"

# Update Ubuntu Software repository and install MySQL non-interactively
RUN apt-get update -qq && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y mysql-server

# Add the Flask application and install requirements
RUN apt -y install python3-pip vim
RUN mkdir /app
COPY . /app
WORKDIR /app
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Open ports, set environment variables, start services and app
EXPOSE 8080
ENV PORT 8080
ENV FLASK_ENV=production

CMD service mysql start && \
    mysql -u root -e "CREATE USER IF NOT EXISTS 'master'@'localhost' IDENTIFIED BY 'master'; CREATE DATABASE IF NOT EXISTS db; GRANT ALL PRIVILEGES ON db.* TO 'master'@'localhost'; FLUSH PRIVILEGES;" && \
    exec gunicorn --bind :$PORT --workers 1 --worker-class eventlet --threads 8 --timeout 0 app:app
# -----------------------------------------------------