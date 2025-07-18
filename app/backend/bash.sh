#!/bin/bash
# This script is used to start the FastAPI application using Uvicorn in Ubuntu.
uvicorn main:app --reload --host 0.0.0.0 --port 8000
# This script starts the FastAPI application using Uvicorn.