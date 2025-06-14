FROM python:3.11

RUN pip install playwright beautifulsoup4 pandas flask
RUN playwright install

COPY . /app
WORKDIR /app

CMD ["python", "scrape_zillow.py"]
