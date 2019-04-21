#compatible with python 3
FROM python:3

#Add python scripts to run using following line
ADD server_instance.py /

#proto support
ADD https://github.com/google/protobuf/releases/download/v3.6.1/protoc-3.6.1-linux-x86_64.zip ./

#Following command is for any python libraries that need to be installed before we run python scripts
#zmq-python-library support
RUN pip install zmq


#change the script in the following command
CMD [ "python", "./server_instance.py" ]

#save this file as Dockerfile

#then run the following commands on the terminal
#to build docker image : docker build -t python-image .
#to run the image : docker run python-image
