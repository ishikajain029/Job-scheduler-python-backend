# Job Scheduling Microservice

This microservice is a FastAPI-based application that allows users to create, schedule, and manage jobs using cron expressions. The service integrates with MongoDB to store job data and uses APScheduler for job scheduling.

## Features

- **Create Job**: Define a new job with a unique name and optional cron scheduling.
- **Schedule Job**: Update the scheduling of an existing job with a new cron expression.
- **List Jobs**: Retrieve a list of all jobs.
- **Get Job by ID**: Retrieve details of a specific job by its ID.
- **Stop Job**: Stop a running job and update its status.

## Requirements

- Python 3.8+
- FastAPI
- APScheduler
- PyMongo
- python-dotenv
- Pytz
- Pydantic

## Installation

1. Clone the repository:

    ```bash
    git clone <repository_url>
    cd <repository_name>
    ```

2. Create a virtual environment and activate it:

   
    ```bash
    pip install virtualenv
    ```

    Then, create a virtual environment:

    ```bash
    python -m venv venv
    ```
    ```bash
        source venv/bin/activate
    ```


3. Install the required dependencies:

    ```bash
    pip install -r requirements.txt
    ```

4. Create a `.env` file in the root directory with the following environment variables:

    ```env
    DB_NAME=<your_database_name>
    COLLECTION_NAME=<your_collection_name>
    PORT=<port_number>
    ```

## Usage

1. **Run the application**:

    ```bash
    python3 job_scheduler.py
    ```

2. **Endpoints**:

    - **Create a job**:

        ```http
        POST /create-job
        ```

        **Request Body**:

        ```json
        {
            "job_name": "email_sender_job",
            "schedule_time": "* * * * *",
            "job_details":"this is job will send mail"
        }
        ```

    - **Reschedule a job**:

        ```http
        POST /jobs/{id}/schedule
        ```

        **Query Parameter**:

        ```json
        {
            "schedule_time": "0 0 1 1 *"
        }
        ```

    - **List all jobs**:

        ```http
        GET /get-all-jobs
        ```

    - **Get job by ID**:

        ```http
        GET /get-job-by-id/{id}
        ```

    - **Stop a job**:

        ```http
        PUT /jobs/{id}/stop
        ```




