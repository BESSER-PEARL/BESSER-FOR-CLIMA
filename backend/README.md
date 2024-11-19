# Backend part for BESSER-FOR-CLIMA


## Setup

### Requirements: 
- Python 3.11.1
- Docker


### Recommendation: Create a virtual environment

```
python -m venv env
```
And enter it by executing:
```
env\Scripts\Activate
```

### Install the requirements:

```bash
pip install -r requirements.txt
```


# Generate and run

First generate the backend code by executing the generate.py:

```
python generate.py
```

This will generate:
* The SQLAlchemy code
* The fastapi code
* The pydantic classes

Note that the generate.py ingests the metamodel (called metamodel.txt) and a partially instantiated object model (called plantumlobject.txt).


For local development, I suggest deploying everything in a dockerized environment. For that purpose, a docker-compose file is available. 
Navigate to the "Docker" folder and execute:

```
docker-compose build
docker-compose up
```

This includes the local deployment of:
* A PostgreSQL DB
* PGAdmin available under http://localhost:80
* The fastapi application available under http://localhost:8000


You might need to adjust the url, credentials or other configurations of the DB by either using environment variables or manually changing the generator/generated_output/api_interface_objects.py file.
Additionally, you might manually need to instantiate the PostGIS plugin using pgadmin. 

# Pushing updates to the cluster
You'll just need to build the fastapi image and push it to the cluster. Just run the following in the root folder:
```
docker build -t fastapi .
```
And to run it:
```
docker run -p 8000:8000 -e DB_HOST=Your-DB-Address -e DB_NAME=Your-DB-Name -e DB_USER=Your-DB-User -e DB_PASSWORD=Your-DB-User-Password fastapi
```
And voila.