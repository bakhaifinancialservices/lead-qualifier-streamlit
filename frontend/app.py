# CORRECTED: frontend/app.py - Full File with Fixed API Docs Page

import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

API_URL = os.getenv('API_URL', 'http://localhost:8000')

# Page config
st.set_page_config(
    page_title="Lead Qualifier Pro",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #2563eb;
        text-align: center;
        margin-bottom: 1rem;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 20px;
        border-radius: 10px;
        color: white;
        text-align: center;
    }
    .success-box {
        padding: 1rem;
        background-color: #d1fae5;
        border-left: 4px solid #10b981;
        border-radius: 4px;
        margin: 1rem 0;
    }
    .error-box {
        padding: 1rem;
        background-color: #fee2e2;
        border-left: 4px solid #ef4444;
        border-radius: 4px;
        margin: 1rem 0;
    }
    .code-block {
        background-color: #1e293b;
        color: #e2e8f0;
        padding: 1rem;
        border-radius: 8px;
        font-family: 'Courier New', monospace;
        overflow-x: auto;
    }
    .endpoint-card {
        background-color: #f8fafc;
        border-left: 4px solid #3b82f6;
        padding: 1rem;
        border-radius: 4px;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Sidebar navigation
page = st.sidebar.selectbox(
    "📊 Navigate",
    ["Lead Capture Form", "Dashboard", "Analytics", "API Docs"]
)

#============================================
# PAGE 1: LEAD CAPTURE FORM
#============================================
if page == "Lead Capture Form":
    st.markdown('<div class="main-header">Get Financial Advice</div>', unsafe_allow_html=True)
    st.markdown("**Connect with expert financial advisors in 24 hours**")
    st.markdown("---")
    
    # Form
    with st.form("lead_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        
        with col1:
            name = st.text_input("Full Name *", placeholder="Rajesh Kumar")
            email = st.text_input("Email Address *", placeholder="rajesh@example.com")
        
        with col2:
            phone = st.text_input("Phone Number *", placeholder="+91 98765 43210")
            source = st.selectbox("How did you hear about us?", 
                                ["Website", "Referral", "Social Media", "Advertisement", "Other"])
        
        message = st.text_area(
            "What do you need help with? *",
            placeholder="Tell us about your financial goals, timeline, and budget...",
            height=120
        )
        
        st.caption("💡 Be specific about your goals, budget, and timeline for better matching")
        
        submitted = st.form_submit_button("🚀 Get Matched with an Advisor", use_container_width=True)
        
        if submitted:
            if not name or not email or not phone or not message:
                st.markdown('<div class="error-box">❌ Please fill in all required fields</div>', 
                          unsafe_allow_html=True)
            else:
                with st.spinner("🤖 AI is analyzing your requirements..."):
                    try:
                        # Call API
                        response = requests.post(
                            f"{API_URL}/api/leads",
                            json={
                                "name": name,
                                "email": email,
                                "phone": phone,
                                "initial_message": message,
                                "source": source.lower()
                            },
                            timeout=30
                        )
                        
                        if response.status_code == 201:
                            lead_data = response.json()
                            
                            st.markdown('<div class="success-box">✅ Success! We\'ll contact you within 24 hours.</div>',
                                      unsafe_allow_html=True)
                            
                            # Show qualification summary
                            st.success("**Your Profile Summary:**")
                            col1, col2, col3, col4 = st.columns(4)
                            
                            col1.metric("Quality Score", f"{lead_data.get('quality_score', 0)}/100")
                            col2.metric("Goal", (lead_data.get('goal', 'unclear') or 'unclear').replace('_', ' ').title())
                            col3.metric("Timeline", (lead_data.get('timeline', 'unclear') or 'unclear').replace('_', ' ').title())
                            col4.metric("Budget Range", lead_data.get('budget_range', 'Not disclosed'))
                            
                            # Show next steps
                            st.info("**Next Steps:**\n- An advisor will review your profile\n- You'll receive a call/email within 24 hours\n- They'll discuss your goals and create a customized plan")
                        
                        else:
                            error_detail = response.json().get('detail', 'Unknown error')
                            st.markdown(f'<div class="error-box">❌ {error_detail}</div>', 
                                      unsafe_allow_html=True)
                    
                    except requests.exceptions.ConnectionError:
                        st.error("⚠️ Cannot connect to backend. Make sure FastAPI is running on http://localhost:8000")
                    except Exception as e:
                        st.error(f"❌ Error: {str(e)}")

#============================================
# PAGE 2: DASHBOARD
#============================================
elif page == "Dashboard":
    st.markdown('<div class="main-header">Lead Dashboard</div>', unsafe_allow_html=True)
    
    # Fetch stats
    try:
        stats_response = requests.get(f"{API_URL}/api/stats", timeout=10)
        stats = stats_response.json() if stats_response.status_code == 200 else {}
        
        # Summary metrics
        col1, col2, col3, col4, col5 = st.columns(5)
        
        col1.metric("Total Leads", stats.get('total', 0))
        col2.metric("🔥 Hot", stats.get('hot', 0))
        col3.metric("⚠️ Warm", stats.get('warm', 0))
        col4.metric("❄️ Cold", stats.get('cold', 0))
        col5.metric("⚡ Fraud", stats.get('fraud', 0))
        
        st.markdown("---")
        
        # Filters
        st.subheader("Filters")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            score_filter = st.selectbox("Score Range", ["All", "Hot (70+)", "Warm (40-69)", "Cold (<40)"])
        with col2:
            status_filter = st.selectbox("Status", ["All", "new", "assigned", "contacted", "closed"])
        with col3:
            limit = st.number_input("Results Limit", min_value=10, max_value=1000, value=100, step=10)
        
        # Build query params
        params = {"limit": limit}
        if score_filter == "Hot (70+)":
            params["min_score"] = 70
        elif score_filter == "Warm (40-69)":
            params["min_score"] = 40
            params["max_score"] = 69
        elif score_filter == "Cold (<40)":
            params["max_score"] = 39
        
        if status_filter != "All":
            params["status"] = status_filter
        
        # Fetch leads
        leads_response = requests.get(f"{API_URL}/api/leads", params=params, timeout=10)
        
        if leads_response.status_code == 200:
            leads = leads_response.json()
            
            if not leads:
                st.info("No leads found matching your filters.")
            else:
                # Convert to DataFrame
                df = pd.DataFrame(leads)
                
                # Display count
                st.subheader(f"Leads ({len(df)})")
                
                # Style the dataframe
                def highlight_score(val):
                    if pd.isna(val):
                        return ''
                    if val >= 70:
                        return 'background-color: #d1fae5'
                    elif val >= 40:
                        return 'background-color: #fef3c7'
                    else:
                        return 'background-color: #fee2e2'
                
                # Select columns to display
                display_columns = ['id', 'name', 'email', 'phone', 'goal', 'timeline', 'budget_range', 'quality_score', 'status', 'created_at']
                display_df = df[display_columns].copy()
                
                # Rename for better readability
                display_df.columns = ['ID', 'Name', 'Email', 'Phone', 'Goal', 'Timeline', 'Budget', 'Score', 'Status', 'Created']
                
                # Apply styling
                styled_df = display_df.style.applymap(highlight_score, subset=['Score'])
                
                st.dataframe(styled_df, use_container_width=True, height=400)
                
                # Download CSV
                csv = df.to_csv(index=False)
                st.download_button(
                    label="📥 Download as CSV",
                    data=csv,
                    file_name=f"leads_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv"
                )
                
                # Lead details expander
                st.subheader("Lead Details")
                selected_id = st.selectbox("Select Lead ID to view details:", df['id'].tolist())
                
                if selected_id:
                    lead_detail = requests.get(f"{API_URL}/api/leads/{selected_id}", timeout=10).json()
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        st.write("**Contact Information:**")
                        st.write(f"Name: {lead_detail['name']}")
                        st.write(f"Email: {lead_detail['email']}")
                        st.write(f"Phone: {lead_detail['phone']}")
                    
                    with col2:
                        st.write("**Qualification:**")
                        st.write(f"Score: {lead_detail.get('quality_score', 'N/A')}/100")
                        st.write(f"Goal: {lead_detail.get('goal', 'N/A')}")
                        st.write(f"Timeline: {lead_detail.get('timeline', 'N/A')}")
                        st.write(f"Budget: {lead_detail.get('budget_range', 'N/A')}")
                    
                    st.write("**Initial Message:**")
                    st.info(lead_detail['initial_message'])
                    
                    # Update status
                    st.write("**Update Lead:**")
                    new_status = st.selectbox("Change Status:", ["new", "assigned", "contacted", "meeting_booked", "closed", "lost"])
                    assigned_to = st.text_input("Assign To (name/email):")
                    
                    if st.button("Update Lead"):
                        update_response = requests.patch(
                            f"{API_URL}/api/leads/{selected_id}",
                            json={"status": new_status, "assigned_to": assigned_to if assigned_to else None},
                            timeout=10
                        )
                        
                        if update_response.status_code == 200:
                            st.success("✅ Lead updated successfully!")
                            st.rerun()
                        else:
                            st.error("❌ Failed to update lead")
        
    except requests.exceptions.ConnectionError:
        st.error("⚠️ Cannot connect to backend. Make sure FastAPI is running on http://localhost:8000")
    except Exception as e:
        st.error(f"❌ Error: {str(e)}")

#============================================
# PAGE 3: ANALYTICS
#============================================
elif page == "Analytics":
    st.markdown('<div class="main-header">Analytics</div>', unsafe_allow_html=True)
    
    try:
        # Fetch all leads
        leads_response = requests.get(f"{API_URL}/api/leads", params={"limit": 1000}, timeout=10)
        
        if leads_response.status_code == 200:
            leads = leads_response.json()
            
            if not leads:
                st.info("No data available for analytics yet.")
            else:
                df = pd.DataFrame(leads)
                
                # Score distribution
                st.subheader("Score Distribution")
                fig_hist = px.histogram(df, x='quality_score', nbins=20, 
                                       title='Lead Quality Score Distribution',
                                       labels={'quality_score': 'Quality Score'},
                                       color_discrete_sequence=['#2563eb'])
                st.plotly_chart(fig_hist, use_container_width=True)
                
                # Goal breakdown
                col1, col2 = st.columns(2)
                
                with col1:
                    st.subheader("Goals Distribution")
                    goal_counts = df['goal'].value_counts()
                    fig_pie = px.pie(values=goal_counts.values, names=goal_counts.index,
                                    title='Lead Goals')
                    st.plotly_chart(fig_pie, use_container_width=True)
                
                with col2:
                    st.subheader("Timeline Distribution")
                    timeline_counts = df['timeline'].value_counts()
                    fig_bar = px.bar(x=timeline_counts.index, y=timeline_counts.values,
                                    title='Lead Timelines',
                                    labels={'x': 'Timeline', 'y': 'Count'})
                    st.plotly_chart(fig_bar, use_container_width=True)
                
                # Leads over time
                st.subheader("Leads Over Time")
                df['created_date'] = pd.to_datetime(df['created_at']).dt.date
                daily_leads = df.groupby('created_date').size().reset_index(name='count')
                fig_line = px.line(daily_leads, x='created_date', y='count',
                                  title='Daily Lead Volume',
                                  labels={'created_date': 'Date', 'count': 'Number of Leads'})
                st.plotly_chart(fig_line, use_container_width=True)
                
    except Exception as e:
        st.error(f"❌ Error loading analytics: {str(e)}")

#============================================
# PAGE 4: API DOCS (CORRECTED VERSION)
#============================================
elif page == "API Docs":
    st.markdown('<div class="main-header">API Documentation</div>', unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Quick links
    st.subheader("🚀 Quick Access")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f"[📖 Swagger UI]({API_URL}/docs)")
    with col2:
        st.markdown(f"[📘 ReDoc]({API_URL}/redoc)")
    with col3:
        st.markdown(f"[🏥 Health Check]({API_URL}/)")
    
    st.markdown("---")
    
    # Base URL
    st.subheader("🌐 Base URL")
    st.code(API_URL, language="text")
    
    st.markdown("---")
    
    # Endpoints
    st.subheader("📡 API Endpoints")
    
    # Endpoint 1: Create Lead
    with st.expander("**POST** /api/leads - Create New Lead", expanded=True):
        st.markdown("**Description:** Submit a new lead for qualification")
        
        st.markdown("**Request Body:**")
        st.code("""
{
  "name": "string",
  "email": "user@example.com",
  "phone": "string",
  "initial_message": "string",
  "source": "web"
}
        """, language="json")
        
        st.markdown("**Example Request (cURL):**")
        st.code(f"""
curl -X POST "{API_URL}/api/leads" \\
  -H "Content-Type: application/json" \\
  -d '{{
    "name": "Rajesh Kumar",
    "email": "rajesh@example.com",
    "phone": "+91 9876543210",
    "initial_message": "I want to invest 20 lakhs for retirement",
    "source": "web"
  }}'
        """, language="bash")
        
        st.markdown("**Example Request (Python):**")
        st.code(f"""
import requests

response = requests.post(
    "{API_URL}/api/leads",
    json={{
        "name": "Rajesh Kumar",
        "email": "rajesh@example.com",
        "phone": "+91 9876543210",
        "initial_message": "I want to invest 20 lakhs for retirement",
        "source": "web"
    }}
)

print(response.json())
        """, language="python")
        
        st.markdown("**Response (201 Created):**")
        st.code("""
{
  "id": 1,
  "name": "Rajesh Kumar",
  "email": "rajesh@example.com",
  "phone": "+91 9876543210",
  "initial_message": "I want to invest 20 lakhs for retirement",
  "goal": "retirement",
  "timeline": "5+_years",
  "budget_range": "20-50L",
  "quality_score": 82,
  "is_fraud": false,
  "status": "new",
  "created_at": "2026-02-15T10:30:00Z"
}
        """, language="json")
    
    # Endpoint 2: Get All Leads
    with st.expander("**GET** /api/leads - Get All Leads"):
        st.markdown("**Description:** Retrieve leads with optional filters")
        
        st.markdown("**Query Parameters:**")
        st.markdown("""
        - `skip` (integer): Number of records to skip (default: 0)
        - `limit` (integer): Maximum records to return (default: 100)
        - `status` (string): Filter by status (new, assigned, contacted, closed)
        - `min_score` (integer): Minimum quality score (0-100)
        - `max_score` (integer): Maximum quality score (0-100)
        """)
        
        st.markdown("**Example Request (cURL):**")
        st.code(f"""
curl -X GET "{API_URL}/api/leads?min_score=70&limit=50"
        """, language="bash")
        
        st.markdown("**Example Request (Python):**")
        st.code(f"""
import requests

response = requests.get(
    "{API_URL}/api/leads",
    params={{
        "min_score": 70,
        "limit": 50,
        "status": "new"
    }}
)

leads = response.json()
print(f"Found {{len(leads)}} leads")
        """, language="python")
        
        st.markdown("**Response (200 OK):**")
        st.code("""
[
  {
    "id": 1,
    "name": "Rajesh Kumar",
    "email": "rajesh@example.com",
    "quality_score": 82,
    "status": "new",
    ...
  },
  {
    "id": 2,
    "name": "Priya Sharma",
    "email": "priya@example.com",
    "quality_score": 75,
    "status": "new",
    ...
  }
]
        """, language="json")
    
    # Endpoint 3: Get Single Lead
    with st.expander("**GET** /api/leads/{lead_id} - Get Lead by ID"):
        st.markdown("**Description:** Retrieve a specific lead's details")
        
        st.markdown("**Path Parameters:**")
        st.markdown("- `lead_id` (integer): The ID of the lead")
        
        st.markdown("**Example Request (cURL):**")
        st.code(f"""
curl -X GET "{API_URL}/api/leads/1"
        """, language="bash")
        
        st.markdown("**Example Request (Python):**")
        st.code(f"""
import requests

lead_id = 1
response = requests.get(f"{API_URL}/api/leads/{{lead_id}}")

if response.status_code == 200:
    lead = response.json()
    print(f"Lead: {{lead['name']}}, Score: {{lead['quality_score']}}")
else:
    print("Lead not found")
        """, language="python")
    
    # Endpoint 4: Update Lead
    with st.expander("**PATCH** /api/leads/{lead_id} - Update Lead"):
        st.markdown("**Description:** Update lead status or assignment")
        
        st.markdown("**Request Body:**")
        st.code("""
{
  "status": "assigned",
  "assigned_to": "advisor@example.com"
}
        """, language="json")
        
        st.markdown("**Example Request (cURL):**")
        st.code(f"""
curl -X PATCH "{API_URL}/api/leads/1" \\
  -H "Content-Type: application/json" \\
  -d '{{
    "status": "assigned",
    "assigned_to": "advisor@example.com"
  }}'
        """, language="bash")
        
        st.markdown("**Example Request (Python):**")
        st.code(f"""
import requests

lead_id = 1
response = requests.patch(
    f"{API_URL}/api/leads/{{lead_id}}",
    json={{
        "status": "assigned",
        "assigned_to": "advisor@example.com"
    }}
)

print("Updated:", response.json())
        """, language="python")
    
    # Endpoint 5: Get Statistics
    with st.expander("**GET** /api/stats - Get Statistics"):
        st.markdown("**Description:** Get dashboard statistics")
        
        st.markdown("**Example Request (cURL):**")
        st.code(f"""
curl -X GET "{API_URL}/api/stats"
        """, language="bash")
        
        st.markdown("**Example Request (Python):**")
        st.code(f"""
import requests

response = requests.get("{API_URL}/api/stats")
stats = response.json()

print(f"Total Leads: {{stats['total']}}")
print(f"Hot Leads: {{stats['hot']}}")
print(f"Warm Leads: {{stats['warm']}}")
        """, language="python")
        
        st.markdown("**Response (200 OK):**")
        st.code("""
{
  "total": 150,
  "hot": 45,
  "warm": 80,
  "cold": 20,
  "fraud": 5
}
        """, language="json")
    
    st.markdown("---")
    
    # Error Responses
    st.subheader("⚠️ Error Responses")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**400 Bad Request**")
        st.code("""
{
  "detail": "Submission flagged: Disposable email"
}
        """, language="json")
        
        st.markdown("**404 Not Found**")
        st.code("""
{
  "detail": "Lead not found"
}
        """, language="json")
    
    with col2:
        st.markdown("**422 Validation Error**")
        st.code("""
{
  "detail": [
    {
      "loc": ["body", "email"],
      "msg": "Invalid email address",
      "type": "value_error"
    }
  ]
}
        """, language="json")
    
    st.markdown("---")
    
    # Testing Section
    st.subheader("🧪 Test the API")
    
    st.markdown("**Quick Test Form:**")
    
    with st.form("api_test_form"):
        test_name = st.text_input("Name", value="Test User")
        test_email = st.text_input("Email", value="test@example.com")
        test_phone = st.text_input("Phone", value="9876543210")
        test_message = st.text_area("Message", value="I want to invest 10 lakhs")
        
        if st.form_submit_button("Test API"):
            with st.spinner("Calling API..."):
                try:
                    response = requests.post(
                        f"{API_URL}/api/leads",
                        json={
                            "name": test_name,
                            "email": test_email,
                            "phone": test_phone,
                            "initial_message": test_message,
                            "source": "api_test"
                        },
                        timeout=10
                    )
                    
                    st.write("**Response Status:**", response.status_code)
                    st.write("**Response Body:**")
                    st.json(response.json())
                    
                except Exception as e:
                    st.error(f"Error: {str(e)}")
    
    st.markdown("---")
    
    # Technology Stack
    st.subheader("🛠️ Technology Stack")
    
    tech_col1, tech_col2 = st.columns(2)
    
    with tech_col1:
        st.markdown("""
        **Backend:**
        - Framework: FastAPI
        - Database: PostgreSQL
        - ORM: SQLAlchemy
        - Migrations: Alembic
        """)
    
    with tech_col2:
        st.markdown("""
        **Services:**
        - AI: Google Gemini 2.0 Flash
        - Email: Resend
        - Validation: Pydantic
        - Testing: Pytest
        """)
    
    st.markdown("---")
    
    # Additional Resources
    st.subheader("📚 Additional Resources")
    
    st.markdown("""
    - **Full API Documentation:** Visit `/docs` for interactive Swagger UI
    - **Alternative Docs:** Visit `/redoc` for detailed ReDoc documentation
    - **Source Code:** [GitHub Repository](#)
    - **Support:** [Create an Issue](#)
    """)
    
    # API Health Check
    st.markdown("---")
    st.subheader("🏥 API Health Check")
    
    if st.button("Check API Status"):
        try:
            response = requests.get(f"{API_URL}/", timeout=5)
            if response.status_code == 200:
                st.success("✅ API is healthy and running!")
                st.json(response.json())
            else:
                st.warning(f"⚠️ API returned status code: {response.status_code}")
        except requests.exceptions.ConnectionError:
            st.error("❌ Cannot connect to API. Make sure it's running at " + API_URL)
        except Exception as e:
            st.error(f"❌ Error: {str(e)}")