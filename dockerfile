# 
FROM python:3.11

# 
WORKDIR /code
# Set an environment variable
# 
COPY ./requirements.txt /code/requirements.txt

# 
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

# 
COPY /generator/generated_output /code/app
RUN cd /code/app
WORKDIR  /code/app

# 
CMD ["uvicorn", "api_interface:app", "--host", "0.0.0.0", "--port", "8000"]
