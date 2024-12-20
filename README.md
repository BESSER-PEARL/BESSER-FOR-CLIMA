# BESSER-FOR-CLIMA

This repository contains the DSL for the clima domain and the corresponding generators.

## Table of Contents
- [Introduction](#introduction)
- [Setup and Installation](#setup-and-installation)
- [Usage](#usage)
- [Contributing](#contributing)
- [License](#license)
- [Contact Information](#contact-information)

## Introduction
BESSER-FOR-CLIMA is a platform with a low-code/no-code dashboard solution. As part of the ClimaBorough project, this platform enables:

- Easy creation and management of climate data visualizations
- Customizable dashboards for different cities
- Automated code generation for data processing and analysis
- Interactive data exploration and reporting capabilities

The ClimaPlatform dashboard - a user-friendly interface for data visualization and management

## Setup and Installation

### Requirements
- Python 3.11.1
- Docker
- Node.js v18

### Backend Setup

#### Create a Virtual Environment
```bash
python -m venv env

# Activate the environment:
env\Scripts\Activate

# Install Requirements
pip install -r requirements.txt
```

#### Generate Backend Code
Run the generate.py script to generate the necessary code:
```bash
python generate.py
```

This will generate:
- SQLAlchemy code
- FastAPI code
- Pydantic classes

#### Local Development with Docker
Navigate to the Docker folder and execute:
```bash
docker-compose build
docker-compose up
```

This includes:
- A PostgreSQL DB
- PGAdmin at http://localhost:80
- FastAPI application at http://localhost:8000

### Frontend Setup

#### Install Dependencies
```bash
npm install
```

#### Compile and Hot-Reload for Development
```bash
npm run dev
```

#### Docker Setup for Frontend
Build the Docker image:
```bash
docker build -t frontend .
```

Run the Docker container:
```bash
docker run -p 3000:3000 -e API_URL=http://localhost:8000 -e WEBSOCKET_URL=ws://localhost:8765 frontend
```

Set environment variables:
- API_URL: Address of your FastAPI application
- WEBSOCKET_URL: Address of your bot application

## Usage
Provide examples of how to use the project, including any necessary commands or scripts.

## Contributing
We welcome contributions! Please see the guidelines for instructions on how to contribute to this project.

## License
This project is licensed under the MIT License.

## Contact Information
For support or questions, please contact the repository maintainers or open an issue on GitHub.
