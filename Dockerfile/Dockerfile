# Set the base image
FROM ubuntu:17.10

# Dockerfile author / maintainer 
MAINTAINER William H Thompson <hedley@startmail.com> 

RUN apt-get update && apt-get install python3-dev -y

# Update
RUN apt-get update && apt-get install -y \
  build-essential \
  gfortran \
  git \
  wget \
  liblapack-dev \
  libopenblas-dev \
  python3-dev \
  python3-pip \
  python3-nose \
  python3-tk

ENV DISPLAY :0
# Install tvc_benchmarker (and dependencies)
RUN pip3 install --upgrade pip
RUN pip3 install --upgrade six
RUN pip3 install --upgrade --no-deps git+git://github.com/Theano/Theano.git
RUN pip3 install teneto==0.2.7b 
RUN pip3 install git+https://github.com/wiheto/tvc_benchmarker.git
RUN mkdir -p /root/.config/matplotlib
RUN echo "backend : Agg" > /root/.config/matplotlib/matplotlibrc 

CMD ["python3","-m","tvc_benchmarker"]
