import csv
import io
from datetime import datetime
from typing import List
from fastapi import HTTPException
from fastapi.responses import StreamingResponse
from models.schemas import Lead

class ExportService:
    # Service for Exporting Lead Data
    
    @staticmethod
    def export_leads_to_csv(leads: List[Lead]) -> StreamingResponse:
        # Export Leads to CSV Format
        if not leads:
            raise HTTPException(status_code=400, detail="No leads provided for export")
        
        # Create CSV in Memory
        output = io.StringIO()
        fieldnames = [
            "Company", "Industry", "Location", "Website", "LinkedIn URL",
            "Contact", "Employees", "Priority", "Outreach Angle", "Last Updated"
        ]
        
        writer = csv.DictWriter(output, fieldnames=fieldnames)
        writer.writeheader()
        
        for lead in leads:
            writer.writerow({
                "Company": lead.company,
                "Industry": lead.industry,
                "Location": lead.location,
                "Website": lead.website,
                "LinkedIn URL": lead.linkedinUrl,
                "Contact": lead.contact,
                "Employees": lead.employees,
                "Priority": lead.priority,
                "Outreach Angle": lead.outreachAngle,
                "Last Updated": lead.lastUpdated
            })
        
        # Convert to Bytes for Streaming
        output.seek(0)
        csv_content = output.getvalue()
        output.close()
        
        # Create Streaming Response
        def generate_csv():
            yield csv_content.encode('utf-8')
        
        filename = f"leads_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        
        return StreamingResponse(
            generate_csv(),
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )