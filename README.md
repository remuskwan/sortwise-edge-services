# SortWise Edge Services

Edge services for SortWise, including image upload to s3, and inference and metadata from Amazon SageMaker and DynamoDB.

## Requirements

Python 3.11 and above. Exectute the following command to check the version of python installed on your system.

```
python --version
```

## Setup

1. Install Python Virtual Environment

```
python -m venv env
```

2. Activate the virtual environment

```
source env/bin/activate
```

3. Install the required packages

```
pip install -r requirements.txt
```

### Notes

1. If there are new packages installed, update the requirements.txt file by running the following command:

```
pip freeze > requirements.txt
```

## Running the development server

1. Create a new `.env` file using the `.env.example` provided in the repository. Fill in the required environment variables.

```bash
# In the root directory of the repository
touch .env
```

2. Run the following command to start the development server. By default, the development process runs on port 8000.

```
uvicorn src.main:app --reload
```

3. Open the browser and navigate to the following URL to access the API documentation

```
http://localhost:8000/docs
```
![Screenshot 2024-03-26 at 12 19 28 AM](https://github.com/remuskwan/sortwise-edge-services/assets/36059985/9ee3b4ee-0871-4afd-a222-642cb6b77bda)

## Deployment

SortWise API is deployed onto AWS Lambda using Docker images and Amazon ECR. The deployment process is automated using GitHub Actions. The deployment process is triggered when a new release is created on the repository.
