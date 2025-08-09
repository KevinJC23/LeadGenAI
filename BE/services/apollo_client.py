import httpx
from fastapi import HTTPException
from typing import Dict, Any
from core.config import settings

class ApolloAPIClient:    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = settings.APOLLO_API_URL
    
    async def search_companies(self, industry: str, location: str, page: int = 1, per_page: int = 25) -> Dict[str, Any]:
        # Search Companies Using Apollo API
        headers = {
            "Cache-Control": "no-cache",
            "Content-Type": "application/json",
            "X-Api-Key": self.api_key
        }
        
        # Parse Location to Extract City & State/Country
        location_parts = location.split(", ")
        city = location_parts[0] if location_parts else location
        state_country = location_parts[1] if len(location_parts) > 1 else ""
        
        payload = {
            "q_organization_keywords": industry,
            "organization_locations": [f"{city}, {state_country}"] if state_country else [city],
            "page": page,
            "per_page": per_page,
            "organization_num_employees_ranges": [
                "1,10", "11,50", "51,200", "201,500", 
                "501,1000", "1001,5000", "5001,10000", "10001+"
            ]
        }
        
        async with httpx.AsyncClient(timeout=settings.REQUEST_TIMEOUT) as client:
            try:
                response = await client.post(
                    f"{self.base_url}/organizations/search",
                    headers=headers,
                    json=payload
                )
                response.raise_for_status()
                return response.json()
            except httpx.HTTPStatusError as e:
                raise HTTPException(
                    status_code=e.response.status_code,
                    detail=f"Apollo API error: {e.response.text}"
                )
            except httpx.RequestError as e:
                raise HTTPException(
                    status_code=500,
                    detail=f"Request error: {str(e)}"
                )

# Initialize Apollo Client if API Key is Available
apollo_client = ApolloAPIClient(settings.APOLLO_API_KEY) if settings.is_apollo_configured else None