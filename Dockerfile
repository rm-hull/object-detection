FROM debian:11

WORKDIR /app
ENV HOME /app
RUN apt-get update && \
    apt-get install -y git nano python3-pip python3-dev python3-opencv python3-numpy pkg-config wget usbutils curl && \
    echo "deb https://packages.cloud.google.com/apt coral-edgetpu-stable main" | tee /etc/apt/sources.list.d/coral-edgetpu.list && \
    curl https://packages.cloud.google.com/apt/doc/apt-key.gpg | apt-key add - && \
    apt-get update && \ 
    apt-get install -y gasket-dkms libedgetpu1-std python3-pycoral

RUN git clone https://github.com/google-coral/pycoral.git
RUN bash pycoral/examples/install_requirements.sh classify_image.py

ENV PYTHONPATH=/app
ENV PYTHONDONTWRITEBYTECODE=1

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 4000

ENV UVICORN_HOST=0.0.0.0
ENV UVICORN_PORT=4000
ENV UVICORN_LOG_LEVEL=info
