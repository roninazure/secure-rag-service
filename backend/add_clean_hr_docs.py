#!/usr/bin/env python3
"""Add clean HR policies to the knowledge base"""
import requests
import json

API_URL = "http://3.87.201.201:8000/api"

# Clean HR policy documents without Dan Pfeiffer references
HR_DOCUMENTS = [
    {
        "title": "PTO Policy",
        "content": """PTO (Paid Time Off) Policy

All full-time employees are entitled to 20 days of PTO per year, accruing at 1.67 days per month. 
PTO requests must be submitted at least two weeks in advance for periods of 5 or more consecutive days.
Shorter PTO requests require 48 hours advance notice.
All PTO requests must be approved by the HR Director.
Unused PTO may be carried over up to 5 days into the next year.
PTO payout upon termination is provided for accrued but unused days up to a maximum of 20 days."""
    },
    {
        "title": "Remote Work Policy", 
        "content": """Remote Work Policy

Our firm offers flexible remote work arrangements for eligible employees.
Full-time employees may work remotely up to 3 days per week after completing their 90-day probationary period.
Remote work schedules must be approved in advance by the HR Director.
Employees must maintain core hours of 10 AM to 3 PM in their local time zone.
Remote workers must have reliable internet connection and a quiet workspace.
The firm will provide necessary equipment including laptop and software licenses.
Remote work privileges may be revoked if performance standards are not met."""
    },
    {
        "title": "Time Off Approval Process",
        "content": """Time Off and Leave Approval Process

All requests for time off, including PTO, sick leave, personal days, and extended leave must follow this process:
1. Submit request through the HR portal or email to hr@firm.com
2. Requests are reviewed by your direct supervisor
3. Final approval must be granted by the HR Director
4. The HR Director has sole authority to approve all time off requests
5. Emergency leave should be communicated as soon as possible to both your supervisor and HR
6. For questions about time off policies, contact the HR department at hr@firm.com"""
    },
    {
        "title": "Employee Benefits",
        "content": """Employee Benefits Overview

Our firm provides comprehensive benefits to all full-time employees:
- Health insurance: Medical, dental, and vision coverage
- 401(k) retirement plan with 4% company match
- Life insurance: 2x annual salary
- Short-term and long-term disability insurance
- Professional development: CLE credits and training reimbursement up to $5,000 annually
- Bar dues and professional memberships covered
- Parking or transit subsidy up to $250 per month
- Gym membership reimbursement up to $100 per month"""
    }
]

def ingest_documents():
    """Ingest HR documents into the knowledge base"""
    print("Adding clean HR policies to knowledge base...")
    
    # Convert documents to simple strings for ingestion
    documents = [doc["content"] for doc in HR_DOCUMENTS]
    
    payload = {
        "documents": documents,
        "metadata": []  # Empty list for metadata
    }
    
    print(f"\nIngesting {len(documents)} HR policy documents...")
    
    try:
        response = requests.post(
            f"{API_URL}/ingest",
            json=payload,
            timeout=30
        )
            
        if response.status_code == 200:
            result = response.json()
            print(f"✓ Success: {result.get('message', 'Documents ingested')}")
            print(f"  Chunks created: {result.get('chunks_created', 'Unknown')}")
        else:
            print(f"✗ Error {response.status_code}: {response.text}")
            
    except Exception as e:
        print(f"✗ Exception: {e}")
    
    print("\n✓ Clean HR policies ingestion complete!")

if __name__ == "__main__":
    ingest_documents()
