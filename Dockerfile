FROM python:2-onbuild
RUN apt-get update
RUN apt-get install apt-utils --yes --force-yes
RUN dpkg-reconfigure apt-utils --force
RUN apt-get install geographiclib-tools proj-bin --yes
RUN mkdir /usr/share/geographiclib
RUN dpkg-query -L geographiclib-tools
RUN /usr/sbin/geographiclib-get-geoids best
CMD [ "python", "./runserver.py" ]
