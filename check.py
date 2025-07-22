import streamlit as st
import pandas as pd
from datetime import datetime
import google.generativeai as genai
import json
import os
from typing import Dict, Any
import re
from supabase import create_client, Client

# Configure page
import streamlit as st

st.set_page_config(
    page_title="Digital Marketing Form",
    page_icon="💢",  # Temp emoji if image isn't supported directly
    layout="wide"
)

# Inject custom favicon/logo using HTML
favicon = "/logo.jpg"  # Upload your logo somewhere (imgur, Cloudinary, etc.)
st.markdown(
    f"""
    <head>
        <link rel="icon" type="image/png" href="{favicon}">
    </head>
    """,
    unsafe_allow_html=True
)


# Supabase Configuration
SUPABASE_URL = "https://zdvemdysvawaoiiababe.supabase.co"
SUPABASE_ANON_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InpkdmVtZHlzdmF3YW9paWFiYWJlIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTMxNjczMjUsImV4cCI6MjA2ODc0MzMyNX0.H42eeqDM9r2_M858KjuMBKJMnJM8nd1yzDngEbUgPGo"

# Initialize Supabase client
@st.cache_resource
def init_supabase():
    return create_client(SUPABASE_URL, SUPABASE_ANON_KEY)

supabase: Client = init_supabase()

# Knowledge Base
ZAPPS_KNOWLEDGE_BASE = {
    "highlights": [
        "We provide automation solutions for e-commerce, including cart recovery, order processing, and CRM integration.",
        "Our pricing starts at 20,000 PKR/month, and includes AI-based support agents, marketing automation, and analytics.",
        "For low-revenue clients (<100k PKR), we offer lean automation models to maximize ROI without large investment."
    ],
    "pricing_plans": {
        "starter": {
            "name": "Crystal Clear Starter Plan",
            "description": "Unlocking Value for Your Healthy Food Brand",
            "features": [
                "8 Designed Posts (static/image)",
                "2 Instagram Reels (basic video editing)",
                "Captions + Hashtag Research",
                "Profile Bio Optimization",
                "Monthly Report (reach & engagement)"
            ],
            "price_pkr": "PKR 16,000 – 37,990",
            "price_usd": "$80",
            "price_sar": "SAR 500"
        },
        "growth": {
            "name": "Growth Plan",
            "description": "Ideal for businesses looking to grow audience & engagement",
            "features": [
                "8 TikTok Videos per Month",
                "Trendy Editing, Filters, Voiceover/Text",
                "Product Showcase with brand voice",
                "Custom Strategy + Bi-Weekly Report",
                "Audience Targeting & Growth Tips"
            ],
            "price_pkr": "PKR 25,000 – 75,980",
            "price_usd": "$150",
            "price_sar": "SAR 1,000"
        },
        "pro": {
            "name": "Pro Brand Plan",
            "description": "Strong online presence, high-level engagement",
            "features": [
                "12–16 Viral TikTok Videos",
                "Full Scripting + Trend Research",
                "Premium Editing with Voiceovers + Effects",
                "Brand Challenges, Skits, Influencer Collabs",
                "Hashtag Campaigns + Weekly Reports",
                "24/7 Community Management & Support"
            ],
            "price_pkr": "PKR 35,000 – 113,970",
            "price_usd": "$200",
            "price_sar": "SAR 1,500"
        }
    }
}

# Country to Currency Mapping
COUNTRY_CURRENCY = {
    "Pakistan": {"currency": "PKR", "symbol": "Rs.", "rate": 1},
    "Saudi Arabia": {"currency": "SAR", "symbol": "SAR", "rate": 0.11},  # 1 PKR = 0.11 SAR approx
    "United States": {"currency": "USD", "symbol": "$", "rate": 0.0036},  # 1 PKR = 0.0036 USD approx
    "United Kingdom": {"currency": "GBP", "symbol": "£", "rate": 0.0028},
    "Canada": {"currency": "CAD", "symbol": "C$", "rate": 0.0049},
    "Australia": {"currency": "AUD", "symbol": "A$", "rate": 0.0054},
    "UAE": {"currency": "AED", "symbol": "AED", "rate": 0.013}
}

# Red and White Theme CSS Styling
st.markdown("""
<style>
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    @keyframes glow {
        0%, 100% { box-shadow: 0 0 20px rgba(220, 20, 60, 0.3); }
        50% { box-shadow: 0 0 40px rgba(220, 20, 60, 0.8); }
    }

    .main > div {
        padding-top: 0.5rem;
    }
    
    /* Header styling */
    .main .block-container {
        padding-top: 1rem;
        padding-bottom: 2rem;
    }
    
    [data-testid="stForm"] {
        border: 3px solid #DC143C;
        border-radius: 25px;
        padding: 3rem;
        background: linear-gradient(135deg, #ffffff 0%, #f8f8ff 50%, #ffffff 100%);
        box-shadow: 0 20px 40px rgba(220, 20, 60, 0.2);
        margin: 2rem 0;
    }
    
    .form-section {
        border: 2px solid #DC143C;
        border-radius: 20px;
        padding: 2.5rem;
        margin: 2rem 0;
        background: rgba(255, 255, 255, 0.95);
        box-shadow: 0 12px 30px rgba(220, 20, 60, 0.15);
        transform: perspective(1200px) rotateX(1deg);
        transition: all 0.5s ease;
    }
    
    .form-section:hover {
        transform: perspective(1200px) rotateX(0deg);
        box-shadow: 0 15px 35px rgba(220, 20, 60, 0.25);
    }
    
    h1 {
        color: #DC143C !important;
        text-align: center;
        font-size: 3.5rem !important;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
        margin-bottom: 1rem !important;
        margin-top: 0 !important;
        padding-top: 0 !important;
        background: linear-gradient(45deg, #DC143C, #B22222);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    h3 {
        color: #DC143C !important;
        font-size: 2rem !important;
        border-bottom: 3px solid #DC143C;
        padding-bottom: 1rem;
        margin-bottom: 2rem !important;
        text-shadow: 1px 1px 2px rgba(0,0,0,0.1);
    }
    
    .stSelectbox label, .stTextInput label, .stTextArea label, .stNumberInput label, 
    .stMultiselect label, .stRadio label, .stCheckbox label, .stSlider label {
        color: #000 !important;
        font-weight: 700 !important;
        font-size: 1.1rem !important;
    }
    





            
    /* Input fields styling */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea,
    .stSelectbox > div > div > select {
        background-color: #ffffff !important;
        border: 2px solid #DC143C !important;
        color: #000000 !important;
    }
    
    [data-testid="stFormSubmitButton"] button {
        background: linear-gradient(135deg, #DC143C, #B22222);
        color: #ffffff !important;
        font-weight: bold;
        font-size: 1.4rem;
        padding: 1.5rem 3rem;
        border-radius: 50px;
        border: none;
        box-shadow: 0 10px 25px rgba(220, 20, 60, 0.3);
        transition: all 0.4s ease;
        width: 100%;
    }
    
    [data-testid="stFormSubmitButton"] button:hover {
        transform: translateY(-3px) scale(1.02);
        box-shadow: 0 15px 30px rgba(220, 20, 60, 0.5);
        background: linear-gradient(135deg, #B22222, #8B0000);
    }
    
    .proposal-container {
        background: linear-gradient(135deg, #ffffff 0%, #fff5f5 50%, #ffffff 100%);
        border: 3px solid #DC143C;
        border-radius: 25px;
        padding: 3rem;
        margin: 3rem 0;
        color: #000000;
        box-shadow: 0 20px 45px rgba(220, 20, 60, 0.2);
        transform: perspective(1000px) rotateY(1deg);
        transition: transform 0.5s ease;
        animation: fadeIn 0.8s ease-out;
    }
    
    .proposal-container:hover {
        transform: perspective(1000px) rotateY(0deg);
    }
    
    .plans-container {
        display: flex;
        gap: 2rem;
        margin: 3rem 0;
        justify-content: center;
        flex-wrap: wrap;
        perspective: 1000px;
    }
    
    .plan-card {
        background: #ffffff;
        border: 3px solid #DC143C;
        border-radius: 20px;
        padding: 2.5rem;
        color: #000000;
        margin: 2rem 0;
        width: 300px;
        box-shadow: 0 15px 35px rgba(220, 20, 60, 0.2);
        transform: perspective(800px) rotateX(5deg) scale(0.85);
        transition: all 0.4s ease;
        opacity: 0.85;
        position: relative;
    }
    
    .plan-card.recommended {
        transform: perspective(800px) rotateX(0deg) scale(1.2);
        border: 3px solid #228B22;
        opacity: 1;
        z-index: 10;
        animation: glow 2s ease-in-out infinite alternate;
        box-shadow: 0 0 20px rgba(34, 139, 34, 0.3);
    }
    
    .plan-card:hover:not(.recommended) {
        transform: perspective(800px) rotateX(0deg) scale(1.02);
        opacity: 1;
    }
    
    .plan-card h4 {
        color: #DC143C !important;
        font-size: 1.8rem !important;
        margin-bottom: 1.5rem !important;
        text-shadow: 1px 1px 2px rgba(0,0,0,0.1);
    }
    
    .plan-card ul {
        list-style-type: none;
        padding-left: 0;
    }
    
    .plan-card li {
        margin: 12px 0;
        padding-left: 25px;
        position: relative;
        font-size: 1.1rem;
        color: #000000;
    }
    
    .plan-card li:before {
        content: "✓";
        color: #228B22;
        position: absolute;
        left: 0;
        font-size: 1.2rem;
        font-weight: bold;
    }
    
    .recommended-badge {
        position: absolute;
        top: -15px;
        right: -15px;
        background: #228B22;
        color: white;
        padding: 8px 15px;
        border-radius: 20px;
        font-size: 0.9rem;
        font-weight: bold;
        transform: rotate(15deg);
        box-shadow: 0 5px 15px rgba(34, 139, 34, 0.5);
    }
    
    .highlight-box {
        background: rgba(220, 20, 60, 0.1);
        border-left: 5px solid #DC143C;
        padding: 1.5rem;
        margin: 1.5rem 0;
        border-radius: 10px;
        color: #000000;
        font-weight: 600;
    }
    
    /* Page background */
    .stApp {
        background: linear-gradient(135deg, #ffffff 0%, #f8f8ff 100%);
    }
    
    @media (max-width: 768px) {
        .plans-container {
            flex-direction: column;
            align-items: center;
        }
        
        .plan-card {
            width: 90%;
            max-width: 350px;
        }
        
        .plan-card.recommended {
            transform: scale(1.05);
        }
        
        h1 {
            font-size: 2.5rem !important;
        }
        
        .form-section {
            padding: 1.5rem;
        }
    }
    
    @media (max-width: 480px) {
        .plan-card {
            width: 95%;
            padding: 1.5rem;
        }
        
        h1 {
            font-size: 2rem !important;
        }
    }
</style>
""", unsafe_allow_html=True)

# Initialize Gemini AI
def initialize_gemini():
    """Initialize Gemini AI with API key"""
    try:
        # You need to set your Gemini API key as environment variable or streamlit secret
        api_key =  os.getenv("GEMINI_API_KEY")
        if not api_key:
            st.error("❌ Gemini API key not found. Please set GEMINI_API_KEY in secrets or environment.")
            st.stop()
        
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.5-flash')
        return model
    except Exception as e:
        st.error(f"❌ Error initializing Gemini AI: {str(e)}")
        return None

# Supabase Functions
def save_to_supabase(form_data: Dict, proposal: str):
    """Save client data and AI proposal to Supabase"""
    try:
        # Prepare data for insertion
        client_data = {
            'full_name': f"{form_data['full_name']} {form_data['last_name']}",
            'country': form_data['country'],
            'phone_number': form_data['phone_number'],
            'business_description': form_data['business_description'],
            'monthly_revenue': form_data['monthly_revenue'],
            'marketing_platforms': ', '.join(form_data['marketing_platforms']),
            'ai_proposal': proposal,
            'created_at': datetime.now().isoformat(),
            'client_data': json.dumps(form_data)  # Store full form data as JSON
        }
        
        # Insert into Supabase
        result = supabase.table('client_responses').insert(client_data).execute()
        return True, result
    except Exception as e:
        return False, str(e)

class DigitalMarketingAgent:
    """Agentic AI for Digital Marketing Proposal Generation"""
    
    def __init__(self, model):
        self.model = model
        self.knowledge_base = ZAPPS_KNOWLEDGE_BASE
    
    def convert_currency(self, amount_pkr: float, target_country: str) -> str:
        """Convert PKR amount to target country currency"""
        if target_country not in COUNTRY_CURRENCY:
            return f"PKR {amount_pkr:,.0f}"
        
        currency_info = COUNTRY_CURRENCY[target_country]
        converted_amount = amount_pkr * currency_info["rate"]
        symbol = currency_info["symbol"]
        
        return f"{symbol} {converted_amount:,.0f}"
    
    def analyze_client_needs(self, form_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze client data and determine best plan"""
        monthly_revenue = form_data.get('monthly_revenue', 0)
        marketing_platforms = form_data.get('marketing_platforms', [])
        business_location = form_data.get('business_location', '').lower()
        
        # Determine recommended plan based on revenue and needs
        if monthly_revenue < 50000:  # PKR
            recommended_plan = "starter"
        elif monthly_revenue < 200000:
            recommended_plan = "growth"  
        else:
            recommended_plan = "pro"
        
        # Adjust based on platforms
        if len(marketing_platforms) >= 4:
            recommended_plan = "pro" if recommended_plan != "pro" else "pro"
        
        return {
            "recommended_plan": recommended_plan,
            "plan_info": self.knowledge_base["pricing_plans"][recommended_plan]
        }
    
    def generate_proposal(self, form_data: Dict[str, Any]) -> str:
        """Generate AI-powered proposal using Gemini"""
        
        analysis = self.analyze_client_needs(form_data)
        recommended_plan = analysis["recommended_plan"]
        plan_info = analysis["plan_info"]
        
        # Convert pricing to client's country currency
        country = form_data.get('country', 'Pakistan')
        
        # Create AI prompt
        prompt = f"""
You are a Senior Growth Consultant at ZAPPS — a premium AI marketing agency.

Your job is to write a **short, natural, and premium proposal** for this client:

CLIENT INFO:
- Name: {form_data['full_name']} {form_data['last_name']}
- Country: {form_data['country']}
- Business: {form_data['business_description'][:200]}
- Revenue: {form_data['monthly_revenue']} PKR
- Problem: {form_data['problem_solved'][:150]}
- Platforms: {', '.join(form_data['marketing_platforms'])}
- Marketing status: Ads? {form_data['running_ads']} | Budget: {form_data['ad_budget']}

✅ RULES FOR OUTPUT:
- Keep it under 800 words
- Write EXACTLY 3-4 short paragraphs maximum
- Maximum 2-3 sentences per paragraph
- Use the client's first name (e.g., "{form_data['full_name']}") naturally 2-3 times
- Use exactly 2 emojis (but NOT 🚀)
- DO NOT use any HTML, markdown, bullet points, headings, or code
- Write like a human — no robotic or AI-sounding text
- Focus on ZAPPS ROI, social media strategy, and client growth
- Never mention AI, technology, or systems

🎯 FORMAT:
Write a mini message that includes:  
1. A warm intro  
2. Acknowledgement of their challenge  
3. ZAPPS suggested plan with outcome  just 1 plan 
4. Strong CTA to connect  

Just write the plain message only — no HTML, formatting, or extra styling. just 1 card 
"""

        try:
            response = self.model.generate_content(prompt)
            # Clean the response - remove any formatting
            proposal = response.text.strip()
            # Remove any HTML tags if they appear
            proposal = re.sub(r'<[^>]+>', '', proposal)
            # Remove markdown formatting
            proposal = re.sub(r'[*_#`]', '', proposal)
            # Remove bullet points
            proposal = re.sub(r'^[-•]\s*', '', proposal, flags=re.MULTILINE)
            
            return proposal
        
        except Exception as e:
            return f"Thank you {form_data['full_name']} for sharing your business details with us. We appreciate your interest in growing your business through strategic marketing. Based on your current revenue and marketing needs, we believe there are significant opportunities to enhance your online presence and drive measurable growth. Our team specializes in helping businesses like yours achieve sustainable results through proven strategies and execution. We would love to discuss how we can help you achieve your business goals and take your marketing to the next level."
    
    def create_plan_card(self, plan_info: Dict, country: str, is_recommended: bool = False) -> str:
        """Create styled plan card HTML"""
        
        # Get pricing for the country
        if country == "Pakistan":
            price = plan_info["price_pkr"]
        elif country == "Saudi Arabia":
            price = plan_info["price_sar"]
        else:
            price = plan_info["price_usd"]
        
        features_html = '\n'.join([f'<li>{feature}</li>' for feature in plan_info['features']])
        
        card_class = "plan-card recommended" if is_recommended else "plan-card"
        badge_html = '<div class="recommended-badge">Recommended</div>' if is_recommended else ''
        
        card_html = f"""
        <div class="{card_class}">
            {badge_html}
            <h4>{plan_info['name']}</h4>
            <p style="font-size: 1.2rem; margin-bottom: 1.5rem; color: #000;">{plan_info['description']}</p>
            <ul>
                {features_html}
            </ul>
            <div style="margin-top: 2rem; padding: 1rem; background: rgba(220, 20, 60, 0.1); border-radius: 10px;">
                <h4 style="color: #DC143C; margin: 0;"> Cost: {price}</h4>
            </div>
        </div>
        """
        return card_html

def save_client_data(form_data: Dict, proposal: str) -> str:
    """Save client data as text file"""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    client_name = f"{form_data['full_name']}_{form_data['last_name']}"
    filename = f"{client_name}_Response_{timestamp}.txt"
    
    # Clean filename
    filename = re.sub(r'[^\w\-_\.]', '_', filename)
    
    # Create text content
    content = f"""
DIGITAL MARKETING PROPOSAL
Generated: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}

CLIENT INFORMATION:
Name: {form_data['full_name']} {form_data['last_name']}
Country: {form_data['country']}
Phone: {form_data['phone_number']}
Reference: {form_data.get('reference', 'Direct inquiry')}

BUSINESS OVERVIEW:
{form_data['business_description']}

PROPOSAL:
{proposal}

---
ZAPPS Digital Marketing Agency
Professional Growth Solutions
"""
    
    # Save file
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(content)
        return filename
    except Exception as e:
        return f"response_{timestamp}.txt"

def main():
    st.title(" Digital Marketing Form")
    
    # Initialize AI
    model = initialize_gemini()
    if not model:
        return
    
    agent = DigitalMarketingAgent(model)
    
    with st.form("client_discovery_form"):
        # Country Selection First
        
        country = st.selectbox(
            "Where are you based? *",
            ["Pakistan", "Saudi Arabia", "United States", "United Kingdom", "Canada", "Australia", "UAE"],
            help="Select your country for localized pricing"
        )
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Section 1: Personal Info
      
        st.subheader("All About You")
        
        col1, col2 = st.columns(2)
        with col1:
            full_name = st.text_input("• Your First Name *")
        with col2:
            last_name = st.text_input("• Your Last Name *")

        col3, col4 = st.columns(2)
        with col3:
            reference = st.text_input("• Reference (How did you hear about us?)")
        with col4:
            phone_number = st.text_input("• Phone Number *", placeholder="+1 (555) 123-4567")
        
        st.markdown('</div>', unsafe_allow_html=True)

        # Section 2: Business Info
        
        st.subheader("Your Product and Service")
        
        business_description = st.text_area("• What does your business do? *")
        problem_solved = st.text_area("• What problem does your product/service solve? *")
        unique_selling_point = st.text_area("• What makes your offering unique? *")
        customer_results = st.text_area("• Typical results your customers get?")
        main_competitors = st.text_area("• Who are your main competitors?")
        
        st.markdown('</div>', unsafe_allow_html=True)

        # Section 3: Business Model
        
        st.subheader(" Your Business Model")

        # Sales Channels (Checkboxes)
        st.markdown("• How are you currently selling your product/service?")
        sales_channels = st.multiselect(
            "Select sales channels",
            ["Physical Store", "Shopify", "Amazon", "Instagram Shop", "WhatsApp Business", "Other"]
            if st.session_state.get('other_sales_channel', st.text_area("• Other Sales Channel (if any)"))
            else ["Physical Store", "Shopify", "Amazon", "Instagram Shop", "WhatsApp Business", "Direct Sales"]
        )

        # Revenue Slider
        monthly_revenue = st.slider(
            "• Current monthly revenue (PKR) (Expected)", 
            min_value=0, 
            max_value=1000000, 
            step=10000,
            value=50000,
            help="Move slider to set your approximate monthly revenue"
        )
        
        profit_margin = st.number_input("• Expected annual profit margin (%)", min_value=0.0, step=0.5)

        col1, col2 = st.columns(2)
        with col1: 
            st.text_input("• Who are your ideal customers *")
        with col2:
            business_location = st.text_input("• Where is your business mostly active? where's You want to do marketing *", placeholder="City, Countries")

        # Marketing Platforms (Multi-select)
        marketing_platforms = st.multiselect(
            "• Which platforms do you use for marketing?",
            ["Facebook", "Instagram", "TikTok", "LinkedIn", "YouTube", "WhatsApp", "Google Ads", "Email Marketing", "Other"]
        )

        smart_goals = st.text_area("• Business goals for this year (OPTIONAL)")
        
        st.markdown('</div>', unsafe_allow_html=True)

        # Section 4: Online Marketing
        
        st.subheader("Socials Url Marketing")

        col1, col2 = st.columns(2)
        with col1:
            facebook_page = st.text_input("Facebook Page URL")
            instagram = st.text_input("Instagram Account")
        with col2:
            website = st.text_input("Website")

        # Selectbox for visitors
        monthly_visitors = st.selectbox(
            "• Monthly website visitors (OPTIONAL)", 
            ["Select", "Under 1k", "1k-5k", "5k-20k", "20k+", "Not Sure"]
        )

        col3, col4 = st.columns(2)
        with col3:
            traffic_source = st.text_area("• Website traffic sources? (Optional)")
        with col4:
            running_ads = st.selectbox("• Are you running any marketing campaigns or ads?", ["Select", "Yes", "No"])

        col5, col6 = st.columns(2)
        with col5:
            # Budget as selectbox
            ad_budget = st.selectbox("• Current budget for marketing/ads", ["Select", "Low (Under 10k PKR)", "Normal (10k-50k PKR)", "High (50k+ PKR)"])
        with col6:
            other_campaigns = st.text_area("• Other ongoing marketing campaigns (optional)")

        col7, col8 = st.columns(2)
        with col7:
            marketing_software = st.text_area("• Marketing software in use (optional)")
        with col8:
            using_software = st.selectbox("• Are you using any marketing software?", ["Select", "Yes", "No"])

        
        
        st.markdown('</div>', unsafe_allow_html=True)

        # Submit Button
        submitted = st.form_submit_button(" SUBMIT")

        # Form Processing
        if submitted:
            # Validation
            required_fields = [full_name, last_name, phone_number, business_description, problem_solved, unique_selling_point, business_location]
            if not all(required_fields):
                st.error("❌ Please fill in all required fields marked with *")
            else:
                # Prepare form data
                form_data = {
                    'country': country,
                    'full_name': full_name,
                    'last_name': last_name,
                    'phone_number': phone_number,
                    'reference': reference,
                    'business_description': business_description,
                    'problem_solved': problem_solved,
                    'unique_selling_point': unique_selling_point,
                    'customer_results': customer_results,
                    'main_competitors': main_competitors,
                    'sales_channels': sales_channels,
                    'monthly_revenue': monthly_revenue,
                    'profit_margin': profit_margin,
                    'business_location': business_location,
                    'marketing_platforms': marketing_platforms,
                    'smart_goals': smart_goals,
                    'facebook_page': facebook_page,
                    'instagram': instagram,
                    'website': website,
                    'monthly_visitors': monthly_visitors,
                    'traffic_source': traffic_source,
                    'running_ads': running_ads,
                    'ad_budget': ad_budget,
                    'other_campaigns': other_campaigns,
                    'marketing_software': marketing_software,
                    'using_software': using_software,
                }

                with st.spinner("Our Agent is crafting your premium proposal..."):
                    try:
                        #
                        # Generate proposal
                        proposal = agent.generate_proposal(form_data)
                        
                        # Get recommended plan
                        analysis = agent.analyze_client_needs(form_data)
                        recommended_plan = analysis["recommended_plan"]
                        
                        # Save to file
                        
                        filename = save_client_data(form_data, proposal)

                        # ✅ ADD THIS LINE TO SAVE IN SUPABASE
                        success, result = save_to_supabase(form_data, proposal)

                        if success:
                            st.success(" Your proposal and details were saved in our system.")
                        else:
                            st.warning("⚠️ Proposal saved but failed to send data to database.")

                        # Display clean proposal text in container
                        st.markdown(f"""
                        <div class="proposal-container">
                            <div style="font-size: 16px; line-height: 1.6;">
                                {proposal}
                            </div>
                            <div style="margin-top: 1rem; font-size: 0.9rem; color: #ccc;">
                                : Thanks You :
                            </div>
                        </div>
                        """, unsafe_allow_html=True)

                        # Display plans with recommended highlighted
                        st.markdown('<div class="plans-container">', unsafe_allow_html=True)
                        
                        recommended_plan_info = ZAPPS_KNOWLEDGE_BASE["pricing_plans"][recommended_plan]
                        plan_html = agent.create_plan_card(recommended_plan_info, country, is_recommended=True)
                        st.markdown('<div class="plans-container style="margin-top: -40px;">', unsafe_allow_html=True)
                        st.markdown(plan_html , unsafe_allow_html=True)
                        st.markdown('</div>', unsafe_allow_html=True)
                        st.markdown('</div>', unsafe_allow_html=True)
                        st.markdown('</div>', unsafe_allow_html=True)
                        st.markdown('</div>', unsafe_allow_html=True)
                        

                    except Exception:
                        # Fallback if AI fails
                        st.markdown(f"""
                        <div class="proposal-container">
                            <div style="font-size: 16px; line-height: 1.6;">
                                Thank you {full_name} for your interest in growing your business. We appreciate you taking the time to share your business details with us. Based on your information, we see great potential for growth and would love to discuss how we can help you achieve your marketing goals. Our team will review your requirements and get back to you with personalized recommendations within 24 hours.
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                st.markdown("""
    <div style="margin-top: 30px; text-align: center;">
        <a href="https://wa.me/923702669133" target="_blank" style="background-color: #25D366; color: white; padding: 12px 25px; text-decoration: none; border-radius: 6px; font-size: 16px; margin-right: 10px;">
            📞 Chat on WhatsApp
        </a>
        <a href="https://calendly.com/zappsconsulting-info/marketing-consulting-booking" style="background-color: #D44638; color: white; padding: 12px 25px; text-decoration: none; border-radius: 6px; font-size: 16px;">
            ✉️ Meeting
        </a>
    </div>
""", unsafe_allow_html=True)
                        
    st.markdown("""Powwered By ZAPPS Consulting """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
