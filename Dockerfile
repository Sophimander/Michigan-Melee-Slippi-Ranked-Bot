# Use an official Python 3.10 runtime as a parent image
FROM python:3.10-slim-buster

# Install prerequisites
RUN apt-get update && apt-get install -y git curl wget gnupg2 unzip cron
RUN wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add -
RUN echo "deb http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list
RUN apt-get update && apt-get install -y google-chrome-stable

# Set up the Chrome driver
RUN LATEST_CHROMEDRIVER_VERSION=$(curl -sS chromedriver.storage.googleapis.com/LATEST_RELEASE) && \
    wget -O /tmp/chromedriver.zip http://chromedriver.storage.googleapis.com/$LATEST_CHROMEDRIVER_VERSION/chromedriver_linux64.zip && \
    unzip /tmp/chromedriver.zip chromedriver -d /usr/local/bin/ && \
    rm /tmp/chromedriver.zip

# Create a directory to store the git repository
RUN mkdir /michigan_melee_bot
WORKDIR /michigan_melee_bot

# Clone the git repository
RUN git clone https://github.com/ConstObject/Michigan-Melee-Slippi-Ranked-Bot.git

# Set the working directory to the cloned repository
WORKDIR /michigan_melee_bot/Michigan-Melee-Slippi-Ranked-Bot

# Copy database if present
COPY database.db database.db

# Copy backup script if possible
COPY backup_database.sh backup_database.sh

# Install any dependencies required by the repository
RUN pip install -r requirements.txt

# Set environment variables
ENV DISCORD_TOKEN=<YOUR_DISCORD_TOKEN>
ENV DISCORD_COMMAND_PREFIX=$
ENV PYTHONUNBUFFERED=1

# Make script executable
RUN chmod +x create_snapshot.sh

# Create cron job to run create_snapshot.py every 2 hours
RUN echo "SHELL=/bin/bash\n0 */2 * * * /michigan_melee_bot/Michigan-Melee-Slippi-Ranked-Bot/create_snapshot.sh >> /var/log/cron.log 2>&1" >> mycron
RUN crontab mycron
RUN touch /var/log/cron.log

# Set the command to start the bot and cron daemon
CMD service cron start && python -u main.py
