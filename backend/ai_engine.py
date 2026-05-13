import os
import json
from google import genai
from google.genai import types

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

async def generate_devops_configs(repo_name: str, tech_stack: dict, file_tree: list[str]) -> dict:
    if not GEMINI_API_KEY:
        raise ValueError("Gemini API key is not configured.")

    client = genai.Client(api_key=GEMINI_API_KEY)
    
    # We use gemini-2.5-flash as the latest fast model
    model_id = 'gemini-2.5-flash'
    
    # Truncate file tree if it's too large to fit in context nicely
    tree_subset = file_tree[:1000]
    tree_str = "\n".join(tree_subset)

    prompt = f"""
You are an expert DevOps engineer. I need you to generate production-ready configuration files for my project.

Project Name: {repo_name}
Detected Tech Stack: {json.dumps(tech_stack, indent=2)}

Here is a list of files in the repository:
{tree_str}

IMPORTANT RULES:
- Use modern, available Docker base images. 
- For Java/Kotlin backend services, DO NOT use the deprecated `openjdk` image. Use `eclipse-temurin` (e.g., `eclipse-temurin:17-jdk`) instead.
- If the project uses Gradle (has `build.gradle` or `build.gradle.kts`) but `gradlew` is MISSING from the file tree, DO NOT try to execute or copy `./gradlew`. Instead, use an official Gradle Docker image or just standard `gradle` commands if the SDK provides it.
- If the project is an Android Application, you MUST use `mobiledevops/android-sdk-image:34-jdk17` as the base build image. It already has the Android SDK and `sdkmanager` installed. DO NOT try to run `sdkmanager` or install the SDK manually in the Dockerfile. Just copy the code and run the build command directly.

Please generate the following files:
1. A complete, optimized Dockerfile for building and running the application.
2. A complete docker-compose.yml file.
3. A complete .github/workflows/deploy.yml file for GitHub Actions to build and test the project.

Return your response strictly as a single valid JSON object with the following keys, and nothing else (do not include markdown blocks around the JSON):
- "dockerfile": the string content of the Dockerfile
- "docker_compose": the string content of the docker-compose.yml
- "github_actions": the string content of the deploy.yml
- "explanation": a 2-3 sentence plain English explanation of the deployment strategy chosen.
"""

    try:
        response = await client.aio.models.generate_content(
            model=model_id,
            contents=prompt,
        )
        
        # Parse the JSON response
        text_content = response.text
        # Clean up in case Gemini included markdown formatting
        if text_content.startswith("```json"):
            text_content = text_content[7:]
        if text_content.endswith("```"):
            text_content = text_content[:-3]
            
        result_json = json.loads(text_content.strip())
        return result_json
        
    except Exception as e:
        raise RuntimeError(f"Failed to generate configs from AI engine: {str(e)}")
