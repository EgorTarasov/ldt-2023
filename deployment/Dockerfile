FROM python:3.11.3-buster

# Select working directory
WORKDIR /code

# Copy requirements.txt to working directory
COPY requirements/production.txt requirements/production.txt
COPY requirements/base.txt requirements/base.txt

# Install dependencies
RUN pip install -r requirements/production.txt

# Copy source code to working directory
COPY . /code

# Create data directory
RUN mkdir -p /data/logs

# Run the application
CMD ["python3", "main.py"]