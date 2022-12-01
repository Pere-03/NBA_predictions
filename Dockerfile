FROM python:3.9.15

RUN apt-get -y update \&& apt-get -y install gcc make \&& rm -rf /var/lib/apt/lists/*s

# Para instalar Chrome  
RUN wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add -
RUN sh -c 'echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list'
RUN apt-get -y update
RUN apt-get install -y google-chrome-stable

# Para instalar el driver
RUN apt-get install -yqq unzip
RUN wget -O /tmp/chromedriver.zip http://chromedriver.storage.googleapis.com/`curl -sS chromedriver.storage.googleapis.com/LATEST_RELEASE`/chromedriver_linux64.zip
RUN unzip /tmp/chromedriver.zip chromedriver -d /usr/local/bin/

WORKDIR /usr/src/app

COPY . .

RUN /usr/local/bin/python -m pip install --upgrade pip && pip install -r requirements.txt

CMD ["python3", "team_stats.py"]
