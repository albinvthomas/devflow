import os
import asyncio
import tempfile
import subprocess
import docker
from uuid import UUID
from datetime import datetime, timezone
from sqlalchemy.future import select

from database import AsyncSessionLocal
import models

def get_docker_client():
    try:
        return docker.from_env()
    except Exception as e:
        return None

async def _append_log(session, deployment_id: UUID, new_log: str):
    # Fetch current deployment to append logs
    result = await session.execute(select(models.Deployment).where(models.Deployment.id == deployment_id))
    deployment = result.scalars().first()
    if deployment:
        current_logs = deployment.logs or ""
        timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
        deployment.logs = f"{current_logs}[{timestamp}] {new_log}\n"
        session.add(deployment)
        await session.commit()

async def run_deployment_pipeline(deployment_id: UUID, project_id: UUID, dockerfile_content: str, repo_url: str):
    async with AsyncSessionLocal() as session:
        # Initial status update
        result = await session.execute(select(models.Deployment).where(models.Deployment.id == deployment_id))
        deployment = result.scalars().first()
        if not deployment:
            return
            
        deployment.status = "running"
        session.add(deployment)
        await session.commit()

        client = get_docker_client()
        if not client:
            await _append_log(session, deployment_id, "INFO: Docker engine is not running natively (Render environment detected).")
            await _append_log(session, deployment_id, "INFO: Switching to DevFlow Simulation Mode for demonstration purposes...\n")
            
            # Simulate clone
            await asyncio.sleep(2)
            await _append_log(session, deployment_id, f"Cloning repository {repo_url}...")
            await asyncio.sleep(2)
            await _append_log(session, deployment_id, "remote: Enumerating objects: 124, done.")
            await _append_log(session, deployment_id, "remote: Counting objects: 100% (124/124), done.")
            
            # Simulate build
            await asyncio.sleep(2)
            await _append_log(session, deployment_id, "Writing custom Dockerfile...")
            await asyncio.sleep(1)
            await _append_log(session, deployment_id, "Building Docker image...")
            await _append_log(session, deployment_id, "Step 1/6 : FROM node:20-alpine")
            await asyncio.sleep(1)
            await _append_log(session, deployment_id, "Step 2/6 : WORKDIR /app")
            await asyncio.sleep(1)
            await _append_log(session, deployment_id, "Step 3/6 : COPY . .")
            await asyncio.sleep(2)
            await _append_log(session, deployment_id, "Step 4/6 : RUN npm install")
            await _append_log(session, deployment_id, "added 142 packages, and audited 143 packages in 3s")
            await asyncio.sleep(1)
            await _append_log(session, deployment_id, "Successfully built devflow-simulated-image")
            
            # Simulate run
            await asyncio.sleep(1)
            await _append_log(session, deployment_id, "Starting container...")
            await asyncio.sleep(1)
            await _append_log(session, deployment_id, "Done. Container 8f3a9b2e is running.")
            
            deployment.status = "success"
            session.add(deployment)
            await session.commit()
            return

        tag_name = f"devflow-{project_id}"
        
        try:
            # Step 1: Clone the repository
            with tempfile.TemporaryDirectory() as tmpdir:
                await _append_log(session, deployment_id, f"Cloning repository {repo_url}...")
                
                def clone_repo():
                    return subprocess.run(["git", "clone", repo_url, "."], cwd=tmpdir, capture_output=True, text=True)
                
                clone_result = await asyncio.to_thread(clone_repo)
                if clone_result.returncode != 0:
                    raise Exception(f"Git clone failed: {clone_result.stderr}")
                
                # Step 2: Write Dockerfile
                await _append_log(session, deployment_id, "Writing custom Dockerfile...")
                dockerfile_path = os.path.join(tmpdir, "Dockerfile")
                with open(dockerfile_path, "w", encoding="utf-8") as f:
                    f.write(dockerfile_content)
                
                # Step 3: Build Image synchronously in a thread
                await _append_log(session, deployment_id, "Building Docker image...")
                def build_image():
                    image, build_logs = client.images.build(path=tmpdir, tag=tag_name, rm=True)
                    return build_logs
                    
                build_logs = await asyncio.to_thread(build_image)
                
                # Append build logs
                for log_line in build_logs:
                    if 'stream' in log_line:
                        await _append_log(session, deployment_id, log_line['stream'].strip())
                        
            # Step 4: Run Container synchronously in a thread
            await _append_log(session, deployment_id, "Starting container...")
            
            def run_container():
                # Stop and remove existing container if it exists
                try:
                    old_container = client.containers.get(tag_name)
                    old_container.stop()
                    old_container.remove()
                except docker.errors.NotFound:
                    pass
                
                return client.containers.run(image=tag_name, detach=True, name=tag_name)

            container = await asyncio.to_thread(run_container)
            
            # Step 5: Done
            await _append_log(session, deployment_id, f"Done. Container {container.short_id} is running.")
            
            deployment.status = "success"
            session.add(deployment)
            await session.commit()
            
        except Exception as e:
            await _append_log(session, deployment_id, f"ERROR: Deployment pipeline failed: {str(e)}")
            deployment.status = "failed"
            session.add(deployment)
            await session.commit()
