import os
import json
import time
import uuid
import threading
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import uvicorn

# Import your custom functions
from github_process import validate_github_url, clone_github_repo, setup_github_repo_files_dir
from src.main import main as run_main_pipeline

app = FastAPI(title="GitHub Repository Analyzer API")

# Allow all origins (adjust for production)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory store for job results
job_results = {}

class GitHubRepoRequest(BaseModel):
    url: str

@app.get("/cors-test")
async def cors_test():
    return {"message": "CORS is working correctly"}

def process_job(job_id: str, url: str):
    """
    This function sets up the repo and spawns a separate thread to run the heavy analysis.
    The thread will update the global `job_results` when finished.
    """
    try:
        os.environ["GITHUB_REPO_URL"] = url
        if not validate_github_url(url):
            job_results[job_id] = {"status": "error", "detail": "Invalid GitHub repository URL."}
            return

        repo_dir = clone_github_repo(url)
        if not repo_dir:
            job_results[job_id] = {"status": "error", "detail": "Failed to clone the repository."}
            return

        files_dir = setup_github_repo_files_dir(repo_dir)
        os.environ['GITHUB_PROJECT_DIR'] = repo_dir
        os.environ['FILES_DIR'] = files_dir

        def heavy_task():
            try:
                # Run the long analysis (this may take 40+ seconds)
                run_main_pipeline(is_github_repo=True)
                
                # Define the expected output paths
                main_files_dir = "/home/prajwalak/Desktop/CodeAnaa"
                main_files_dir = os.path.join(main_files_dir, "files")
                json_file_path = os.path.join(main_files_dir, "aider_repomap.json")
                csv_file_path = os.path.join(main_files_dir, "output.csv")
                
                # Wait until the files appear (with a timeout)
                timeout = 60  # seconds
                start_time = time.time()
                while ((not os.path.exists(json_file_path) or not os.path.exists(csv_file_path))
                       and (time.time() - start_time < timeout)):
                    time.sleep(2)
                
                if not os.path.exists(json_file_path) or not os.path.exists(csv_file_path):
                    job_results[job_id] = {"status": "error", "detail": "Analysis results not found after timeout."}
                    return

                with open(json_file_path, "r") as f:
                    json_data = json.load(f)
                with open(csv_file_path, "r") as f:
                    csv_content = f.read()

                job_results[job_id] = {
                    "json_data": json_data,
                    "csv_data": csv_content,
                    "status": "success"
                }
            except Exception as e:
                job_results[job_id] = {"status": "error", "detail": f"Error processing job: {str(e)}"}
        
        # Start the heavy analysis in a new thread so it doesn't block the main loop.
        thread = threading.Thread(target=heavy_task)
        thread.start()
    except Exception as e:
        job_results[job_id] = {"status": "error", "detail": f"Unexpected error: {str(e)}"}

@app.post("/analyze")
async def analyze_repo(repo_request: GitHubRepoRequest, background_tasks: BackgroundTasks):
    """
    Starts the analysis by creating a job with status "processing" and then launching the processing.
    """
    job_id = uuid.uuid4().hex
    # Initialize the job entry with "processing" status so that polling always gets a valid response.
    job_results[job_id] = {"status": "processing"}
    # Offload the processing (which itself spawns a thread for heavy work)
    background_tasks.add_task(process_job, job_id, repo_request.url)
    return {"job_id": job_id, "status": "processing"}

@app.get("/result/{job_id}")
async def get_result(job_id: str):
    """
    Polling endpoint that returns the job status (processing, success, or error) for a given job ID.
    """
    if job_id not in job_results:
        # Instead of raising an HTTPException (which might not have proper CORS headers), we return a JSON with status "processing".
        return JSONResponse(content={"status": "processing"}, status_code=200)
    return job_results[job_id]

if __name__ == "__main__":
    uvicorn.run("api_server:app", host="0.0.0.0", port=8000, reload=True)
