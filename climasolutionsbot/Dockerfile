# Use the official Python 3.10.8 image from the Docker Hub
FROM python:3.11.9

# Set the working directory in the container
WORKDIR /app

# Copy the requirements.txt file into the container at /app
COPY requirements.txt .

# Install the dependencies specified in requirements.txt
RUN pip install besser-bot-framework==1.3.0 --no-deps


# Install necessary tools to handle dependencies
RUN pip install pipdeptree

# Get the dependencies list, excluding torch, and install them
RUN set -ex && \
    deps=$(pip show besser-bot-framework | grep Requires | cut -d: -f2 | tr ',' '\n' | awk '{print $1}' | grep -v torch) && \
    for dep in $deps; do pip install $dep; done

# Optionally, if you want to confirm the installations
RUN pip list

# Copy the rest of your application code into the container at /app
COPY . .

# Expose the port that the app runs on
EXPOSE 8765



CMD ["python", "./climabot.py"]


