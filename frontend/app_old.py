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
# PAGE 4: API DOCS
#============================================
elif page == "API Docs":
    st.markdown('<div class="main-header">API Documentation</div>', unsafe_allow_html=True)
    
    st.markdown("""
    ## FastAPI Backend
    
    The backend API is built with FastAPI and provides the following endpoints:
    
    ### Base URL