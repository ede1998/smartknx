FROM python:3

# Some stuff that everyone has been copy-pasting
# since the dawn of time.
ENV PYTHONUNBUFFERED 1

RUN mkdir -p /website
WORKDIR /website

COPY ./website .
RUN rm general_utilities
COPY ./general_utilities ./general_utilities
RUN pip install --no-cache-dir -r requirements.txt

RUN mkdir /config
