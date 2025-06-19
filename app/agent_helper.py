from smolagents import CodeAgent
from smolagents import tool
import os
import requests
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv(override=True)

class OllamaModel:
    def __init__(self, model_name=None, api_base=None):
        load_dotenv(override=True)
        self.api_base = api_base or os.getenv("OLLAMA_API_BASE", "http://localhost:11434")
        self.model_name = model_name or os.getenv("OLLAMA_MODEL", "llama3.2")
        if not self.api_base.strip():
            self.api_base = "http://localhost:11434"
        if os.getenv("DEBUG") == "1":
            print(f"OllamaModel initialized with API base: {self.api_base}")

    def __call__(self, prompt, **kwargs):
        if not isinstance(prompt, str):
            prompt = json.dumps(prompt, default=str)
        return self.generate(prompt, **kwargs)

    def generate(self, prompt, **kwargs):
        url = f"{self.api_base}/api/generate"
        timeout = int(os.getenv("OLLAMA_TIMEOUT", "300"))
        payload = {
            "model": self.model_name,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": 0.3,
                "top_p": 0.9,
                "top_k": 40,
                "num_predict": 2048,
                "num_ctx": 4096
            }
        }
        if "options" in kwargs and isinstance(kwargs["options"], dict):
            payload["options"].update(kwargs["options"])
        for key, value in kwargs.items():
            if key != "options" and value is not None:
                payload[key] = value
        try:
            if os.getenv("DEBUG") == "1":
                print(f"DEBUG: Sending request to Ollama with payload: {json.dumps(payload)[:200]}...")
            response = requests.post(url, json=payload, timeout=timeout)
            response.raise_for_status()
            return response.json().get("response", "")
        except requests.exceptions.RequestException as e:
            raise Exception(f"Ollama request failed: {e}")

def is_ollama_available(api_base=None):
    load_dotenv(override=True)
    api_base = api_base or os.getenv("OLLAMA_API_BASE", "http://localhost:11434")
    try:
        response = requests.get(f"{api_base}/api/version", timeout=0.5)
        return response.status_code == 200
    except Exception as e:
        if os.getenv("DEBUG") == "1":
            print(f"Ollama check failed: {e}")
        return False

def is_ai_enhancement_enabled():
    return os.getenv("DISABLE_AI_ENHANCEMENT") != "true" and is_ollama_available()

def get_available_ollama_models(api_base=None):
    api_base = api_base or os.getenv("OLLAMA_API_BASE", "http://localhost:11434")
    if not is_ollama_available(api_base):
        return ["llama3.2", "llama3.1", "deepseek-r1"]
    try:
        response = requests.get(f"{api_base}/api/tags", timeout=1.0)
        response.raise_for_status()
        return [m["name"] for m in response.json().get("models", [])] or ["llama3.2"]
    except Exception:
        return ["llama3.2", "llama3.1"]

@tool
def enhance_solution(problem_description: str, existing_solution: str, log_patterns: list) -> dict:
    """
    Enhance a basic solution to a log issue using AI.

    Args:
        problem_description (str): A short description of the identified problem.
        existing_solution (str): The base solution already suggested.
        log_patterns (list): A list of log message patterns related to the problem.

    Returns:
        dict: An enhanced solution with detailed explanation and steps.
    """
    pass  # used by SmolAgents, logic handled elsewhere

def enhance_solution_direct(model, problem, solution, log_examples):
    log_text = "\n".join(log_examples or ["No examples"])
    prompt = f"""Enhance this log analysis solution:
Problem: {problem}
Basic solution: {solution}
Log examples:
{log_text}
Provide a detailed explanation and specific steps to resolve the issue."""
    try:
        if os.getenv("DEBUG") == "1":
            print(f"Prompt:\n{prompt[:300]}...")
        return model(prompt, options={"temperature": 0.5, "top_p": 0.85, "num_predict": 2000})
    except Exception as e:
        print(f"Error enhancing solution for '{problem}': {e}")
        return solution

def get_agent(model_name=None, api_base=None):
    model = OllamaModel(model_name, api_base)
    return CodeAgent(model=model, tools=[enhance_solution]), model

def enhance_solutions(analysis_results):
    if not is_ai_enhancement_enabled():
        print("AI enhancement is disabled.")
        analysis_results["ai_enhancement_used"] = False
        return analysis_results
    model_name = os.getenv("OLLAMA_MODEL", "llama3.2")
    api_base = os.getenv("OLLAMA_API_BASE", "http://localhost:11434")
    agent, model = get_agent(model_name, api_base)
    enhanced = []
    for s in analysis_results.get("solutions", []):
        problem, base = s.get("problem", ""), s.get("solution", "")
        patterns = [p["pattern"] for p in analysis_results.get("analysis", {}).get("error_patterns", [])
                    if any(k in p["pattern"].lower() for k in problem.lower().split())][:3]
        new_sol = enhance_solution_direct(model, problem, base, patterns)
        enhanced.append({
            "problem": problem,
            "solution": new_sol if new_sol != base else base,
            "ai_enhanced": new_sol != base,
            "original_solution": base if new_sol != base else None
        })
    analysis_results["solutions"] = enhanced
    analysis_results["ai_enhancement_used"] = True
    analysis_results["ollama_model_used"] = model_name
    return analysis_results