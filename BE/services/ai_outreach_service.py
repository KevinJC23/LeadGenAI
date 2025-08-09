import os
import google.generativeai as genai
from typing import Dict, Any, List
import json
import asyncio
from models.schemas import Lead, OutreachMessage, OutreachRequest
from core.config import settings
import logging

logger = logging.getLogger(__name__)

class AIOutreachService:
    def __init__(self):
        # Configure Gemini API
        genai.configure(api_key=settings.GEMINI_API_KEY)
        self.model = genai.GenerativeModel('gemini-1.5-flash')
        
    async def generate_outreach_message(
        self, 
        lead: Lead, 
        request: OutreachRequest
    ) -> OutreachMessage:
        # Generate Personalized Outreach Message for a Specific Lead
        try:
            prompt = self._create_outreach_prompt(lead, request)
            
            # Generate Content Using Gemini
            response = await asyncio.to_thread(
                self.model.generate_content, prompt
            )
            
            # Parse the Response
            message_data = self._parse_ai_response(response.text)
            
            return OutreachMessage(
                lead_id=lead.id,
                subject=message_data.get('subject', f'Partnership Opportunity with {lead.company}'),
                message=message_data.get('message', ''),
                tone=request.tone,
                message_type=request.message_type,
                personalization_level=request.personalization_level,
                generated_at=None 
            )
            
        except Exception as e:
            logger.error(f"Failed to generate outreach message for lead {lead.id}: {str(e)}")
            raise Exception(f"AI message generation failed: {str(e)}")
    
    async def generate_bulk_messages(
        self, 
        leads: List[Lead], 
        request: OutreachRequest
    ) -> List[OutreachMessage]:
        # Generate Outreach Messages for Multiple Leads
        messages = []
        
        for lead in leads:
            try:
                message = await self.generate_outreach_message(lead, request)
                messages.append(message)
            except Exception as e:
                logger.error(f"Failed to generate message for lead {lead.id}: {str(e)}")
                # Create a Fallback Message
                fallback_message = self._create_fallback_message(lead, request)
                messages.append(fallback_message)
        
        return messages
    
    def _create_outreach_prompt(self, lead: Lead, request: OutreachRequest) -> str:
        # Create a Detailed Prompt for the AI Model
        base_prompt = f"""
            You are an expert B2B sales copywriter. Generate a personalized outreach message based on the following information:

            LEAD INFORMATION:
            - Company: {lead.company}
            - Industry: {lead.industry}
            - Location: {lead.location}
            - Website: {lead.website}
            - LinkedIn: {lead.linkedinUrl}
            - Contact: {lead.contact}
            - Employees: {lead.employees}
            - Priority: {lead.priority}
            - Suggested Outreach Angle: {lead.outreachAngle}

            MESSAGE REQUIREMENTS:
            - Type: {request.message_type}
            - Tone: {request.tone}
            - Personalization Level: {request.personalization_level}
            - Target Role: {request.target_role or 'Decision Maker'}
            - Company Description: {request.company_description or 'Our company'}
            - Value Proposition: {request.value_proposition or 'We help businesses grow'}
        """

        # Add Specific Instructions Based on Message Type
        if request.message_type == "cold_email":
            base_prompt += """
                EMAIL SPECIFIC REQUIREMENTS:
                - Create both a compelling subject line and email body
                - Keep email between 100-150 words
                - Include a clear call-to-action
                - Make it mobile-friendly
                - Avoid spam trigger words
            """
        elif request.message_type == "linkedin_message":
            base_prompt += """
                LINKEDIN SPECIFIC REQUIREMENTS:
                - Keep message under 300 characters for initial connection
                - Reference something specific from their LinkedIn profile or company
                - Be conversational and professional
                - Include a soft call-to-action
            """
        elif request.message_type == "cold_call_script":
            base_prompt += """
                COLD CALL SCRIPT REQUIREMENTS:
                - Create an opening, value proposition, and closing
                - Include handling common objections
                - Keep it conversational and natural
                - Provide timing cues and pauses
                - Maximum 2-minute script
            """

        # Add Tone-Specific Instructions
        tone_instructions = {
            "professional": "Use formal business language, be respectful and corporate",
            "friendly": "Use warm, approachable language while maintaining professionalism",
            "casual": "Use conversational tone, be relatable but still business-focused",
            "urgent": "Create sense of urgency without being pushy, emphasize time-sensitive opportunities"
        }
        
        base_prompt += f"\nTONE INSTRUCTIONS: {tone_instructions.get(request.tone, 'Be professional')}"
        
        # Add Personalization Level Instructions
        if request.personalization_level == "high":
            base_prompt += """
                HIGH PERSONALIZATION:
                - Research and reference specific company achievements, recent news, or industry challenges
                - Mention specific pain points relevant to their industry
                - Use company-specific terminology
                - Reference mutual connections or shared experiences if applicable
            """
        elif request.personalization_level == "medium":
            base_prompt += """
                MEDIUM PERSONALIZATION:
                - Use industry-specific language and challenges
                - Reference general company information
                - Mention location or company size relevance
            """
        else:
            base_prompt += """
                LOW PERSONALIZATION:
                - Use general business language
                - Keep references broad but relevant
                - Focus on universal business challenges
            """

        base_prompt += """
            OUTPUT FORMAT:
            Return your response as a JSON object with the following structure:
            {
                "subject": "Subject line (for emails only)",
                "message": "The complete outreach message",
                "key_personalization_points": ["point1", "point2", "point3"],
                "call_to_action": "The specific CTA used",
                "tone_score": 9.5
            }

            Make sure the message is highly engaging, personalized, and likely to get a response.
        """
        
        return base_prompt
    
    def _parse_ai_response(self, response_text: str) -> Dict[str, Any]:
        # Parse AI Response and Extract Structured Data
        try:
            # Try to Find JSON in the Response
            start_idx = response_text.find('{')
            end_idx = response_text.rfind('}') + 1
            
            if start_idx != -1 and end_idx > start_idx:
                json_str = response_text[start_idx:end_idx]
                return json.loads(json_str)
            else:
                # If No JSON Found, Treat Entire Response as Message
                return {
                    "subject": "Partnership Opportunity",
                    "message": response_text,
                    "key_personalization_points": [],
                    "call_to_action": "Let's connect",
                    "tone_score": 8.0
                }
        except json.JSONDecodeError:
            # Fallback Parsing
            return {
                "subject": "Partnership Opportunity", 
                "message": response_text,
                "key_personalization_points": [],
                "call_to_action": "Let's connect",
                "tone_score": 8.0
            }
    
    def _create_fallback_message(self, lead: Lead, request: OutreachRequest) -> OutreachMessage:
        # Create a Basic Fallback Message When AI Generation Fails
        if request.message_type == "cold_email":
            subject = f"Partnership Opportunity with {lead.company}"
            message = f"""Hi {lead.contact.split()[0] if lead.contact != 'N/A' else 'there'},

                I hope this email finds you well. I came across {lead.company} and was impressed by your work in the {lead.industry} industry.

                {request.value_proposition or 'Our company specializes in helping businesses like yours achieve better results.'}

                I'd love to explore how we might be able to support {lead.company}'s goals. Would you be open to a brief conversation?

                Best regards,
                {request.sender_name or 'Your Sales Team'}
            """
        
        elif request.message_type == "linkedin_message":
            subject = f"Connection with {lead.company}"
            message = f"""Hi {lead.contact.split()[0] if lead.contact != 'N/A' else 'there'},

                I noticed your work at {lead.company} in {lead.industry}. {request.value_proposition or 'We help companies in your industry achieve better results.'}

                Would love to connect and share some insights that might be valuable for {lead.company}.

                Best,
                {request.sender_name or 'Your Name'}
            """
        
        else:  
            subject = f"Call Script for {lead.company}"
            message = f"""Opening: Hi, this is [Your Name] from [Your Company]. I'm calling because I noticed {lead.company} is doing great work in {lead.industry}.

                Value Prop: {request.value_proposition or 'We help companies like yours improve their results and efficiency.'}

                Question: I'd love to learn more about {lead.company}'s current challenges in this area. Do you have a few minutes to chat?

                Close: If not now, when would be a better time to connect?
            """
        
        return OutreachMessage(
            lead_id=lead.id,
            subject=subject,
            message=message,
            tone=request.tone,
            message_type=request.message_type,
            personalization_level=request.personalization_level,
            generated_at=None
        )

    async def analyze_message_quality(self, message: OutreachMessage) -> Dict[str, Any]:
        # Analyze the Quality of a Generated Message
        try:
            analysis_prompt = f"""
                Analyze the following outreach message and provide a quality score and feedback:

                MESSAGE TYPE: {message.message_type}
                TONE: {message.tone}
                SUBJECT: {message.subject}
                MESSAGE: {message.message}

                Provide analysis in JSON format:
                {{
                    "overall_score": 8.5,
                    "personalization_score": 7.0,
                    "clarity_score": 9.0,
                    "engagement_score": 8.0,
                    "call_to_action_score": 8.5,
                    "feedback": ["Suggestion 1", "Suggestion 2"],
                    "strengths": ["Strength 1", "Strength 2"],
                    "improvements": ["Improvement 1", "Improvement 2"]
                }}
            """
            
            response = await asyncio.to_thread(
                self.model.generate_content, analysis_prompt
            )
            
            return self._parse_ai_response(response.text)
            
        except Exception as e:
            logger.error(f"Failed to analyze message quality: {str(e)}")
            return {
                "overall_score": 7.5,
                "personalization_score": 7.0,
                "clarity_score": 7.5,
                "engagement_score": 7.0,
                "call_to_action_score": 7.5,
                "feedback": ["Message generated successfully"],
                "strengths": ["Clear messaging"],
                "improvements": ["Could be more personalized"]
            }