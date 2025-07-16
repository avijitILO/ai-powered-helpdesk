import httpx
from langchain.llms.base import LLM
from langchain.callbacks.manager import CallbackManagerForLLMRun
from typing import Optional, List, Any
import json
from ..config import settings

class OllamaLLM(LLM):
    """Custom Ollama LLM wrapper for Langchain"""
    
    model: str = "llama2"
    base_url: str = "http://ollama:11434"
    
    @property
    def _llm_type(self) -> str:
        return "ollama"
    
    def _call(
        self,
        prompt: str,
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> str:
        headers = {"Content-Type": "application/json"}
        data = {
            "model": self.model,
            "prompt": prompt,
            "stream": False
        }
        if stop:
            data["stop"] = stop
            
        with httpx.Client() as client:
            response = client.post(
                f"{self.base_url}/api/generate",
                headers=headers,
                json=data,
                timeout=60.0
            )
            response.raise_for_status()
            return response.json()["response"]

class LLMService:
    def __init__(self):
        self.llm = None
        self.model_name = settings.OLLAMA_MODEL
        
    async def initialize(self):
        """Initialize the LLM service and download model if needed"""
        self.llm = OllamaLLM(
            model=self.model_name,
            base_url=settings.OLLAMA_URL
        )
        
        # Pull model if not exists
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    f"{settings.OLLAMA_URL}/api/pull",
                    json={"name": self.model_name},
                    timeout=300.0
                )
                print(f"Model {self.model_name} ready")
            except Exception as e:
                print(f"Error pulling model: {e}")
    
    async def generate_response(self, prompt: str, context: str = "") -> str:
        """Generate response using the LLM"""
        if not self.llm:
            raise Exception("LLM not initialized")
            
        full_prompt = f"""You are an AI helpdesk assistant for an organization. 
        You help with IT, HR, and Finance queries. Be helpful, concise, and professional.
        
        Context: {context}
        
        User Query: {prompt}
        
        Response:"""
        
        return self.llm(full_prompt)
    
    async def classify_department(self, query: str) -> str:
        """Classify query to appropriate department"""
        prompt = f"""Classify the following query into one of these departments: IT, HR, Finance, Operations, Security.
        Only respond with the department name.
        
        Query: {query}
        
        Department:"""
        
        response = self.llm(prompt).strip()
        
        # Validate response
        valid_departments = ["IT", "HR", "Finance", "Operations", "Security"]
        if response not in valid_departments:
            return "IT"  # Default to IT
        return response
    
    async def cleanup(self):
        """Cleanup resources"""
        pass