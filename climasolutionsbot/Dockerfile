# Use the official Python 3.10.8 image from the Docker Hub
FROM python:3.11.9

# Set the working directory in the container
WORKDIR /app

# Copy the requirements.txt file into the container at /app
COPY requirements.txt .

# Install the dependencies specified in requirements.txt
RUN pip install -r requirements.txt

# Install additional dependencies that might be needed
RUN pip install langchain_community openai langchain-openai chromadb langchain-chroma

# Copy the rest of your application code into the container at /app
COPY . .

# Expose the port that the app runs on
EXPOSE 8765

CMD ["python", "./climabot.py"]


