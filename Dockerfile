FROM scrapinghub/scrapinghub-stack-scrapy:1.3
ENV TERM xterm
ENV SCRAPY_SETTINGS_MODULE traveloka.settings
RUN mkdir -p /app
WORKDIR /app
COPY ./requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
COPY . /app
RUN python setup.py install
RUN pip install scrapy
RUN pip install scrapy-selenium

# install google chrome
RUN wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add -
RUN sh -c 'echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list'
RUN apt-get -y update
RUN apt-get install -y google-chrome-stable

# install chromedriver
COPY ./chromedriver /usr/local/bin
COPY ./chromedriver /app
