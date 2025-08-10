import uuid
from datetime import datetime
from typing import Dict, Any
from models.schemas import Lead

class DataTransformer:
    # Service for Transforming Data Between Different Formats
    @staticmethod
    def get_priority_from_employee_count(employee_count: int) -> str:
        # Determine Priority Based on Employee Count
        if employee_count < 50:
            return "Low"
        elif employee_count < 200:
            return "Medium"
        else:
            return "High"
    
    @staticmethod
    def get_outreach_angle_from_industry(industry: str) -> str:
        # Generate Outreach Angle Based on Industry
        outreach_angles = {
            "technology": "Digital transformation solutions",
            "healthcare": "HIPAA-compliant solutions",
            "finance": "Regulatory compliance tools",
            "manufacturing": "Operational efficiency improvements",
            "retail": "Customer experience enhancement",
            "education": "Learning management solutions"
        }
        
        for key, angle in outreach_angles.items():
            if key.lower() in industry.lower():
                return angle
        
        return "Business growth solutions"
    
    @staticmethod
    def transform_apollo_data_to_lead(company_data: Dict[str, Any]) -> Lead:
        # Transform Apollo API Company Data to Lead Model
        
        # Extract Company Information
        organization = company_data.get("organization", {})
        person = company_data.get("person", {})
        
        # Get Employee Count
        employee_count = organization.get("estimated_num_employees", 0)
        employees_display = str(employee_count) if employee_count else "Unknown"
        
        # Determine Priority & Outreach Angle
        priority = DataTransformer.get_priority_from_employee_count(employee_count)
        industry = organization.get("industry", "")
        outreach_angle = DataTransformer.get_outreach_angle_from_industry(industry)
        
        # Get Contact Information
        primary_phone = organization.get("primary_phone", {})
        contact_number = primary_phone.get("number", "")

        if contact_number:
            contact_info = contact_number
        else:
            contact_name = person.get("name")
            contact_email = person.get("email")
            if contact_name:
                contact_info = contact_name
                if contact_email:
                    contact_info += f" ({contact_email})"
            else:
                contact_info = "Contact Not Available"
        
        # Format Location
        city = organization.get("city", "")
        state = organization.get("state", "")
        location = f"{city}, {state}".strip(", ")
        
        return Lead(
            id=str(uuid.uuid4()),
            company=organization.get("name", "Unknown Company"),
            industry=industry,
            location=location,
            website=organization.get("website_url", "N/A"),
            linkedinUrl=organization.get("linkedin_url", "N/A"),
            contact=contact_info,
            employees=employees_display,
            priority=priority,
            outreachAngle=outreach_angle,
            lastUpdated=datetime.now().strftime("%Y-%m-%d")
        )