FROM alpine:3.3
MAINTAINER haloword@ela.build

RUN apk --no-cache add python py-pip && pip install --upgrade pip

ADD app.py /app/
ADD requirements.txt /app/
WORKDIR /app

RUN pip install -r /app/requirements.txt
RUN pip install gunicorn

EXPOSE 8000
CMD ["gunicorn", "-b 0.0.0.0", "-w 2", "app:app"]
