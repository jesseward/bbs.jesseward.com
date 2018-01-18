FROM python:2
MAINTAINER jesseward

RUN mkdir /opt/bbs
RUN mkdir /opt/bbs/.data
RUN git clone https://github.com/jesseward/bbs.jesseward.com.git /opt/bbs/bbs.jesseward.com
RUN pip install x84
EXPOSE 64738
ENTRYPOINT [ "/usr/local/bin/x84", "--config",  "/opt/bbs/bbs.jesseward.com/config.ini" ]
