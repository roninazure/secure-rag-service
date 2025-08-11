#!/usr/bin/env python3
"""
Test ingesting a large document to verify chunking works end-to-end
"""

import requests
import json

# API endpoint
BASE_URL = "http://localhost:8000"

def test_large_document_ingestion():
    """Test ingesting a large document that will be chunked"""
    
    # Create a comprehensive HR policy document
    large_document = """
    COMPREHENSIVE EMPLOYEE HANDBOOK
    
    SECTION 1: REMOTE WORK POLICY
    
    Effective Date: January 1, 2024
    Last Updated: December 15, 2023
    Policy Owner: Dan Pfeiffer, VP of Human Resources
    
    1.1 PURPOSE AND SCOPE
    This policy establishes guidelines for remote work arrangements to ensure productivity, maintain team cohesion, and support work-life balance. It applies to all full-time employees across all departments and locations. The policy aims to provide flexibility while maintaining operational excellence and security standards.
    
    1.2 ELIGIBILITY CRITERIA
    Employees must meet the following criteria to be eligible for remote work:
    - Completed probationary period of 90 days with satisfactory performance
    - Role responsibilities that can be effectively performed remotely
    - Demonstrated ability to work independently and meet deadlines
    - No active performance improvement plans or disciplinary actions
    - Manager recommendation and approval
    - Final approval from Dan Pfeiffer or designated HR representative
    
    1.3 APPLICATION AND APPROVAL PROCESS
    Step 1: Employee submits remote work request form via HR portal
    Step 2: Direct manager reviews and provides recommendation within 5 business days
    Step 3: HR department conducts eligibility verification
    Step 4: Dan Pfeiffer reviews and makes final determination within 10 business days
    Step 5: Employee receives written approval or denial with explanation
    Step 6: If approved, employee and manager create remote work agreement
    
    1.4 EQUIPMENT AND TECHNOLOGY REQUIREMENTS
    The company provides a technology stipend of up to $1,500 for initial setup, including:
    - Laptop or desktop computer meeting company specifications
    - External monitor (minimum 24 inches)
    - Ergonomic keyboard and mouse
    - High-quality webcam and headset for video conferencing
    - Necessary software licenses and VPN access
    
    Additionally, the company reimburses up to $75 monthly for high-speed internet (minimum 50 Mbps download, 10 Mbps upload). Employees must maintain a dedicated, quiet workspace free from distractions and meeting professional standards for video calls.
    
    SECTION 2: PAID TIME OFF (PTO) POLICY
    
    Policy Administrator: Dan Pfeiffer, VP of Human Resources
    Review Cycle: Annual (December)
    
    2.1 PTO ACCRUAL RATES
    PTO accrual is based on length of service and employment status:
    - 0-2 years: 15 days annually (1.25 days per month)
    - 3-5 years: 20 days annually (1.67 days per month)
    - 6-10 years: 25 days annually (2.08 days per month)
    - 10+ years: 30 days annually (2.5 days per month)
    
    Part-time employees accrue PTO on a prorated basis. Unused PTO may be carried over up to a maximum of 10 days, subject to manager approval and company policy.
    
    2.2 PTO REQUEST PROCEDURES
    All PTO requests must be submitted through the HR system at least:
    - 2 weeks in advance for requests of 3 or more consecutive days
    - 1 week in advance for 1-2 day requests
    - Emergency leave should be communicated as soon as possible
    
    Approval workflow:
    1. Employee submits request via HR portal
    2. Direct manager reviews based on team coverage and business needs
    3. Requests over 5 consecutive days require Dan Pfeiffer's approval
    4. Employee receives confirmation within 48 hours of submission
    
    2.3 HOLIDAY SCHEDULE
    The company observes the following paid holidays:
    - New Year's Day
    - Martin Luther King Jr. Day
    - Presidents' Day
    - Memorial Day
    - Independence Day
    - Labor Day
    - Thanksgiving (2 days)
    - Christmas (2 days)
    
    Employees required to work on holidays receive premium pay (1.5x regular rate) plus a compensatory day off, subject to manager and Dan Pfeiffer's approval.
    
    SECTION 3: PERFORMANCE MANAGEMENT
    
    3.1 PERFORMANCE REVIEW CYCLE
    All employees participate in formal performance reviews:
    - Annual comprehensive review (December/January)
    - Mid-year check-in (June/July)
    - Quarterly informal feedback sessions
    - New employee reviews at 30, 60, and 90 days
    
    Performance ratings scale:
    5 - Exceptional: Consistently exceeds all expectations
    4 - Exceeds Expectations: Often surpasses goals
    3 - Meets Expectations: Achieves all core requirements
    2 - Needs Improvement: Requires development in key areas
    1 - Unsatisfactory: Fails to meet minimum requirements
    
    3.2 PERFORMANCE IMPROVEMENT PLANS (PIP)
    Employees receiving a rating below "Meets Expectations" may be placed on a Performance Improvement Plan. The PIP process includes:
    - Written documentation of performance gaps
    - Specific, measurable improvement goals
    - Timeline for improvement (typically 30-90 days)
    - Regular check-ins with manager and HR
    - Final review with Dan Pfeiffer for decisions on continued employment
    
    SECTION 4: EMPLOYEE BENEFITS
    
    4.1 HEALTH AND WELLNESS
    Comprehensive benefits package includes:
    - Medical insurance (company pays 80% of premium)
    - Dental insurance (company pays 70% of premium)
    - Vision insurance (company pays 60% of premium)
    - Life insurance (2x annual salary, company paid)
    - Short and long-term disability insurance
    - Employee Assistance Program (EAP)
    - Wellness reimbursement up to $500 annually
    
    4.2 RETIREMENT PLANNING
    401(k) retirement plan with company matching:
    - Immediate eligibility upon hire
    - Company matches 100% of first 3% contributed
    - Company matches 50% of next 2% contributed
    - Vesting schedule: 20% per year, fully vested after 5 years
    
    For questions about any policies in this handbook, please contact Dan Pfeiffer at dan.pfeiffer@company.com or the HR department at hr@company.com.
    
    This handbook supersedes all previous versions and may be updated at the discretion of company leadership.
    """
    
    # Metadata for the document
    metadata = {
        "document_type": "HR Policy",
        "version": "2024.1",
        "author": "Human Resources Department",
        "approver": "Dan Pfeiffer",
        "effective_date": "2024-01-01"
    }
    
    # Prepare the request
    request_data = {
        "documents": [large_document],
        "metadata": [metadata]
    }
    
    print("=" * 60)
    print("Testing Large Document Ingestion with Chunking")
    print("=" * 60)
    print(f"\nDocument size: {len(large_document)} characters")
    print(f"Expected chunks: ~6-8 (based on 800 char chunk size)")
    
    try:
        # Send ingestion request
        print("\nSending document to ingestion endpoint...")
        response = requests.post(
            f"{BASE_URL}/api/ingest",
            json=request_data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            result = response.json()
            print("\n✅ Ingestion successful!")
            print(f"   Documents: {result['document_count']}")
            print(f"   Chunks created: {result['chunk_count']}")
            print(f"   Message: {result['message']}")
            print(f"   Document IDs: {len(result['doc_ids'])} created")
            
            # Test search to verify chunking worked
            print("\n\nTesting search for 'Dan Pfeiffer' across chunks...")
            search_query = {
                "message": "Who is Dan Pfeiffer and what are his responsibilities?",
                "session_id": "test_chunking"
            }
            
            search_response = requests.post(
                f"{BASE_URL}/api/chat",
                json=search_query,
                headers={"Content-Type": "application/json"}
            )
            
            if search_response.status_code == 200:
                search_result = search_response.json()
                print("\n✅ Search successful!")
                print(f"\nAI Response:\n{search_result.get('content', 'No content field')}")
                
                # Note: The /chat endpoint doesn't return context_info,
                # but we can see from the logs that it found 2 similar documents
            else:
                print(f"\n❌ Search failed: {search_response.status_code}")
                print(search_response.text)
                
        else:
            print(f"\n❌ Ingestion failed with status code: {response.status_code}")
            print(f"Error: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("\n❌ Error: Could not connect to the backend server.")
        print("Please ensure the FastAPI server is running on http://localhost:8000")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
    
    print("\n" + "=" * 60)

if __name__ == "__main__":
    test_large_document_ingestion()
