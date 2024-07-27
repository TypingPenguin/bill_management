#
FROM python:latest

# install google chrome
#RUN wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add -
#RUN sh -c 'echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list'
#RUN apt-get -y update
#RUN apt-get install -y google-chrome-stable
#
## install chromedriver
#RUN apt-get install -yqq unzip
#RUN curl -o /tmp/chromedriver-linux64.zip https://edgedl.me.gvt1.com/edgedl/chrome/chrome-for-testing/116.0.5845.96/linux64/chromedriver-linux64.zip
#RUN ls /tmp
#RUN unzip /tmp/chromedriver-linux64.zip chromedriver-linux64/chromedriver -d /usr/local/bin/

# set display port to avoid crash
#ENV DISPLAY=:99

#
WORKDIR /code

#
COPY ./requirements.txt /code/requirements.txt

#
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

#
COPY ./app /code/app

#
## Install Chrome and ChromeDriver
#RUN apt-get update && apt-get install -y \
#    chromium-driver \
#    && rm -rf /var/lib/apt/lists/*

# Set environment variables to run ChromeDriver with Chrome
#ENV CHROME_EXECUTABLE=/usr/bin/chromium-browser
#ENV CHROMEDRIVER_PATH=/usr/bin/chromedriver
#ENV CHROMEDRIVER_PATH=/usr/local/bin/chromedriver

#
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "80"]
