# Climaborough-data-platform-frontend (aka the dashboards)

## Local deployment without Docker (not recommended)

### Requirements
* Python 3.11.3



### Project Setup

```sh
pip install -r requirements.txt
```

Before running, make sure that the following configurations in config.ini are set correctly:
* websocket.host = localhost


### Run

```sh
python climabot.py
```


## Docker deployment

Before building, make sure that the following configurations in config.ini are set correctly:
* websocket.host = 0.0.0.0


Docker build:
```sh
docker build -t climabot .
```

Run docker version using:
```
docker run -p 8765:8765 climabot
```


