# VideoMan: The Ultimate Video Management API

## Introduction

This FastAPI application provides a robust RESTful API for video management. Admin users can perform various tasks to manage the video content efficiently.

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/tnahddisttud/video_man.git
```

### 2. Create a Virtual Environment

```bash
# Navigate to the project directory
cd video_man

# Create a virtual environment
python -m venv venv
```

### 3. Install Dependencies

```bash
# Activate the virtual environment
source venv/bin/activate  # Linux/macOS
# or
venv\Scripts\activate  # Windows

# Install requirements
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Create a `.env` file in the root directory and add the following environment variables:

```env
SECRET_KEY=your_secret_key
ALGORITHM=your_algorithm
```

## Usage

### Run the Application

Use the following command to run the application:

```bash
uvicorn main:app --reload
```

### Access API Documentation

Open your browser and navigate to [http://localhost:8000/docs](http://localhost:8000/docs) to access the Swagger-based API documentation.

### Create Admin User

Use the API endpoint `POST /user` in the documentation to create an admin user. Provide the required details in the request body.

