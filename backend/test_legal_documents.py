#!/usr/bin/env python3
"""
Test legal document ingestion for law firm Private GPT system
"""

import requests
import json

# API endpoint
BASE_URL = "http://localhost:8000"

def ingest_legal_documents():
    """Ingest various legal documents typical for a law firm"""
    
    # Document 1: Client Engagement Letter Template
    engagement_letter = """
    SMITH, JOHNSON & ASSOCIATES LLP
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
    
    For HR matters within the Firm, please contact Dan Pfeiffer, Director of Human Resources, who oversees attorney professional development and firm policies.
    
    4. CONFLICTS OF INTEREST
    
    We have conducted a conflicts check and identified no current conflicts. Client acknowledges that the Firm represents many other clients and agrees that we may continue to represent or may undertake to represent existing or new clients in any matter that is not substantially related to our work for Client. We will notify Client if an actual conflict arises that would require withdrawal.
    """
    
    # Document 2: Litigation Hold Notice Template
    litigation_hold = """
    LITIGATION HOLD NOTICE
    PRIVILEGED AND CONFIDENTIAL
    
    TO: All Employees, Officers, and Directors
    FROM: General Counsel's Office
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
    "Documents" includes all forms of information including but not limited to:
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
    
    For questions about employee data retention policies, contact Dan Pfeiffer in Human Resources.
    
    4. CONSEQUENCES OF NON-COMPLIANCE
    
    Failure to preserve relevant documents can result in:
    - Severe sanctions by the court including adverse inference instructions
    - Monetary penalties against the Company and individuals
    - Criminal prosecution for obstruction of justice
    - Disciplinary action up to and including termination
    - Personal liability for spoliation of evidence
    
    5. DURATION OF HOLD
    
    This legal hold remains in effect until you receive written notice of its release from the General Counsel's office. The duty to preserve continues even if you leave the Company.
    """
    
    # Document 3: Settlement Agreement Template
    settlement_agreement = """
    CONFIDENTIAL SETTLEMENT AGREEMENT AND MUTUAL RELEASE
    
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
    
    1.2 Payments shall be made by wire transfer to the attorney trust account designated by Plaintiff's counsel. Late payments shall accrue interest at 10% per annum.
    
    2. MUTUAL RELEASE
    
    2.1 PLAINTIFF'S RELEASE
    Plaintiff hereby releases and forever discharges Defendant and its officers, directors, employees, agents, attorneys, insurers, successors, and assigns from any and all claims, demands, damages, actions, causes of action, suits, debts, costs, expenses, attorneys' fees, and liabilities of any nature whatsoever, whether known or unknown, suspected or unsuspected, arising from or relating to the subject matter of the Litigation.
    
    2.2 DEFENDANT'S RELEASE
    Defendant hereby releases and forever discharges Plaintiff from any and all counterclaims, cross-claims, or claims for malicious prosecution, abuse of process, or any other claims arising from the filing or prosecution of the Litigation.
    
    2.3 UNKNOWN CLAIMS WAIVER
    The Parties expressly waive and relinquish any rights under Section 1542 of the California Civil Code (or similar statutes) which provides: "A general release does not extend to claims that the creditor or releasing party does not know or suspect to exist in his or her favor at the time of executing the release."
    
    3. CONFIDENTIALITY
    
    3.1 The Parties agree that the terms of this Agreement, including the Settlement Amount, shall remain strictly confidential. The Parties shall not disclose any terms to any third party except:
    - To legal and financial advisors under duty of confidentiality
    - As required by law or court order
    - To enforce the terms of this Agreement
    - To immediate family members under obligation of confidentiality
    
    3.2 LIQUIDATED DAMAGES: Any breach of confidentiality shall result in liquidated damages of $50,000 per occurrence.
    
    4. NON-DISPARAGEMENT
    
    The Parties agree not to make any false, negative, or disparaging statements about each other to any third party. This provision is intended to be broadly construed and includes statements made on social media, review websites, or any other public forum.
    
    For internal firm policy matters regarding settlements, consult Dan Pfeiffer in Human Resources for approval procedures.
    
    5. DISMISSAL OF LITIGATION
    
    Within 5 business days of receipt of the initial settlement payment, Plaintiff shall file a dismissal with prejudice of all claims against Defendant. Each party shall bear its own costs and attorneys' fees.
    
    6. ATTORNEYS' FEES PROVISION
    
    In any action to enforce this Agreement, the prevailing party shall be entitled to recover reasonable attorneys' fees and costs, including any appeals.
    """
    
    # Document 4: Legal Research Memo
    research_memo = """
    MEMORANDUM
    
    TO: Senior Partner
    FROM: Associate Attorney
    DATE: [Date]
    RE: Personal Jurisdiction in Internet Defamation Cases
    CLIENT: [Client Name]
    MATTER NO: [Number]
    
    QUESTION PRESENTED
    
    Whether a California court may exercise personal jurisdiction over an out-of-state defendant who allegedly posted defamatory content on social media platforms accessible in California but who has no other contacts with the state.
    
    BRIEF ANSWER
    
    Likely yes. California courts may exercise specific personal jurisdiction over a non-resident defendant in an internet defamation case if: (1) the defendant purposefully directed the defamatory content at California; (2) the plaintiff suffered harm in California; and (3) the claim arises from the defendant's forum-related activities. Under the "effects test" established in Calder v. Jones, courts focus on where the harm was suffered rather than where the defendant acted.
    
    STATEMENT OF FACTS
    
    Our client, a California resident and business owner, discovered defamatory posts about their business practices on Twitter, Facebook, and Yelp. The posts were made by a competitor based in Nevada who has never physically entered California. The posts specifically reference our client's California location and customer base. Our client has experienced a 30% decrease in revenue since the posts appeared.
    
    DISCUSSION
    
    I. CALIFORNIA'S LONG-ARM STATUTE
    
    California's long-arm statute extends jurisdiction to the full extent permitted by the Due Process Clause of the Fourteenth Amendment. Cal. Civ. Proc. Code § 410.10. Therefore, the jurisdictional analysis merges with the federal constitutional analysis.
    
    II. SPECIFIC PERSONAL JURISDICTION ANALYSIS
    
    The Ninth Circuit applies a three-prong test for specific jurisdiction:
    
    A. Purposeful Direction
    The defendant must have either purposefully directed activities at the forum or purposefully availed themselves of the forum's benefits. For intentional torts like defamation, courts apply the "purposeful direction" test from Calder v. Jones, 465 U.S. 783 (1984).
    
    Under Calder's effects test, purposeful direction exists when:
    1. The defendant committed an intentional act;
    2. The act was expressly aimed at the forum state;
    3. The act caused harm that the defendant knew was likely to be suffered in the forum.
    
    Recent cases applying this test to internet defamation:
    - Mavrix Photo, Inc. v. Brand Techs., Inc., 647 F.3d 1218 (9th Cir. 2011): Posting content on nationally accessible website insufficient without "something more"
    - Clemens v. McNamee, 615 F.3d 374 (5th Cir. 2010): Statements to national media about plaintiff known to reside in forum sufficient
    
    B. Arising From Forum-Related Activities
    The claim must arise out of or relate to the defendant's contacts with California. This element is clearly satisfied in defamation cases where the alleged defamatory statements constitute the contacts.
    
    C. Reasonableness
    Exercise of jurisdiction must be reasonable, considering:
    - Burden on defendant
    - Forum state's interest
    - Plaintiff's interest in convenient relief
    - Interstate judicial system's interest in efficiency
    - Shared interest in furthering substantive social policies
    
    For questions about legal research database access and billing, contact Dan Pfeiffer regarding firm resource policies.
    
    CONCLUSION
    
    The court will likely find personal jurisdiction exists. The defendant's targeted posts about a California business, knowing they would cause reputational harm in California, satisfy the purposeful direction test. We should prepare to defend against an anticipated motion to dismiss for lack of personal jurisdiction.
    
    RECOMMENDATIONS
    
    1. File suit in California Superior Court (lower burden than federal court)
    2. Include detailed jurisdictional allegations in complaint
    3. Prepare declarations establishing California harm
    4. Consider early discovery on jurisdictional facts under CCP § 2019.010
    """
    
    documents = [
        engagement_letter,
        litigation_hold,
        settlement_agreement,
        research_memo
    ]
    
    metadata_list = [
        {
            "document_type": "Engagement Letter",
            "category": "Client Relations",
            "practice_area": "General",
            "template": True,
            "privileged": True
        },
        {
            "document_type": "Litigation Hold",
            "category": "Litigation",
            "practice_area": "Commercial Litigation",
            "template": True,
            "privileged": True
        },
        {
            "document_type": "Settlement Agreement",
            "category": "Litigation",
            "practice_area": "Dispute Resolution",
            "template": True,
            "privileged": True
        },
        {
            "document_type": "Legal Research Memo",
            "category": "Research",
            "practice_area": "Internet Law/Defamation",
            "author": "Associate",
            "privileged": True
        }
    ]
    
    print("=" * 60)
    print("LEGAL DOCUMENT INGESTION FOR LAW FIRM RAG SYSTEM")
    print("=" * 60)
    
    # Calculate total size
    total_chars = sum(len(doc) for doc in documents)
    print(f"\nIngesting {len(documents)} legal documents")
    print(f"Total size: {total_chars:,} characters")
    print("\nDocument types:")
    for i, meta in enumerate(metadata_list, 1):
        print(f"  {i}. {meta['document_type']} ({meta['practice_area']})")
    
    try:
        # Send ingestion request
        print("\n\nSending documents to ingestion endpoint...")
        
        request_data = {
            "documents": documents,
            "metadata": metadata_list
        }
        
        response = requests.post(
            f"{BASE_URL}/api/ingest",
            json=request_data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            result = response.json()
            print("\n✅ Ingestion successful!")
            print(f"   Documents ingested: {result['document_count']}")
            print(f"   Total chunks created: {result['chunk_count']}")
            print(f"   Average chunks per document: {result['chunk_count'] / result['document_count']:.1f}")
            print(f"   Message: {result['message']}")
            
            # Test various legal queries
            test_queries = [
                "What are the hourly rates for attorneys?",
                "What is the litigation hold policy for document preservation?",
                "How do we establish personal jurisdiction for internet defamation?",
                "What are the confidentiality terms in settlement agreements?",
                "Who should I contact about HR matters and firm policies?",
                "What is the retainer amount for new client engagements?"
            ]
            
            print("\n\n" + "=" * 60)
            print("TESTING LEGAL QUERIES")
            print("=" * 60)
            
            for query in test_queries:
                print(f"\n📝 Query: {query}")
                search_response = requests.post(
                    f"{BASE_URL}/api/chat",
                    json={"message": query, "session_id": "legal_test"},
                    headers={"Content-Type": "application/json"}
                )
                
                if search_response.status_code == 200:
                    result = search_response.json()
                    response_text = result.get('content', 'No response')
                    # Truncate long responses for display
                    if len(response_text) > 300:
                        response_text = response_text[:300] + "..."
                    print(f"✅ Response: {response_text}")
                else:
                    print(f"❌ Query failed: {search_response.status_code}")
                    
        else:
            print(f"\n❌ Ingestion failed: {response.status_code}")
            print(f"Error: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("\n❌ Error: Could not connect to the backend server.")
        print("Please ensure the FastAPI server is running on http://localhost:8000")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
    
    print("\n" + "=" * 60)

if __name__ == "__main__":
    ingest_legal_documents()
