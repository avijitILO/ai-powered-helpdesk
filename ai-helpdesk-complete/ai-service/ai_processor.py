import logging
import re
from typing import Dict, List, Any
from datetime import datetime
import asyncio
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class AIResponse:
    response: str
    department: str
    priority: str
    confidence: float
    suggested_actions: List[str]
    should_create_ticket: bool

class AIProcessor:
    def __init__(self):
        self.department_keywords = {
            'IT': [
                'computer', 'laptop', 'software', 'hardware', 'network', 'wifi', 'internet',
                'email', 'password', 'login', 'access', 'printer', 'scanner', 'phone',
                'system', 'application', 'app', 'server', 'database', 'backup', 'virus',
                'malware', 'security', 'vpn', 'remote', 'desktop', 'laptop', 'mouse',
                'keyboard', 'monitor', 'screen', 'install', 'update', 'upgrade', 'error',
                'crash', 'freeze', 'slow', 'performance'
            ],
            'HR': [
                'payroll', 'salary', 'wage', 'benefits', 'insurance', 'vacation', 'leave',
                'sick', 'time off', 'pto', 'holiday', 'overtime', 'schedule', 'shift',
                'employee', 'manager', 'supervisor', 'team', 'department', 'hiring',
                'recruitment', 'onboarding', 'termination', 'resignation', 'performance',
                'review', 'evaluation', 'training', 'development', 'policy', 'handbook',
                'compliance', 'harassment', 'discrimination', 'grievance'
            ],
            'Finance': [
                'expense', 'receipt', 'reimbursement', 'invoice', 'payment', 'bill',
                'cost', 'budget', 'financial', 'accounting', 'money', 'cash', 'card',
                'procurement', 'purchase', 'order', 'vendor', 'supplier', 'contract',
                'audit', 'tax', 'revenue', 'profit', 'loss', 'reporting', 'analysis'
            ],
            'Facilities': [
                'office', 'building', 'room', 'desk', 'chair', 'furniture', 'cleaning',
                'maintenance', 'repair', 'hvac', 'heating', 'cooling', 'temperature',
                'lighting', 'parking', 'security', 'access card', 'badge', 'door',
                'lock', 'key', 'elevator', 'stairs', 'bathroom', 'kitchen', 'supplies',
                'catering', 'meeting room', 'conference', 'booking', 'reservation'
            ]
        }
        
        self.priority_keywords = {
            'urgent': [
                'urgent', 'emergency', 'critical', 'asap', 'immediately', 'now',
                'down', 'outage', 'broken', 'not working', 'failed', 'crashed',
                'deadline', 'blocking', 'stuck', 'cannot work', 'production'
            ],
            'high': [
                'important', 'high', 'priority', 'soon', 'today', 'this week',
                'affecting multiple', 'team', 'department', 'customers', 'business'
            ],
            'medium': [
                'normal', 'standard', 'regular', 'when possible', 'convenient'
            ],
            'low': [
                'low', 'minor', 'cosmetic', 'enhancement', 'feature', 'improvement',
                'suggestion', 'nice to have', 'future'
            ]
        }
        
        self.interaction_stats = {
            'total_interactions': 0,
            'tickets_created': 0,
            'knowledge_base_hits': 0,
            'department_distribution': {'IT': 0, 'HR': 0, 'Finance': 0, 'Facilities': 0, 'General': 0}
        }

    async def initialize(self):
        """Initialize AI processor"""
        logger.info("Initializing AI Processor...")
        # In production, this would initialize the actual LLM
        logger.info("AI Processor initialized successfully")

    async def process_message(self, message: str, db=None) -> AIResponse:
        """Process user message and generate AI response"""
        try:
            logger.info(f"Processing message: {message[:100]}...")
            
            # Update stats
            self.interaction_stats['total_interactions'] += 1
            
            # Classify department and priority
            department = self._classify_department(message)
            priority = self._classify_priority(message)
            
            # Update department stats
            self.interaction_stats['department_distribution'][department] += 1
            
            # Generate response
            response_text = await self._generate_response(message, department, priority)
            
            # Determine if ticket should be created
            should_create_ticket = self._should_create_ticket(message, priority)
            if should_create_ticket:
                self.interaction_stats['tickets_created'] += 1
            
            # Generate suggested actions
            suggested_actions = self._generate_suggested_actions(department, priority)
            
            # Calculate confidence (simplified)
            confidence = self._calculate_confidence(message, department, priority)
            
            return AIResponse(
                response=response_text,
                department=department,
                priority=priority,
                confidence=confidence,
                suggested_actions=suggested_actions,
                should_create_ticket=should_create_ticket
            )
            
        except Exception as e:
            logger.error(f"Error processing message: {str(e)}")
            return AIResponse(
                response="I apologize, but I encountered an error processing your request. I'll create a support ticket to ensure you get the help you need.",
                department="IT",
                priority="medium",
                confidence=0.0,
                suggested_actions=["Contact support directly", "Try again later"],
                should_create_ticket=True
            )

    def _classify_department(self, message: str) -> str:
        """Classify message into department based on keywords"""
        message_lower = message.lower()
        scores = {}
        
        for dept, keywords in self.department_keywords.items():
            score = sum(1 for keyword in keywords if keyword in message_lower)
            scores[dept] = score
        
        # Find department with highest score
        max_score = max(scores.values())
        if max_score > 0:
            return max(scores, key=scores.get)
        
        return 'General'

    def _classify_priority(self, message: str) -> str:
        """Classify message priority based on keywords"""
        message_lower = message.lower()
        
        for priority, keywords in self.priority_keywords.items():
            if any(keyword in message_lower for keyword in keywords):
                return priority
        
        return 'medium'

    async def _generate_response(self, message: str, department: str, priority: str) -> str:
        """Generate AI response based on message analysis"""
        
        # Check for common patterns and generate appropriate responses
        if any(word in message.lower() for word in ['password', 'login', 'access']):
            return f"""I understand you're having trouble with login/password issues. Here's what I can help you with:

1. **Password Reset**: You can reset your password through our self-service portal or I can create a ticket for IT support to assist you.

2. **Account Access**: If you're locked out, our IT team can unlock your account and verify your access permissions.

3. **Two-Factor Authentication**: If you're having 2FA issues, we can help you reset or reconfigure your authentication methods.

Since this is categorized as {priority} priority for the {department} department, {'I recommend creating a support ticket for immediate assistance' if priority in ['urgent', 'high'] else 'I can create a support ticket to track this issue'}.

Would you like me to proceed with creating a support ticket?"""

        elif any(word in message.lower() for word in ['leave', 'vacation', 'time off', 'pto']):
            return f"""I can help you with your leave request. Here's the process:

1. **Submit Request**: Log into the HR portal and submit your leave request with the specific dates you need.

2. **Manager Approval**: Your request will be routed to your manager for approval. This typically takes 1-2 business days.

3. **HR Processing**: Once approved by your manager, HR will process the request and update your leave balance.

4. **Confirmation**: You'll receive email confirmation once everything is processed.

**Important reminders:**
- Submit requests at least 2 weeks in advance when possible
- Check the company calendar for blackout dates
- Ensure work coverage is arranged

Since this is {priority} priority, {'I recommend contacting HR directly' if priority in ['urgent', 'high'] else 'you can follow the standard process'}. Would you like me to create an HR ticket to track your request?"""

        elif any(word in message.lower() for word in ['expense', 'reimbursement', 'receipt']):
            return f"""I can assist you with your expense-related inquiry. Here's what you need to know:

1. **Expense Reports**: Submit through the finance portal with all receipts attached within 30 days of the expense.

2. **Reimbursement Timeline**: 
   - Manager approval: 1-2 business days
   - Finance review: 2-3 business days  
   - Payment processing: 5-7 business days

3. **Required Information**:
   - Clear, readable receipts
   - Business justification
   - Proper expense categories
   - Cost center/department codes

4. **Common Issues**:
   - Missing receipts (required for amounts over $25)
   - Late submissions (over 30 days)
   - Personal expenses mixed with business

Since this is {priority} priority for {department}, {'I recommend contacting Finance immediately' if priority in ['urgent', 'high'] else 'I can create a Finance ticket to track your inquiry'}.

Would you like me to create a support ticket for this?"""

        else:
            # Generic response based on department
            dept_responses = {
                'IT': f"""I understand you have an IT-related inquiry. As this is classified as {priority} priority, here's how I can help:

**Immediate Steps:**
1. Try restarting your device if it's a performance issue
2. Check if others are experiencing the same problem
3. Verify all cables and connections are secure

**Next Steps:**
Our IT support team can assist with hardware issues, software problems, network connectivity, security concerns, and system access. 

{'Given the urgency, I strongly recommend creating a support ticket immediately' if priority in ['urgent', 'high'] else 'I can create a support ticket to ensure proper tracking and resolution'}.

Would you like me to create an IT support ticket for you?""",

                'HR': f"""Thank you for reaching out about your HR inquiry. This has been classified as {priority} priority. Here's how we can assist:

**Common HR Services:**
- Employee benefits and insurance questions
- Payroll and compensation inquiries  
- Leave and time-off requests
- Policy clarifications
- Training and development opportunities

**Response Timeline:**
{'HR will prioritize your request due to its urgent nature' if priority in ['urgent', 'high'] else 'Standard HR inquiries are typically resolved within 2-3 business days'}.

Our HR team is equipped to handle all employee-related matters with confidentiality and care.

Would you like me to create an HR support ticket to ensure proper handling?""",

                'Finance': f"""I can help with your finance-related inquiry. This has been categorized as {priority} priority. Here's what our Finance team can assist with:

**Finance Services:**
- Expense report processing and reimbursements
- Invoice and payment inquiries
- Budget and cost center questions
- Procurement and vendor management
- Financial reporting and analysis

**Processing Timeline:**
{'Given the priority level, Finance will expedite your request' if priority in ['urgent', 'high'] else 'Standard finance requests are processed within 3-5 business days'}.

Our Finance team ensures accurate and timely handling of all financial matters.

Would you like me to create a Finance support ticket for proper tracking?""",

                'Facilities': f"""I understand you have a facilities-related concern. This has been marked as {priority} priority. Here's how our Facilities team can help:

**Facilities Services:**
- Building maintenance and repairs
- Office space and seating arrangements
- Meeting room bookings and setup
- Cleaning and janitorial services
- Security and access control
- Parking and transportation

**Response Timeline:**
{'Facilities will address this urgently' if priority in ['urgent', 'high'] else 'Standard facilities requests are handled within 24-48 hours'}.

Our Facilities team ensures a comfortable and functional work environment for everyone.

Would you like me to create a Facilities support ticket?""",

                'General': f"""Thank you for your inquiry. I've analyzed your message and classified it as {priority} priority. While I couldn't determine a specific department, here's how I can help:

**Next Steps:**
1. I can create a general support ticket that will be routed to the appropriate team
2. You can contact your manager or team lead for department-specific guidance
3. Check our knowledge base for self-service options

**Response Timeline:**
{'Your request will be prioritized and routed urgently' if priority in ['urgent', 'high'] else 'General inquiries are typically routed and addressed within 24 hours'}.

Our support team will ensure your request reaches the right department for proper resolution.

Would you like me to create a support ticket for you?"""
            }
            
            return dept_responses.get(department, dept_responses['General'])

    def _should_create_ticket(self, message: str, priority: str) -> bool:
        """Determine if a ticket should be created"""
        # Always create tickets for urgent/high priority
        if priority in ['urgent', 'high']:
            return True
        
        # Check for problem indicators
        problem_indicators = [
            'not working', 'broken', 'error', 'problem', 'issue', 'help',
            'cannot', 'unable', 'failed', 'stuck', 'wrong', 'missing'
        ]
        
        if any(indicator in message.lower() for indicator in problem_indicators):
            return True
        
        # Create ticket for medium priority if message is complex
        if priority == 'medium' and len(message.split()) > 10:
            return True
        
        return False

    def _generate_suggested_actions(self, department: str, priority: str) -> List[str]:
        """Generate suggested actions based on department and priority"""
        actions = []
        
        base_actions = {
            'IT': [
                "Check IT knowledge base for solutions",
                "Try basic troubleshooting (restart, reconnect)",
                "Contact IT helpdesk if issue persists",
                "Document error messages or screenshots"
            ],
            'HR': [
                "Review employee handbook for policies",
                "Check HR portal for self-service options", 
                "Contact your manager if appropriate",
                "Email HR directly for sensitive matters"
            ],
            'Finance': [
                "Check expense management system",
                "Review financial policies and procedures",
                "Gather all relevant receipts/documentation",
                "Contact Finance team for clarifications"
            ],
            'Facilities': [
                "Report to facilities management",
                "Check for building-wide notifications",
                "Contact security for urgent safety issues",
                "Submit maintenance requests online"
            ],
            'General': [
                "Check company intranet for information",
                "Contact your direct supervisor",
                "Review relevant department policies",
                "Submit general inquiry ticket"
            ]
        }
        
        actions.extend(base_actions.get(department, base_actions['General'])[:3])
        
        if priority in ['urgent', 'high']:
            actions.insert(0, f"Contact {department} support immediately")
        
        return actions

    def _calculate_confidence(self, message: str, department: str, priority: str) -> float:
        """Calculate confidence score for the classification"""
        # Simple confidence calculation based on keyword matches
        dept_keywords = self.department_keywords.get(department, [])
        priority_keywords = self.priority_keywords.get(priority, [])
        
        message_lower = message.lower()
        dept_matches = sum(1 for keyword in dept_keywords if keyword in message_lower)
        priority_matches = sum(1 for keyword in priority_keywords if keyword in message_lower)
        
        # Base confidence
        confidence = 0.5
        
        # Boost based on keyword matches
        if dept_matches > 0:
            confidence += min(dept_matches * 0.1, 0.3)
        
        if priority_matches > 0:
            confidence += min(priority_matches * 0.1, 0.2)
        
        # Cap at 0.95
        return min(confidence, 0.95)

    async def get_interaction_stats(self) -> Dict[str, Any]:
        """Get AI interaction statistics"""
        return self.interaction_stats