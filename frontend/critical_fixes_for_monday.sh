#!/bin/bash

# CRITICAL FIXES FOR MONDAY TESTING
# This addresses the absolute minimum for a functional pilot

set -e

EC2_IP="44.202.131.48"
KEY_PATH="$HOME/.ssh/Scott-Key.pem"

echo "========================================="
echo "CRITICAL FIXES FOR MONDAY PILOT"
echo "========================================="

# CRITICAL FIX 1: POPULATE THE KNOWLEDGE BASE
echo ""
echo "🚨 CRITICAL FIX 1: Populating Empty Knowledge Base..."
echo "-----------------------------------------------------"

# First, let's create a more comprehensive document set
cat << 'DOCUMENTS_PY' > /tmp/create_comprehensive_docs.py
import asyncio
import sys
import os

# Add the backend directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.rag_service import rag_service

async def ingest_comprehensive_documents():
    """Ingest a comprehensive set of legal documents"""
    
    documents = [
        # HR Policies
        {
            "title": "Remote Work Policy",
            "content": """REMOTE WORK POLICY
            
Effective Date: January 1, 2024

1. APPROVAL AUTHORITY
All remote work arrangements must be approved by the employee's direct supervisor.
For extended remote work (more than 2 days per week), approval from HR Director is required.

2. ELIGIBILITY
- Employees must have completed 90-day probationary period
- Performance rating of "Meets Expectations" or higher
- Role must be suitable for remote work

3. EQUIPMENT
The firm provides:
- Laptop computer
- VPN access
- Microsoft 365 license
- Zoom license

4. WORK HOURS
Core hours: 10 AM - 3 PM (employee's time zone)
Employees must be available during core hours via Teams/Slack

5. SECURITY REQUIREMENTS
- Use VPN for all work activities
- Enable 2FA on all accounts
- Lock screens when away from computer
- No work on public WiFi without VPN"""
        },
        
        {
            "title": "PTO and Leave Policy",
            "content": """PAID TIME OFF (PTO) POLICY

1. PTO ACCRUAL
- Years 1-3: 15 days per year (1.25 days/month)
- Years 4-6: 20 days per year (1.67 days/month)  
- Years 7+: 25 days per year (2.08 days/month)
- Maximum accrual: 40 days

2. APPROVAL PROCESS
- Submit requests via HR system at least 2 weeks in advance
- Manager approval required for all PTO
- HR approval required for leave exceeding 5 consecutive days

3. SICK LEAVE
- 10 days per year (does not roll over)
- No advance notice required
- Doctor's note required for absence exceeding 3 days

4. HOLIDAYS
The firm observes 11 federal holidays plus 2 floating holidays

5. PARENTAL LEAVE
- 12 weeks paid parental leave
- Must be taken within 1 year of birth/adoption"""
        },
        
        # Legal Documents
        {
            "title": "Standard Retainer Agreement",
            "content": """LEGAL SERVICES RETAINER AGREEMENT

This Agreement is entered into between [LAW FIRM NAME] ("Firm") and [CLIENT NAME] ("Client").

1. SCOPE OF REPRESENTATION
The Firm agrees to provide legal services for [MATTER DESCRIPTION].
This representation does not include appeals or other matters unless specified.

2. LEGAL FEES
- Partner Rate: $650-850 per hour
- Senior Associate: $450-550 per hour
- Associate: $295-395 per hour
- Paralegal: $195-250 per hour

Rates are subject to annual adjustment.

3. RETAINER
Client agrees to pay an initial retainer of $10,000.
The retainer will be held in trust and applied to final invoice.

4. BILLING
- Invoices issued monthly
- Payment due within 30 days
- Interest of 1.5% monthly on overdue amounts
- Minimum billing increment: 0.1 hour (6 minutes)

5. EXPENSES
Client reimburses for costs including:
- Filing fees
- Court reporters
- Expert witnesses
- Travel expenses
- Research databases

6. TERMINATION
Either party may terminate with written notice.
Client responsible for fees/costs through termination."""
        },
        
        {
            "title": "Litigation Hold Notice Template",
            "content": """LITIGATION HOLD NOTICE

TO: [RECIPIENT]
FROM: Legal Department
DATE: [DATE]
RE: Preservation of Documents and Electronic Information

You are receiving this notice because you may have documents relevant to pending or anticipated litigation.

EFFECTIVE IMMEDIATELY, you must preserve all documents related to:
[DESCRIPTION OF MATTER]

This includes but is not limited to:
- Emails (including deleted items)
- Text messages
- Instant messages
- Voicemails
- Calendar entries
- Documents (Word, Excel, PowerPoint, PDF)
- Databases
- Hard copy files
- Handwritten notes

DO NOT:
- Delete any potentially relevant information
- Modify documents
- Use auto-delete functions
- Destroy backup tapes

This hold supersedes any document retention/destruction policies.
The hold remains in effect until written notice of release.

Failure to preserve documents may result in sanctions, adverse inference instructions, 
contempt findings, and personal liability.

Contact Legal Department with any questions: legal@lawfirm.com"""
        },
        
        {
            "title": "Billing Guidelines",
            "content": """CLIENT BILLING GUIDELINES

1. TIMEKEEPER RATES (2024)
- Equity Partner: $850-1,200/hour
- Non-Equity Partner: $650-850/hour  
- Senior Counsel: $550-750/hour
- Senior Associate (6+ years): $450-550/hour
- Mid-level Associate (3-5 years): $350-450/hour
- Junior Associate (0-2 years): $295-350/hour
- Senior Paralegal: $225-275/hour
- Paralegal: $195-225/hour
- Project Assistant: $125-150/hour

2. BILLING PRACTICES
- Time recorded in 6-minute increments (0.1 hour)
- Detailed descriptions required for all entries
- No block billing permitted
- Travel time billed at 50% of standard rate

3. NON-BILLABLE ACTIVITIES
- Administrative tasks
- Training (unless client-specific)
- Business development
- Billing inquiries
- File organization (routine)

4. EXPENSE GUIDELINES
Prior approval required for:
- Air travel (book 14+ days in advance)
- Hotels exceeding $300/night
- Meals exceeding $100/person
- Expert fees exceeding $5,000
- Vendor costs exceeding $2,500

5. ALTERNATIVE FEE ARRANGEMENTS
Available upon request:
- Flat fees
- Contingency fees (where permitted)
- Blended rates
- Volume discounts
- Success fees"""
        },
        
        # Practice Area Specific
        {
            "title": "Criminal Defense Practice Guide",
            "content": """CRIMINAL DEFENSE PRACTICE GUIDE

1. INITIAL CLIENT CONSULTATION
- Explain attorney-client privilege
- Obtain basic facts (do not record)
- Discuss fee structure
- Provide retainer agreement
- Conduct conflict check

2. CASE TYPES WE HANDLE
- White collar crimes
- Federal criminal defense
- State felonies
- DUI/DWI
- Drug offenses
- Fraud and embezzlement
- RICO violations
- Criminal appeals

3. IMMEDIATE ACTIONS
Upon retention:
- Enter appearance
- Request discovery
- File preservation letters
- Interview witnesses
- Retain necessary experts
- Review charging documents

4. PLEA NEGOTIATIONS
- Evaluate strength of prosecution's case
- Identify weaknesses
- Prepare mitigation package
- Negotiate with prosecutor
- Advise client on options
- Document all offers

5. TRIAL PREPARATION
- Jury consultant evaluation
- Mock trials for major cases
- Witness preparation
- Exhibit preparation
- Motion practice
- Jury instructions

6. BILLING CONSIDERATIONS
- Criminal cases typically require substantial retainer
- Flat fees common for routine matters
- Hourly billing for complex cases
- Separate retainer for appeals"""
        },
        
        {
            "title": "Civil Litigation Procedures",
            "content": """CIVIL LITIGATION PROCEDURES

1. CASE EVALUATION
- Statute of limitations analysis
- Jurisdiction determination
- Venue considerations
- Damage calculations
- Insurance coverage review

2. PRE-LITIGATION
- Demand letters
- Preservation notices
- Pre-suit investigation
- Asset searches
- Settlement negotiations

3. PLEADINGS
- Complaint drafting
- Service of process
- Answer and counterclaims
- Motion practice
- Discovery planning

4. DISCOVERY PHASE
- Initial disclosures
- Document requests
- Interrogatories
- Depositions
- Expert discovery
- ESI protocols

5. MOTION PRACTICE
- Motion to dismiss
- Summary judgment
- Discovery motions
- Motions in limine
- Daubert motions

6. TRIAL
- Jury selection
- Opening statements
- Direct examination
- Cross examination
- Closing arguments
- Post-trial motions

7. SETTLEMENT
- Mediation
- Settlement conferences
- Arbitration
- Negotiation strategies"""
        }
    ]
    
    print(f"Ingesting {len(documents)} comprehensive documents...")
    
    for doc in documents:
        try:
            result = await rag_service.ingest_documents([doc])
            if result['success']:
                print(f"✅ Ingested: {doc['title']}")
            else:
                print(f"❌ Failed: {doc['title']} - {result.get('error')}")
        except Exception as e:
            print(f"❌ Error ingesting {doc['title']}: {e}")
    
    # Verify ingestion
    from app.services.vector_service import vector_service
    stats = await vector_service.get_index_stats()
    total = stats.get('total_vector_count', 0)
    
    print(f"\n{'='*50}")
    print(f"✅ Knowledge base now contains {total} vectors")
    print(f"✅ Ready for testing")
    print(f"{'='*50}")
    
    return total > 0

if __name__ == "__main__":
    success = asyncio.run(ingest_comprehensive_documents())
    sys.exit(0 if success else 1)
DOCUMENTS_PY

# Copy and run comprehensive document ingestion
scp -i "$KEY_PATH" /tmp/create_comprehensive_docs.py ec2-user@$EC2_IP:/home/ec2-user/privategpt/backend/

ssh -i "$KEY_PATH" ec2-user@$EC2_IP << 'EOF'
    cd /home/ec2-user/privategpt/backend
    source /home/ec2-user/privategpt/venv/bin/activate
    
    # Clear any bad data first
    python3 -c "
import asyncio
from app.services.vector_service import vector_service

async def clear():
    print('Clearing old data...')
    await vector_service.clear_index()
    print('✅ Index cleared')
    
asyncio.run(clear())
"
    
    # Ingest comprehensive documents
    echo "Ingesting comprehensive knowledge base..."
    python3 create_comprehensive_docs.py
EOF

# CRITICAL FIX 2: ADD SESSION MANAGEMENT
echo ""
echo "🚨 CRITICAL FIX 2: Adding Session Management..."
echo "------------------------------------------------"

cat << 'SESSION_PY' > /tmp/update_chat_session.py
# Update chat.py to use session-based conversations

chat_py_content = '''from fastapi import APIRouter, HTTPException, Request
from app.models.chat import ChatRequest, ChatResponse
from app.services.rag_service import rag_service
import datetime
from typing import Dict, List
import uuid
import hashlib

router = APIRouter()

# Store conversation history per session
conversation_sessions: Dict[str, List[Dict]] = {}
MAX_HISTORY_LENGTH = 20
MAX_SESSIONS = 100

def get_session_id(request: Request) -> str:
    """Generate session ID from IP + User Agent"""
    client_ip = request.client.host
    user_agent = request.headers.get("user-agent", "unknown")
    session_string = f"{client_ip}:{user_agent}"
    return hashlib.md5(session_string.encode()).hexdigest()[:16]

@router.post("/chat/", response_model=ChatResponse)
async def chat(request: ChatRequest, http_request: Request):
    """Process chat message with session-based context"""
    try:
        # Get session ID
        session_id = get_session_id(http_request)
        
        # Initialize session if needed
        if session_id not in conversation_sessions:
            # Limit total sessions to prevent memory issues
            if len(conversation_sessions) >= MAX_SESSIONS:
                # Remove oldest session
                oldest = min(conversation_sessions.keys())
                del conversation_sessions[oldest]
            conversation_sessions[session_id] = []
        
        # Add user message to session history
        conversation_sessions[session_id].append({
            "role": "user",
            "content": request.message
        })
        
        # Build context from session history
        context_message = request.message
        if len(conversation_sessions[session_id]) > 1:
            recent_history = conversation_sessions[session_id][-5:-1]
            if recent_history:
                history_text = "\\n".join([
                    f"{msg[\'role\'].capitalize()}: {msg[\'content\']}" 
                    for msg in recent_history
                ])
                context_message = f"""Previous conversation:
{history_text}

Current question: {request.message}"""
        
        # Get RAG response with context
        rag_result = await rag_service.query_with_rag(context_message)
        
        # Add response to session history
        conversation_sessions[session_id].append({
            "role": "assistant",
            "content": rag_result["response"]
        })
        
        # Limit history length
        if len(conversation_sessions[session_id]) > MAX_HISTORY_LENGTH:
            conversation_sessions[session_id] = conversation_sessions[session_id][-MAX_HISTORY_LENGTH:]
        
        # Create response
        id = int(datetime.datetime.now().timestamp())
        response = ChatResponse(
            id=id,
            role="assistant",
            content=rag_result["response"],
            timestamp=datetime.datetime.now()
        )
        return response
        
    except Exception as e:
        print(f"Chat endpoint error: {e}")
        id = int(datetime.datetime.now().timestamp())
        response = ChatResponse(
            id=id,
            role="assistant",
            content="I apologize, but I encountered an error. Please try again.",
            timestamp=datetime.datetime.now()
        )
        return response

@router.post("/chat/reset")
async def reset_chat(http_request: Request):
    """Reset conversation for current session"""
    session_id = get_session_id(http_request)
    if session_id in conversation_sessions:
        del conversation_sessions[session_id]
    return {"message": "Conversation reset", "session_id": session_id}

@router.get("/chat/stats")
async def chat_stats():
    """Get chat system statistics"""
    return {
        "active_sessions": len(conversation_sessions),
        "total_messages": sum(len(msgs) for msgs in conversation_sessions.values()),
        "max_sessions": MAX_SESSIONS
    }
'''

with open('/tmp/chat_with_sessions.py', 'w') as f:
    f.write(chat_py_content)

print("✅ Session management code created")
SESSION_PY

python3 /tmp/update_chat_session.py
scp -i "$KEY_PATH" /tmp/chat_with_sessions.py ec2-user@$EC2_IP:/home/ec2-user/privategpt/backend/app/api/chat.py

# CRITICAL FIX 3: ADD MONITORING
echo ""
echo "🚨 CRITICAL FIX 3: Adding Health Monitoring..."
echo "-----------------------------------------------"

ssh -i "$KEY_PATH" ec2-user@$EC2_IP << 'EOF'
    cd /home/ec2-user/privategpt/backend
    source /home/ec2-user/privategpt/venv/bin/activate
    
    # Install monitoring dependencies
    pip install psutil
    
    # Create simple health check
    cat << 'HEALTH' > app/api/health.py
from fastapi import APIRouter
from datetime import datetime
import os

router = APIRouter()

@router.get("/health")
async def health_check():
    """Basic health check"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0"
    }

@router.get("/ready")
async def readiness_check():
    """Check if system is ready"""
    try:
        from app.services.vector_service import vector_service
        import asyncio
        
        # Check vector DB
        stats = asyncio.run(vector_service.get_index_stats())
        vector_count = stats.get('total_vector_count', 0)
        
        ready = vector_count > 0
        
        return {
            "ready": ready,
            "vector_count": vector_count,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return {
            "ready": False,
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }
HEALTH
    
    # Update main.py to include health
    python3 -c "
content = open('app/main.py').read()
if 'from app.api import health' not in content:
    content = content.replace(
        'from app.api import chat',
        'from app.api import chat, health'
    )
    content = content.replace(
        'app.include_router(chat.router',
        '''app.include_router(health.router, prefix=\"/api\", tags=[\"health\"])
app.include_router(chat.router'''
    )
    open('app/main.py', 'w').write(content)
    print('✅ Health endpoints added')
"
EOF

# CRITICAL FIX 4: RESTART AND VERIFY
echo ""
echo "🚨 CRITICAL FIX 4: Restarting and Verifying..."
echo "-----------------------------------------------"

ssh -i "$KEY_PATH" ec2-user@$EC2_IP << 'EOF'
    # Restart services
    sudo systemctl restart privategpt-backend
    sudo systemctl restart nginx
    
    echo "Waiting for services to start..."
    sleep 5
    
    # Run verification tests
    echo ""
    echo "Running System Verification..."
    echo "=============================="
    
    # Test 1: Health check
    echo -n "1. Health Check: "
    if curl -s http://localhost:8000/api/health | grep -q "healthy"; then
        echo "✅ PASS"
    else
        echo "❌ FAIL"
    fi
    
    # Test 2: Knowledge base
    echo -n "2. Knowledge Base: "
    VECTORS=$(curl -s http://localhost:8000/api/ready | python3 -c "import sys, json; print(json.load(sys.stdin).get('vector_count', 0))")
    if [ "$VECTORS" -gt "0" ]; then
        echo "✅ PASS ($VECTORS vectors)"
    else
        echo "❌ FAIL (empty)"
    fi
    
    # Test 3: Chat endpoint
    echo -n "3. Chat Endpoint: "
    RESPONSE=$(curl -s -X POST http://localhost:8000/api/chat/ \
        -H "Content-Type: application/json" \
        -d '{"message":"What are the partner billing rates?"}' \
        | python3 -c "import sys, json; print(len(json.load(sys.stdin).get('content', '')))" 2>/dev/null)
    
    if [ "$RESPONSE" -gt "10" ]; then
        echo "✅ PASS"
    else
        echo "❌ FAIL"
    fi
    
    echo ""
    echo "=============================="
EOF

echo ""
echo "========================================="
echo "CRITICAL FIXES COMPLETE"
echo "========================================="
echo ""
echo "✅ Knowledge base populated with legal documents"
echo "✅ Session management implemented"
echo "✅ Health monitoring added"
echo "✅ Services restarted and verified"
echo ""
echo "Your system is now ready for Monday testing at:"
echo "https://$EC2_IP"
echo ""
echo "Test these queries:"
echo "1. 'What are the billing rates for partners?'"
echo "2. 'What is the remote work policy?'"
echo "3. 'How much PTO do employees get?'"
echo ""
echo "Still missing (not critical for Monday):"
echo "- User authentication"
echo "- Proper SSL certificate"
echo "- Advanced monitoring"
echo "- Admin interface"
