#!/bin/bash

# AWS EC2 Document Ingestion Script
# Purpose: Ingest the same documents as on MacBook to ensure identical knowledge base
# Author: Scott Steele System
# Date: December 2024

set -e

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Get EC2 IP
if [ -z "$1" ]; then
    echo -e "${YELLOW}Please enter your EC2 instance public IP address:${NC}"
    read -r EC2_IP
else
    EC2_IP=$1
fi

API_URL="https://$EC2_IP/api"

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}Document Ingestion for AWS EC2${NC}"
echo -e "${BLUE}========================================${NC}"

# Test API connectivity
echo -e "${YELLOW}Testing API connectivity...${NC}"
if curl -k -s "${API_URL}/health" > /dev/null 2>&1; then
    echo -e "${GREEN}✓ API is reachable${NC}"
else
    echo -e "${RED}✗ Cannot reach API at ${API_URL}/health${NC}"
    echo -e "${YELLOW}Make sure the EC2 instance is running and accessible${NC}"
    exit 1
fi

# Function to ingest a document
ingest_document() {
    local title=$1
    local content=$2
    local metadata=$3
    
    echo -e "${YELLOW}Ingesting: $title${NC}"
    
    response=$(curl -k -s -X POST "${API_URL}/ingest" \
        -H "Content-Type: application/json" \
        -d "{
            \"documents\": [\"$content\"],
            \"metadata\": [$metadata]
        }")
    
    if echo "$response" | grep -q "\"success\":true"; then
        echo -e "${GREEN}✓ Successfully ingested: $title${NC}"
    else
        echo -e "${RED}✗ Failed to ingest: $title${NC}"
        echo "Response: $response"
    fi
}

# Document 1: Client Engagement Letter
echo -e "${BLUE}Ingesting Client Engagement Letter Template...${NC}"
engagement_letter='SMITH, JOHNSON & ASSOCIATES LLP
ATTORNEY-CLIENT ENGAGEMENT AGREEMENT

Effective Date: [Date]
Matter Number: [Matter No.]

1. SCOPE OF REPRESENTATION

This engagement letter confirms that Smith, Johnson & Associates LLP ("Firm") has been retained to represent [Client Name] ("Client") in connection with [Matter Description]. The scope of our representation includes:

- Legal research and analysis of applicable federal and state laws
- Drafting and review of legal documents including contracts, pleadings, and motions
- Court appearances and oral arguments as necessary
- Settlement negotiations and mediation proceedings
- Communication with opposing counsel and third parties
- Strategic legal advice and counsel throughout the matter

This representation does not include tax advice unless specifically agreed in writing. Any expansion of scope requires written approval from the Managing Partner and may result in adjusted fee arrangements.

2. BILLING AND PAYMENT TERMS

2.1 HOURLY RATES
Our current hourly rates for this matter are:
- Senior Partners: $750 per hour
- Junior Partners: $550 per hour  
- Senior Associates: $450 per hour
- Junior Associates: $350 per hour
- Paralegals: $175 per hour
- Law Clerks: $125 per hour

These rates are subject to annual adjustment. Time is billed in minimum increments of 0.1 hour (6 minutes).

2.2 RETAINER AND TRUST ACCOUNT
Client agrees to pay an initial retainer of $25,000 upon execution of this agreement. The retainer will be deposited into our client trust account and applied against fees and costs as they are incurred. When the retainer balance falls below $5,000, Client agrees to replenish it to the original amount within 10 business days of notice.

2.3 COSTS AND EXPENSES
Client is responsible for all costs and expenses including but not limited to:
- Court filing fees and service of process fees
- Expert witness and consultant fees
- Deposition and court reporter costs
- Travel expenses (billed at IRS standard rates)
- Document production and e-discovery costs
- Research database charges (Westlaw/Lexis)

3. CLIENT RESPONSIBILITIES

Client agrees to:
- Provide complete and accurate information relevant to the matter
- Respond promptly to requests for information and documents
- Make timely decisions regarding settlement and litigation strategy
- Notify the Firm immediately of any changes in contact information
- Pay all invoices within 30 days of receipt
- Maintain confidentiality of attorney-client privileged communications

4. CONFLICTS OF INTEREST

We have conducted a conflicts check and identified no current conflicts. Client acknowledges that the Firm represents many other clients and agrees that we may continue to represent or may undertake to represent existing or new clients in any matter that is not substantially related to our work for Client.'

ingest_document "Client Engagement Letter Template" "$engagement_letter" '{"type": "template", "category": "engagement", "source": "firm_templates"}'

# Document 2: Litigation Hold Notice
echo -e "${BLUE}Ingesting Litigation Hold Notice Template...${NC}"
litigation_hold='LITIGATION HOLD NOTICE
PRIVILEGED AND CONFIDENTIAL

TO: All Employees, Officers, and Directors
FROM: General Counsel Office
DATE: [Date]
RE: Legal Hold - [Matter Name]

IMPORTANT: MANDATORY DOCUMENT PRESERVATION NOTICE

1. PRESERVATION OBLIGATION

The Company is involved in pending/anticipated litigation regarding [Matter Description]. You are receiving this notice because you may have documents or electronically stored information (ESI) relevant to this matter.

EFFECTIVE IMMEDIATELY, you must preserve ALL documents and data relating to:
- [Specific Topic 1]
- [Specific Topic 2]
- [Specific Topic 3]
- Communications with [Relevant Parties]
- Any documents dated between [Start Date] and [End Date]

2. SCOPE OF PRESERVATION

2.1 DOCUMENTS TO PRESERVE
Documents includes all forms of information including but not limited to:
- Emails (including drafts, sent items, and deleted items)
- Text messages, instant messages, and chat logs
- Voice mails and recorded calls
- Calendar entries and meeting invitations
- Word documents, Excel spreadsheets, PowerPoint presentations
- PDFs and scanned documents
- Photographs and videos
- Social media posts and messages
- Handwritten notes and physical files
- Database records and system logs

2.2 LOCATIONS TO CHECK
Relevant documents may be stored in:
- Company email servers and archives
- Personal devices used for business (BYOD)
- Cloud storage (OneDrive, SharePoint, Dropbox)
- Network drives and shared folders
- Local hard drives and USB devices
- Home offices and remote work locations
- Physical filing cabinets and storage boxes

3. SUSPENSION OF ROUTINE DESTRUCTION

You must immediately suspend any routine document destruction policies including:
- Auto-delete functions in email systems
- Scheduled purging of archived data
- Shredding of physical documents
- Overwriting of backup tapes
- Clearing of temporary files and caches

4. CONSEQUENCES OF NON-COMPLIANCE

Failure to preserve relevant documents can result in:
- Severe sanctions by the court including adverse inference instructions
- Monetary penalties against the Company and individuals
- Criminal prosecution for obstruction of justice
- Disciplinary action up to and including termination
- Personal liability for spoliation of evidence

5. DURATION OF HOLD

This legal hold remains in effect until you receive written notice of its release from the General Counsel office. The duty to preserve continues even if you leave the Company.'

ingest_document "Litigation Hold Notice Template" "$litigation_hold" '{"type": "template", "category": "litigation", "source": "firm_templates"}'

# Document 3: Settlement Agreement Template
echo -e "${BLUE}Ingesting Settlement Agreement Template...${NC}"
settlement_agreement='CONFIDENTIAL SETTLEMENT AGREEMENT AND MUTUAL RELEASE

This Settlement Agreement ("Agreement") is entered into as of [Date] by and between [Party A] ("Plaintiff") and [Party B] ("Defendant") (collectively, the "Parties").

RECITALS

WHEREAS, Plaintiff filed a lawsuit against Defendant in [Court Name], Case No. [Case Number], alleging [Claims Description] (the "Litigation");

WHEREAS, Defendant denies all allegations and liability but desires to avoid the expense, inconvenience, and uncertainty of continued litigation;

WHEREAS, the Parties wish to resolve all claims and disputes between them;

NOW, THEREFORE, in consideration of the mutual covenants and agreements contained herein, and for other good and valuable consideration, the receipt and sufficiency of which are hereby acknowledged, the Parties agree as follows:

1. SETTLEMENT PAYMENT

1.1 Defendant agrees to pay Plaintiff the total sum of $[Amount] ("Settlement Amount") as follows:
- Initial payment of $[Amount] within 30 days of execution
- [Number] monthly installments of $[Amount] beginning [Date]
- Final payment of $[Amount] on or before [Date]

1.2 Payments shall be made by wire transfer to the attorney trust account designated by Plaintiff counsel. Late payments shall accrue interest at 10% per annum.

2. MUTUAL RELEASE

2.1 PLAINTIFF RELEASE
Plaintiff hereby releases and forever discharges Defendant and its officers, directors, employees, agents, attorneys, insurers, successors, and assigns from any and all claims, demands, damages, actions, causes of action, suits, debts, costs, expenses, attorneys fees, and liabilities of any nature whatsoever, whether known or unknown, suspected or unsuspected, arising from or relating to the subject matter of the Litigation.

2.2 DEFENDANT RELEASE
Defendant hereby releases and forever discharges Plaintiff from any and all counterclaims, cross-claims, or claims for malicious prosecution, abuse of process, or any other claims arising from the filing or prosecution of the Litigation.

2.3 UNKNOWN CLAIMS WAIVER
The Parties expressly waive and relinquish any rights under Section 1542 of the California Civil Code (or similar statutes) which provides: A general release does not extend to claims that the creditor or releasing party does not know or suspect to exist in his or her favor at the time of executing the release.

3. CONFIDENTIALITY

3.1 The Parties agree that the terms of this Agreement, including the Settlement Amount, shall remain strictly confidential. The Parties shall not disclose any terms to any third party except:
- To legal and financial advisors under duty of confidentiality
- As required by law or court order
- To enforce the terms of this Agreement
- To immediate family members under obligation of confidentiality

3.2 LIQUIDATED DAMAGES: Any breach of confidentiality shall result in liquidated damages of $50,000 per occurrence.

4. NON-DISPARAGEMENT

The Parties agree not to make any false, negative, or disparaging statements about each other to any third party. This provision is intended to be broadly construed and includes statements made on social media, review websites, or any other public forum.'

ingest_document "Settlement Agreement Template" "$settlement_agreement" '{"type": "template", "category": "settlement", "source": "firm_templates"}'

# Document 4: Firm HR Policies
echo -e "${BLUE}Ingesting Firm HR Policies...${NC}"
hr_policies='SMITH, JOHNSON & ASSOCIATES LLP
EMPLOYEE HANDBOOK AND POLICIES

SECTION 1: WORK ARRANGEMENTS

1.1 STANDARD WORK HOURS
Standard office hours are Monday through Friday, 9:00 AM to 6:00 PM. Partners and senior associates may have flexibility based on client needs and court schedules.

1.2 REMOTE WORK POLICY
Remote work arrangements may be approved on a case-by-case basis. Requests must be submitted to your supervising partner and approved by the Director of Human Resources. Employees working remotely must:
- Maintain regular business hours
- Be available for video conferences
- Have secure internet connection
- Protect client confidentiality

Contact: hr@smithlaw.com or extension 2000

1.3 TIME OFF AND LEAVE POLICIES

Vacation Time:
- Associates: 15 days per year
- Senior Associates: 20 days per year
- Partners: Discretionary
- Support Staff: 10-15 days based on tenure

Sick Leave:
- All employees: 10 days per year
- Unused sick leave does not carry over

Personal Days:
- All employees: 3 personal days per year
- Must be approved 48 hours in advance

SECTION 2: PROFESSIONAL DEVELOPMENT

2.1 CONTINUING LEGAL EDUCATION (CLE)
The Firm covers all mandatory CLE requirements. Additional CLE courses may be approved if relevant to practice area. Submit requests to the Professional Development Committee.

2.2 BAR ADMISSIONS
The Firm will cover bar examination fees and reasonable preparation costs for attorneys seeking admission in jurisdictions where the Firm practices.

2.3 MENTORSHIP PROGRAM
All junior associates are assigned a mentor partner. Mentorship meetings should occur monthly at minimum.

SECTION 3: BILLING AND TIMEKEEPING

3.1 BILLABLE HOUR REQUIREMENTS
- Junior Associates: 1,800 billable hours annually
- Senior Associates: 2,000 billable hours annually
- Of Counsel: As agreed in employment contract
- Partners: No minimum requirement

3.2 TIME ENTRY REQUIREMENTS
- All time must be entered daily
- Entries must be detailed and descriptive
- Time is recorded in 6-minute increments (0.1 hour)
- Non-billable administrative time must also be tracked

SECTION 4: ETHICS AND COMPLIANCE

4.1 CONFIDENTIALITY
All employees must maintain strict confidentiality regarding client matters, firm finances, and internal operations. Violations may result in immediate termination and legal action.

4.2 CONFLICTS OF INTEREST
Employees must disclose any potential conflicts of interest immediately. Run all new matters through the conflicts checking system before engagement.

4.3 MANDATORY REPORTING
Any suspected ethical violations, discrimination, or harassment must be reported immediately to Human Resources or the Managing Partner.

For all HR-related questions or concerns, please contact:
Human Resources Department
hr@smithlaw.com
Extension: 2000
Office: Suite 500'

ingest_document "Firm HR Policies" "$hr_policies" '{"type": "policy", "category": "hr", "source": "internal_policies"}'

# Document 5: Legal Research Procedures
echo -e "${BLUE}Ingesting Legal Research Procedures...${NC}"
research_procedures='LEGAL RESEARCH PROCEDURES AND BEST PRACTICES

1. RESEARCH METHODOLOGY

1.1 PRIMARY SOURCES
Always begin with primary sources:
- Constitutions (federal and state)
- Statutes and codes
- Regulations and administrative rules
- Case law from relevant jurisdictions
- Court rules and local rules

1.2 SECONDARY SOURCES
Use secondary sources for context and analysis:
- Legal treatises and practice guides
- Law review articles
- ALR annotations
- Restatements
- Legal encyclopedias (AmJur, CJS)

1.3 RESEARCH DATABASES
The Firm maintains subscriptions to:
- Westlaw (primary platform)
- Lexis Advance
- Bloomberg Law (securities matters)
- PACER (federal court filings)

2. RESEARCH WORKFLOW

2.1 INITIAL ASSESSMENT
- Define the legal issue precisely
- Identify relevant jurisdiction(s)
- Determine applicable time period
- Note any special procedural requirements

2.2 RESEARCH PLAN
- Create a research plan before beginning
- Set time limits for each research task
- Document search terms and databases used
- Keep detailed notes of findings

2.3 VERIFICATION
- Shepardize or KeyCite all cases
- Verify current status of statutes
- Check for recent amendments or updates
- Confirm local rule compliance

3. MEMORANDUM FORMAT

3.1 STRUCTURE
All research memoranda should include:
- Question Presented
- Brief Answer
- Statement of Facts
- Discussion/Analysis
- Conclusion
- Citations in Bluebook format

3.2 CITATION REQUIREMENTS
- Use Bluebook citation format (current edition)
- Include pinpoint citations
- Provide parallel citations where required
- Hyperlink to cases in electronic documents

4. QUALITY CONTROL

4.1 PEER REVIEW
Research memoranda over 10 pages must be peer-reviewed before submission to partners.

4.2 SUPERVISING ATTORNEY APPROVAL
All research must be approved by the supervising attorney before being incorporated into client work product.

4.3 TIME TRACKING
Research time must be tracked with specificity:
- Note databases searched
- Record specific issues researched
- Distinguish between billable and non-billable research

For research support, contact the Law Library:
library@smithlaw.com
Extension: 2100'

ingest_document "Legal Research Procedures" "$research_procedures" '{"type": "procedure", "category": "research", "source": "internal_procedures"}'

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Document Ingestion Complete!${NC}"
echo -e "${GREEN}========================================${NC}"

# Test the knowledge base
echo -e "${BLUE}Testing knowledge base...${NC}"

test_query() {
    local query=$1
    echo -e "${YELLOW}Testing query: $query${NC}"
    
    response=$(curl -k -s -X POST "${API_URL}/chat/" \
        -H "Content-Type: application/json" \
        -d "{\"message\": \"$query\"}")
    
    if echo "$response" | grep -q "response"; then
        echo -e "${GREEN}✓ Query successful${NC}"
        echo "$response" | python3 -m json.tool | head -20
    else
        echo -e "${RED}✗ Query failed${NC}"
    fi
}

echo ""
test_query "What are the billing rates for attorneys?"
echo ""
test_query "What is the retainer amount for new clients?"
echo ""
test_query "Who should I contact for HR matters?"

echo -e "${BLUE}========================================${NC}"
echo -e "${GREEN}Your AWS deployment now has the same knowledge base as your MacBook!${NC}"
echo -e "${BLUE}========================================${NC}"
