FROM python:3
ENV PYTHONUNBUFFERED 1
RUN mkdir /workdir
WORKDIR /workdir
ADD requirements.txt /workdir/
RUN python -m pip install --upgrade pip
RUN pip install -r requirements.txt
ADD . /workdir/
