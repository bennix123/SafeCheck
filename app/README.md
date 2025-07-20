# Insurance Plan Recommendation System


A full-stack application that recommends insurance plans based on user's financial profile, built with React (Frontend) and Python (Backend), containerized with Docker.

## Features

- User financial profile assessment
- Personalized insurance plan recommendations
- Responsive UI with modern design
- REST API backend
- Dockerized development environment

## Prerequisites

- Docker (v20.10+)
- Docker Compose (v2.0+)

## Project Structure

app/
├── backend/ # Python FastAPI backend
│ ├── Dockerfile # Backend Docker configuration
│ ├── requirements.txt # Python dependencies
│ └── ... # Other backend files
├── frontend/ # React frontend
│ ├── Dockerfile # Frontend Docker configuration
│ ├── package.json # Frontend dependencies
│ └── ... # Other frontend files
├── docker-compose.yml # Orchestration configuration
└── README.md # This file

## Getting Started

### Development with Docker (Recommended)

**Clone the repository**
   git clone https://github.com/bennix123/SafeCheck.git
   cd app


**Build and start containers**

docker-compose up --build


**Access the applications**

Frontend: http://localhost:3000

Backend API: http://localhost:8000

