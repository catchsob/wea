FROM ubuntu:20.04
WORKDIR /weapi
COPY wea.py weapi.py requirements.txt ./
ENV TZ=Asia/Taipei
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && \
    echo $TZ > /etc/timezone && \
    apt-get update && \
    apt-get install -y python3-pip python3-testresources tzdata && \
    dpkg-reconfigure -f noninteractive tzdata && \
    pip3 install -r requirements.txt
CMD uwsgi -w weapi:app --http-socket :$PORT
