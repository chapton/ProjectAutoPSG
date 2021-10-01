FROM nvcr.io/nvidia/tensorflow:20.11-tf1-py3
# Set the working directory to /app
WORKDIR /app
# Copy the current directory contents into the container at /app
COPY requirements.txt /app

# Run app.py when the container launches
RUN pip install --trusted-host pypi.python.org -r requirements.txt
#CMD ["python3", "/app/TensorFlow.py"]
#COPY requirements.txt /app/requirements.txt
#RUN pip install -r requirements.txt