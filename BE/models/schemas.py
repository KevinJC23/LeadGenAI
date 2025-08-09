from typing import List, Optional
from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum

# Request Model for Lead Search
class SearchRequest(BaseModel):
    industry: str
    location: str

# Lead Data Model
class Lead(BaseModel):
    id: str
    company: str
    industry: str
    location: str
    website: Optional[str] = None
    linkedinUrl: Optional[str] = None
    contact: Optional[str] = None
    employees: Optional[str] = None
    priority: Optional[str] = None
    outreachAngle: Optional[str] = None
    lastUpdated: Optional[str] = None

# Response Model for Lead Search
class SearchResponse(BaseModel):
    leads: List[Lead]
    total: int

# Health Check Response Model
class HealthResponse(BaseModel):
    status: str
    apollo_api: str
    timestamp: str

# Outreach Message Enums
class MessageType(str, Enum):
    COLD_EMAIL = "cold_email"
    LINKEDIN_MESSAGE = "linkedin_message"
    COLD_CALL_SCRIPT = "cold_call_script"

class ToneType(str, Enum):
    PROFESSIONAL = "professional"
    FRIENDLY = "friendly"
    CASUAL = "casual"
    URGENT = "urgent"

class PersonalizationLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium" 
    HIGH = "high"

# Outreach Request Models
class OutreachRequest(BaseModel):
    message_type: MessageType = Field(..., description="Type of outreach message")
    tone: ToneType = Field(default=ToneType.PROFESSIONAL, description="Tone of the message")
    personalization_level: PersonalizationLevel = Field(default=PersonalizationLevel.MEDIUM, description="Level of personalization")
    target_role: Optional[str] = Field(default="Decision Maker", description="Target recipient role")
    company_description: Optional[str] = Field(default=None, description="Description of your company")
    value_proposition: Optional[str] = Field(default=None, description="Your value proposition")
    sender_name: Optional[str] = Field(default=None, description="Sender's name")
    additional_context: Optional[str] = Field(default=None, description="Additional context or specific requirements")
    lead: Optional[Lead] = Field(default=None, description="Lead data for message generation") 

class BulkOutreachRequest(BaseModel):
    lead_ids: List[str] = Field(..., description="List of lead IDs to generate messages for")
    outreach_request: OutreachRequest = Field(..., description="Outreach configuration")

# Outreach Message Models
class OutreachMessage(BaseModel):
    id: Optional[str] = Field(default=None)
    lead_id: str = Field(..., description="Associated lead ID")
    subject: Optional[str] = Field(default=None, description="Message subject (for emails)")
    message: str = Field(..., description="Generated message content")
    tone: ToneType
    message_type: MessageType
    personalization_level: PersonalizationLevel
    generated_at: Optional[datetime] = Field(default_factory=datetime.now)
    quality_score: Optional[float] = Field(default=None, description="AI-generated quality score")
    key_personalization_points: Optional[List[str]] = Field(default=[], description="Key personalization elements used")

# Message Quality Analysis Models
class MessageQualityAnalysis(BaseModel):
    message_id: str
    overall_score: float = Field(..., ge=0, le=10, description="Overall quality score")
    personalization_score: float = Field(..., ge=0, le=10, description="Personalization quality")
    clarity_score: float = Field(..., ge=0, le=10, description="Message clarity")
    engagement_score: float = Field(..., ge=0, le=10, description="Engagement potential")
    call_to_action_score: float = Field(..., ge=0, le=10, description="CTA effectiveness")
    feedback: List[str] = Field(default=[], description="Improvement suggestions")
    strengths: List[str] = Field(default=[], description="Message strengths")
    improvements: List[str] = Field(default=[], description="Areas for improvement")

# Outreach Response Models
class OutreachResponse(BaseModel):
    message: OutreachMessage
    analysis: Optional[MessageQualityAnalysis] = None
    success: bool = True
    error: Optional[str] = None

class BulkOutreachResponse(BaseModel):
    messages: List[OutreachMessage]
    success_count: int
    failed_count: int
    total_count: int
    errors: List[str] = Field(default=[])
    success: bool = True