
from fastapi import FastAPI, HTTPException,Query, status
from pydantic import BaseModel
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from pymongo import MongoClient
from bson import ObjectId
from datetime import datetime
import pytz
from typing import Optional
from bson.errors import InvalidId
import re
import os
from dotenv import load_dotenv

#local imports

from models.job_table import Job,JobResponse
from connect_db import Db_connection
from utils import is_valid_object_id, validate_cron_expression
from db_handler import update_db,get_job,create_job


load_dotenv()  # Load environment variables from .env file


# MongoDB client setup
client = Db_connection()
db = client[os.getenv('DB_NAME')]
jobs_collection = db[os.getenv('COLLECTION_NAME')]

get_dbname = os.getenv('DB_NAME')
get_collection = os.getenv('COLLECTION_NAME')


app = FastAPI()
scheduler = BackgroundScheduler(timezone=pytz.utc)
scheduler.start()


def execute_job(job_id):
    """
    Executes the job by updating its last run time in the database.

    Args:
        job_id (str): The ID of the job to execute.
    """
    condition = {"_id": ObjectId(job_id)}
    job = get_job(get_collection,condition,get_dbname)
    if job:
        # Implement the job logic here, for now, we'll just update the last run time
        condition = {"_id": ObjectId(job_id)}
        to_update={"last_run": datetime.utcnow()}
        update_db(get_collection, condition,to_update, get_dbname,upsert=True)    
        print(f"Executing job {job['job_name']}")

def schedule_job(job_id, interval):
    """
    Schedules a job with a cron expression.

    Args:
        job_id (str): The ID of the job to schedule.
        interval (str): The cron expression to use for scheduling.

    Returns:
        Job: The scheduled job.
    """
    job = scheduler.add_job(execute_job, CronTrigger.from_crontab(interval), args=[job_id], id=job_id)
    return job


    

@app.post("/create-job",status_code=status.HTTP_201_CREATED)
def job_creation(job: Job):
    """
    Creates a new job and schedules it if a valid cron expression is provided.

    Args:
        job (Job): The job details.

    Returns:
        dict: Response with status and job ID.
    """

    if not isinstance(job.job_name, str) or not re.match(r"^[_a-zA-Z]", job.job_name):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Job name must start with an underscore or a letter and contain only valid characters.")

    if not job.job_name or job.job_name.strip() == "":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Job name cannot be empty.")
    job.job_name = job.job_name.strip() 

  
    condition = {"job_name": job.job_name}
    existing_job = get_job(get_collection,condition,get_dbname)

    if existing_job:
        raise HTTPException(status_code=400, detail="Job name must be unique.")
    if job.schedule_time:
        if not validate_cron_expression(job.schedule_time):
            raise HTTPException(status_code=400, detail="Invalid cron expression")
    
    job_data = job.dict()
    job_data["last_run"] = None
    job_data["next_run"] = None
    job_data["status"]="not scheduled"
    result = create_job(get_collection,job_data,get_dbname)
    job_id = str(result.inserted_id)
    print("job schedule time",  job.schedule_time)

    if job.schedule_time != None:
        scheduled_job = schedule_job(job_id, job.schedule_time)
    

        condition = {"_id": ObjectId(job_id)}
        to_update={"next_run": scheduled_job.next_run_time,"status": "running"}
       
        update_db(get_collection, condition,to_update, get_dbname,upsert=True)    
         

    
    
    
    return  {
        "status": status.HTTP_201_CREATED,
        "message": "Job created successfully",
        "job_id": job_id
    }
@app.post("/jobs/{id}/schedule",status_code=status.HTTP_201_CREATED)
def job_schedule(
    id: str, 
    schedule_time: str = Query(..., description="Cron expression")
):  
    """
    Reschedules an existing job with a new cron expression.

    Args:
        id (str): The ID of the job to reschedule.
        schedule_time (str): The new cron expression.

    Returns:
        dict: Response with status and next run time.
    """
    # Validate the job ID
    if not is_valid_object_id(id):
        raise HTTPException(status_code=400, detail="Invalid job ID format.")

    condition = {"_id": ObjectId(id)}
    job = get_job(get_collection,condition,get_dbname)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    print("hey______",schedule_time)
   
    if not validate_cron_expression(schedule_time):
            raise HTTPException(status_code=400, detail="Invalid cron expression")
    print(job)    
    
    job_schedule = scheduler.get_job(job_id=id)
   
    if job_schedule:
        scheduler.remove_job(job_id=id)
   
    # Reschedule the job with the new interval
    scheduled_job = schedule_job(id, schedule_time)

  
    condition = {"_id": ObjectId(id)}
    to_update={
                "schedule_time": schedule_time,
                "next_run": scheduled_job.next_run_time,
                "status": "running"
            }
       
    update_db(get_collection, condition,to_update, get_dbname,upsert=True)    


    return { "status": status.HTTP_201_CREATED,
            "message": f"Job {id} scheduled successfully", 
            "next_run": scheduled_job.next_run_time}


@app.get("/get-all-jobs")
async def list_jobs():
        """
         Retrieves all jobs from the database.

        Returns:
           dict: Response with status and list of jobs.
        """
        try:
            jobs = []
            print("heloo")
        
            for job in jobs_collection.find():
                  jobs.append(JobResponse(id=str(job["_id"]), **job))
            return  { "status": 200,
            "message": "Jobs fetched successfully", 
            "jobs_list": jobs}
        except Exception as e:
            print(f"An error occurred: {e}")
            raise HTTPException(status_code=500, detail="An error occurred while fetching jobs.")
    
   
@app.get("/get-job-by-id/{id}")
async def get_jobs(id: str):
    """
    Retrieves a specific job by its ID.

    Args:
        id (str): The ID of the job.

    Returns:
        dict: Response with status and job data.
    """
    print("job_id_____________",id)
    if not is_valid_object_id(id):
        raise HTTPException(status_code=400, detail="Invalid job ID format.")
    condition = {"_id": ObjectId(id)}
    job = get_job(get_collection,condition,get_dbname)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    return {"status":200, 
            "message": "Jobs fetched successfully",
            "job_data":JobResponse(id=str(job["_id"]), **job),}

@app.put("/jobs/{id}/stop")
def stop_job(id: str):
    """
    Stops a job by its ID and updates its status to "paused".

    Args:
        id (str): The ID of the job to stop.

    Returns:
        dict: Response with status of operation.
    """
    # Find the job in the database
    if not is_valid_object_id(id):
        raise HTTPException(status_code=400, detail="Invalid job ID format.")
    condition = {"_id": ObjectId(id)}
    job = get_job(get_collection,condition,get_dbname)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    current_status = job.get("status")
    if current_status != "running":
        return {"message": f"Job is currently '{current_status}'. No action taken."}
    
    
    condition = {"_id": ObjectId(id)}
    to_update={"status": "paused"}
    updated = update_db(get_collection, condition,to_update, get_dbname,upsert=True)  

    if updated:
            try:
                 job_schedule = scheduler.get_job(job_id=id)
   
                 if job_schedule:
                    scheduler.remove_job(job_id=id)
            except Exception as e:
              
                raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to remove job from scheduler")
        
            return {"message": "Job has been stopped"}
    else:
         raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to stopped the job")


def load_jobs():
    """Load and reschedule all jobs from the database when the app starts."""
    
    for job in jobs_collection.find():
        if job['schedule_time'] !=None:
            schedule_job(str(job["_id"]), job['schedule_time'])
            print(f"Loaded job {job['job_name']} with ID {str(job['_id'])}")


@app.on_event("startup")
def startup_event():
    """
    Startup event handler to load jobs and start the scheduler.
    """
    load_jobs()
    if not scheduler.running:
        scheduler.start()

@app.on_event("shutdown")
def shutdown_event():
    """
    Shutdown event handler to stop the scheduler.
    """
    scheduler.shutdown()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
