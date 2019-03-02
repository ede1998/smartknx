FROM python:3

# Some stuff that everyone has been copy-pasting
# since the dawn of time.
ENV PYTHONUNBUFFERED 1

RUN mkdir -p /knxbus
WORKDIR /knxbus

COPY ./knxbus .
RUN rm knx/general_utilities
COPY ./general_utilities ./knx/general_utilities
RUN pip install --no-cache-dir -r requirements.txt

RUN mkdir /config
