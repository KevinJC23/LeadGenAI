from fastapi import APIRouter, HTTPException, Query, Body
from typing import List, Optional
from datetime import datetime
import uuid

from models.schemas import SearchRequest, SearchResponse, Lead, HealthResponse, OutreachRequest, BulkOutreachRequest, OutreachResponse, BulkOutreachResponse, MessageQualityAnalysis
from services.apollo_client import apollo_client
from services.data_transformer import DataTransformer
from services.export_service import ExportService
from services.scraper_service import scrape_apollo_companies, scrape_yellow_pages_companies
from services.ai_outreach_service import AIOutreachService
from core.config import settings

router = APIRouter()
ai_outreach_service = AIOutreachService()

@router.post("/search-leads", response_model=SearchResponse)
async def search_leads(request: SearchRequest):
    # Search for Leads Based on Industry and Location Using Apollo API
    if not apollo_client:
        raise HTTPException(
            status_code=500,
            detail="Apollo API Key Not Configured. Please Set APOLLO_API_KEY Environment Variable."
        )
    
    try:
        # Search Companies Using Apollo API
        apollo_response = await apollo_client.search_companies(
            industry=request.industry,
            location=request.location,
            per_page=settings.MAX_PAGE_SIZE
        )
        
        # Transform Apollo Data to Lead Format
        leads = []
        companies = apollo_response.get("organizations", [])
        people = apollo_response.get("people", [])
        
        # Create a Mapping of Organization ID to People
        org_people_map = {}
        for person in people:
            org_id = person.get("organization_id")
            if org_id:
                if org_id not in org_people_map:
                    org_people_map[org_id] = []
                org_people_map[org_id].append(person)
        
        # Process Companies & Associated People
        for company in companies:
            company_id = company.get("id")
            associated_people = org_people_map.get(company_id, [{}])
            
            # Use the First Person as the Primary Contact
            primary_person = associated_people[0] if associated_people else {}
            
            # Combine Company and Person Data
            combined_data = {
                "organization": company,
                "person": primary_person
            }
            
            lead = DataTransformer.transform_apollo_data_to_lead(combined_data)
            leads.append(lead)
        
        return SearchResponse(
            leads=leads,
            total=len(leads)
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error searching leads: {str(e)}"
        )

@router.post("/scrape-leads-apollo", response_model=SearchResponse)
async def scrape_leads_apollo(
    request: SearchRequest,
    max_pages: int = Query(default=2, ge=1, le=5, description="Maximum pages to scrape (1-5)")
):
    try:
        # Scrape Companies Using Playwright
        scraped_companies = await scrape_apollo_companies(
            industry=request.industry,
            location=request.location,
            max_pages=max_pages
        )
        
        # Transform Scraped Data to Lead Format
        leads = []
        for company_data in scraped_companies:
            # Create a Mock Structure Similar to Apollo API Response
            mock_apollo_data = {
                "organization": {
                    "name": company_data.get("company", "Unknown Company"),
                    "industry": company_data.get("industry", "Unknown"),
                    "city": company_data.get("location", "").split(",")[0].strip() if company_data.get("location") else "",
                    "state": company_data.get("location", "").split(",")[1].strip() if "," in company_data.get("location", "") else "",
                    "website_url": company_data.get("website", "N/A"),
                    "linkedin_url": company_data.get("linkedin_url", "N/A"),
                    "estimated_num_employees": 0  
                },
                "person": {
                    "name": "Contact not available",
                    "email": ""
                }
            }
            
            lead = DataTransformer.transform_apollo_data_to_lead(mock_apollo_data)
            leads.append(lead)
        
        return SearchResponse(
            leads=leads,
            total=len(leads)
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error scraping Apollo leads: {str(e)}"
        )

@router.post("/scrape-leads-yellowpages", response_model=SearchResponse)
async def scrape_leads_yellowpages(request: SearchRequest):
    try:
        # Scrape Companies From Yellow Pages
        scraped_companies = await scrape_yellow_pages_companies(
            industry=request.industry,
            location=request.location
        )
        
        # Transform Scraped Data to Lead Format
        leads = []
        for company_data in scraped_companies:
            # Create a Mock Structure Similar to Apollo API Response
            mock_apollo_data = {
                "organization": {
                    "name": company_data.get("company", "Unknown Company"),
                    "industry": company_data.get("industry", "Unknown"),
                    "city": company_data.get("location", "").split(",")[0].strip() if company_data.get("location") else "",
                    "state": company_data.get("location", "").split(",")[1].strip() if "," in company_data.get("location", "") else "",
                    "website_url": company_data.get("website", "N/A"),
                    "linkedin_url": "N/A",  
                    "estimated_num_employees": 0
                },
                "person": {
                    "name": "Contact not available",
                    "email": company_data.get("contact_phone", "")
                }
            }
            
            lead = DataTransformer.transform_apollo_data_to_lead(mock_apollo_data)
            # Add Phone Number to Contact Info if Available
            if company_data.get("contact_phone", "N/A") != "N/A":
                lead.contact = f"Phone: {company_data.get('contact_phone')}"
            
            leads.append(lead)
        
        return SearchResponse(
            leads=leads,
            total=len(leads)
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error Scraping Yellow Pages Leads: {str(e)}"
        )

@router.post("/search-leads-hybrid", response_model=SearchResponse)
async def search_leads_hybrid(
    request: SearchRequest,
    use_scraping: bool = Query(default=False, description="Include Web Scraping as Fallback"),
    scrape_source: str = Query(default="yellowpages", description="Scraping Source: 'Apollo' or 'Yellowpages'"),
    max_scrape_pages: int = Query(default=1, ge=1, le=3, description="Max Pages to Scrape if API Fails")
):
    leads = []
    api_success = False
    
    # Try Apollo API First
    if apollo_client:
        try:
            apollo_response = await apollo_client.search_companies(
                industry=request.industry,
                location=request.location,
                per_page=settings.MAX_PAGE_SIZE
            )
            
            # Process API Response
            companies = apollo_response.get("organizations", [])
            people = apollo_response.get("people", [])
            
            org_people_map = {}
            for person in people:
                org_id = person.get("organization_id")
                if org_id:
                    if org_id not in org_people_map:
                        org_people_map[org_id] = []
                    org_people_map[org_id].append(person)
            
            for company in companies:
                company_id = company.get("id")
                associated_people = org_people_map.get(company_id, [{}])
                primary_person = associated_people[0] if associated_people else {}
                
                combined_data = {
                    "organization": company,
                    "person": primary_person
                }
                
                lead = DataTransformer.transform_apollo_data_to_lead(combined_data)
                leads.append(lead)
            
            api_success = True
            
        except Exception as e:
            print(f"API failed: {str(e)}")
            api_success = False
    
    # Fallback to Scraping if API Failed and Scraping is Enabled
    if not api_success and use_scraping:
        try:
            if scrape_source == "apollo":
                scraped_companies = await scrape_apollo_companies(
                    industry=request.industry,
                    location=request.location,
                    max_pages=max_scrape_pages
                )
            else:  
                scraped_companies = await scrape_yellow_pages_companies(
                    industry=request.industry,
                    location=request.location
                )
            
            for company_data in scraped_companies:
                mock_apollo_data = {
                    "organization": {
                        "name": company_data.get("company", "Unknown Company"),
                        "industry": company_data.get("industry", "Unknown"),
                        "city": company_data.get("location", "").split(",")[0].strip() if company_data.get("location") else "",
                        "state": company_data.get("location", "").split(",")[1].strip() if "," in company_data.get("location", "") else "",
                        "website_url": company_data.get("website", "N/A"),
                        "linkedin_url": company_data.get("linkedin_url", "N/A"),
                        "estimated_num_employees": 0
                    },
                    "person": {
                        "name": "Contact not available", 
                        "email": company_data.get("contact_phone", "") if scrape_source == "yellowpages" else ""
                    }
                }
                
                lead = DataTransformer.transform_apollo_data_to_lead(mock_apollo_data)
                # Add Phone for Yellow Pages Results
                if scrape_source == "yellowpages" and company_data.get("contact_phone", "N/A") != "N/A":
                    lead.contact = f"Phone: {company_data.get('contact_phone')}"
                
                leads.append(lead)
                
        except Exception as e:
            if not leads:
                raise HTTPException(
                    status_code=500,
                    detail=f"Both API and Scraping Failed: {str(e)}"
                )
    
    if not leads and not api_success:
        raise HTTPException(
            status_code=500,
            detail="Apollo API Not Configured & Scraping Disabled. Please Set APOLLO_API_KEY or Enable Scraping."
        )
    
    return SearchResponse(
        leads=leads,
        total=len(leads)
    )

@router.get("/leads", response_model=List[Lead])
async def get_all_leads():
    # Get All Stored Leads for Outreach Message Generation
    try:
        return list(leads_storage.values())
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to Retrieve Leads: {str(e)}")

@router.get("/leads/{lead_id}", response_model=Lead)
async def get_lead(lead_id: str):
    # Get a Specific Lead by ID
    lead = leads_storage.get(lead_id)
    if not lead:
        raise HTTPException(status_code=404, detail="Lead Not Found")
    return lead

@router.post("/export-leads")
async def export_leads(leads: List[Lead]):
    # Export Selected Leads to CSV Format
    return ExportService.export_leads_to_csv(leads)

@router.get("/health", response_model=HealthResponse)
async def health_check():
    # Health Check Endpoint
    apollo_status = "configured" if settings.is_apollo_configured else "not configured"
    
    return HealthResponse(
        status="healthy",
        apollo_api=apollo_status,
        timestamp=datetime.now().isoformat()
    )

@router.post("/outreach/generate", response_model=OutreachResponse)
async def generate_outreach_message(
    request: OutreachRequest = Body(...),
    lead_id: Optional[str] = None
):
    lead = await get_lead_by_id(lead_id) if lead_id else None

    if not lead and getattr(request, "lead", None):
        lead = request.lead

    if not lead:
        raise HTTPException(status_code=404, detail="Lead Not Found or Not Provided")

    # Generate a Personalized Outreach Message for a Specific Lead
    try:
        message = await ai_outreach_service.generate_outreach_message(lead, request)
        message.id = str(uuid.uuid4())
        store_message(message)

        analysis = None
        try:
            analysis_data = await ai_outreach_service.analyze_message_quality(message)
            analysis = MessageQualityAnalysis(
                message_id=message.id,
                **analysis_data
            )
            message.quality_score = analysis.overall_score
        except Exception as e:
            print(f"Failed to Analyze Message Quality: {e}")

        return OutreachResponse(
            message=message,
            analysis=analysis,
            success=True
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to Generate Outreach Message: {str(e)}")

@router.post("/outreach/generate-bulk", response_model=BulkOutreachResponse)
async def generate_bulk_outreach_messages(request: BulkOutreachRequest):
    # Generate Outreach Messages for Multiple Leads
    try:
        # Fetch All Leads
        leads = []
        errors = []
        
        for lead_id in request.lead_ids:
            try:
                lead = await get_lead_by_id(lead_id) 
                if lead:
                    leads.append(lead)
                else:
                    errors.append(f"Lead {lead_id} Not Found")
            except Exception as e:
                errors.append(f"Failed to Fetch Lead {lead_id}: {str(e)}")
        
        if not leads:
            raise HTTPException(status_code=400, detail="No Valid Leads Found")
        
        # Generate Messages
        messages = await ai_outreach_service.generate_bulk_messages(leads, request.outreach_request)
        
        # Assign IDs and Analyze Quality
        for message in messages:
            message.id = str(uuid.uuid4())
        
        success_count = len([m for m in messages if m.message])
        failed_count = len(messages) - success_count
        
        return BulkOutreachResponse(
            messages=messages,
            success_count=success_count,
            failed_count=failed_count,
            total_count=len(messages),
            errors=errors,
            success=True
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to Generate Bulk Messages: {str(e)}")

@router.get("/outreach/message/{message_id}/analysis", response_model=MessageQualityAnalysis)
async def analyze_message_quality(message_id: str):
    # Analyze the Quality of a Generated Message
    try:
        message = await get_message_by_id(message_id)  
        
        if not message:
            raise HTTPException(status_code=404, detail="Message Not Found")
        
        analysis_data = await ai_outreach_service.analyze_message_quality(message)
        
        analysis = MessageQualityAnalysis(
            message_id=message_id,
            **analysis_data
        )
        
        return analysis
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to Analyze Message: {str(e)}")

@router.get("/outreach/templates")
async def get_message_templates():
    # Get Available Message Templates and Examples
    return {
        "templates": {
            "cold_email": {
                "professional": {
                    "description": "Formal business email approach",
                    "best_for": ["Enterprise clients", "C-level executives", "Formal industries"],
                    "sample_subject": "Partnership Opportunity with [Company Name]"
                },
                "friendly": {
                    "description": "Warm, approachable email style",
                    "best_for": ["SMBs", "Startups", "Creative industries"],
                    "sample_subject": "Love what [Company Name] is doing!"
                }
            },
            "linkedin_message": {
                "casual": {
                    "description": "Conversational LinkedIn approach",
                    "best_for": ["Tech professionals", "Startups", "Modern companies"],
                    "character_limit": 300
                },
                "professional": {
                    "description": "Professional LinkedIn connection",
                    "best_for": ["Traditional industries", "Senior executives"],
                    "character_limit": 300
                }
            },
            "cold_call_script": {
                "friendly": {
                    "description": "Warm, consultative call approach",
                    "best_for": ["Consultative sales", "Relationship building"],
                    "duration": "2-3 minutes"
                }
            }
        },
        "personalization_tips": [
            "Research recent company news or achievements",
            "Reference specific industry challenges",
            "Mention mutual connections when available",
            "Use company-specific terminology",
            "Reference their website or recent content"
        ]
    }

leads_storage: dict = {} 
messages_storage: dict = {}  

# Helper Functions
async def get_lead_by_id(lead_id: str) -> Optional[Lead]:
    # Fetch Lead from In-Memory Storage by ID
    return leads_storage.get(lead_id)

async def get_message_by_id(message_id: str):
    # Fetch Message from In-Memory Storage by ID
    return messages_storage.get(message_id)

def store_lead(lead: Lead) -> None:
    # Store Lead in Memory 
    leads_storage[lead.id] = lead

def store_message(message) -> None:
    # Store Message in Memory
    if message.id:
        messages_storage[message.id] = message