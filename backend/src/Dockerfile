FROM python:3.11

# Set working directory
WORKDIR /code

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Copy requirements first for better caching
COPY requirements.txt /code/requirements.txt

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

# Copy application code
COPY ./app /code/app
COPY ./run.py /code/run.py
COPY ./startup.py /code/startup.py
COPY ./init_db.py /code/init_db.py
COPY ./create_minimal_kpis.py /code/create_minimal_kpis.py

# Create .env file with default values (will be overridden by docker-compose)
RUN echo 'DB_HOST=postgres\nDB_PORT=5432\nDB_USER=aaron\nDB_PASSWORD=aaron\nDB_NAME=aaron\nDEBUG=true' > /code/.env

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/api/health || exit 1

# Command to run the application (using startup script)
CMD ["python", "startup.py"]