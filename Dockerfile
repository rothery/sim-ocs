FROM python:2.7.15
USER root
RUN apt-get update
RUN pip install xmltodict
RUN pip install pymongo
RUN pip install Twisted
RUN pip install dateutils
RUN pip install pprint


RUN mkdir /staf
COPY src/ocs /staf/ocs 
COPY bin /staf/bin

WORKDIR /staf

EXPOSE 10010
EXPOSE 27017

CMD [ "bash", "/staf/bin/run_ocs.sh"]
