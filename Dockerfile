#compatible with python 3
FROM python:3

#Add python scripts to run using following line
ADD server_instance.py /

#Following command is for any python libraries that need to be installed before we run python scripts
RUN pip install zmq


#change the script in the following command
CMD [ "python", "./server_instance.py" ]

#save this file as Dockerfile

#then run the following commands on the terminal
#to build docker image : docker build -t python-image .
#to run the image : docker run python-image
