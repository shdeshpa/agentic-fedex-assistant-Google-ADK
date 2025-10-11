# =============================================================================
#  Filename: fedex_app.py
#
#  Short Description: Modern FedEx shipping application with beautiful UI
#
#  Creation date: 2025-10-11
#  Author: Shrinivas Deshpande
# =============================================================================

"""
FedEx Shipping Assistant - Modern Streamlit Application

A beautiful, intuitive shipping rate application with AI-powered recommendations.

Features:
- Modern, aesthetic UI design
- Calendar widget with current date
- Real-time chat interface
- Performance metrics
- Interactive data visualization
"""

import streamlit as st
import pandas as pd
import time
from datetime import datetime
from typing import Dict, Any
from loguru import logger

from src.agents.unified_agent import UnifiedFedExAgent
from src.agents.state import create_initial_state


def initialize_session_state():
    """Initialize Streamlit session state."""
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    if 'agent' not in st.session_state:
        st.session_state.agent = None


def initialize_agent() -> UnifiedFedExAgent:
    """Initialize the unified FedEx agent."""
    try:
        logger.info("🚀 Initializing Unified FedEx Agent")
        agent = UnifiedFedExAgent()
        logger.success("✅ Agent initialized successfully")
        return agent
    except Exception as e:
        logger.error(f"❌ Agent initialization failed: {e}")
        st.error(f"⚠️ Initialization failed: {e}")
        st.info("💡 **Troubleshooting:**\n"
                "1. Check that Qdrant is running on port 6333\n"
                "2. Verify your API key in .env file\n"
                "3. Ensure fedex_rates.db exists")
        st.stop()


def render_sidebar():
    """Render clean sidebar with calendar and minimal info."""
    with st.sidebar:
        # Simple header without borders
        st.markdown("""
        <div style='text-align: center; padding: 10px 0; margin-bottom: 10px;'>
            <div style='color: #333; font-size: 24px; margin: 0;'>🚀</div>
            <div style='color: #333; margin: 3px 0; font-size: 18px; font-weight: bold;'>FedEx Assistant</div>
            <div style='color: #666; font-size: 12px; margin: 0;'>AI-Powered Shipping</div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Simple Today's Date Display
        st.markdown("### 📅 Today's Date")
        current_date = datetime.now()
        
        # Simple, clean date display without borders
        st.markdown(f"""
        <div style='padding: 10px; margin: 8px 0; text-align: center;'>
            
            <div style='color: #333; font-size: 24px; font-weight: bold; margin: 0;'>
                {current_date.strftime("%d")}
            </div>
            
            <div style='color: #666; font-size: 14px; font-weight: 500; margin: 3px 0;'>
                {current_date.strftime("%B %Y")}
            </div>
            
            <div style='color: #888; font-size: 12px; margin: 0;'>
                {current_date.strftime("%A")}
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Quick Stats
        st.markdown("### 📊 Status")
        if st.session_state.get('agent'):
            config = st.session_state.agent.config
            st.success(f"🟢 {config.llm_provider.upper()} Active")
            st.info(f"💬 {len(st.session_state.messages) // 2} Queries")
        
        st.markdown("---")
        
        # Author Info - Simple without borders
        st.markdown("""
        <div style='text-align: center; padding: 8px 0; margin-top: 10px;'>
            <div style='color: #333; font-weight: bold; font-size: 11px; margin: 0;'>
                Shrinivas Deshpande
            </div>
            <div style='color: #666; font-size: 9px; margin: 2px 0 0 0;'>
                © 2025
            </div>
        </div>
        """, unsafe_allow_html=True)


def render_chat_message(msg: Dict[str, Any]):
    """Render a chat message with beautiful styling."""
    with st.chat_message(msg["role"], avatar="👤" if msg["role"] == "user" else "🤖"):
        # Main message content
        st.markdown(msg["content"])
        
        # Professional shipping details with improved rendering
        if "recommendation" in msg and msg["recommendation"]:
            rec = msg["recommendation"]
            if rec.get('service') != 'N/A' and rec.get('service') != 'Information':
                st.markdown("### 📦 Shipping Recommendation")
                
                # Clean shipping recommendation without borders
                st.markdown(f"""
                <div style='padding: 15px 0; margin: 10px 0;'>
                    
                    <div style='display: flex; justify-content: space-between; margin-bottom: 10px;'>
                        <div>
                            <div style='color: #666; font-size: 11px; margin-bottom: 2px; font-weight: bold;'>SERVICE</div>
                            <div style='color: #333; font-size: 16px; font-weight: 600;'>
                                {rec.get('service', 'N/A').replace('_', ' ')}
                            </div>
                        </div>
                        <div style='text-align: right;'>
                            <div style='color: #666; font-size: 11px; margin-bottom: 2px; font-weight: bold;'>TOTAL COST</div>
                            <div style='color: #2E8B57; font-size: 20px; font-weight: 700;'>
                                ${rec.get('estimated_cost', 0):.2f}
                            </div>
                        </div>
                    </div>
                    
                    <div style='display: flex; justify-content: space-between;'>
                        <div>
                            <div style='color: #666; font-size: 11px; margin-bottom: 2px; font-weight: bold;'>DELIVERY TIME</div>
                            <div style='color: #333; font-size: 13px; font-weight: 500;'>
                                {rec.get('delivery_time', 'N/A')}
                            </div>
                        </div>
                        <div style='text-align: right;'>
                            <div style='color: #666; font-size: 11px; margin-bottom: 2px; font-weight: bold;'>DELIVERY DATE</div>
                            <div style='color: #333; font-size: 13px; font-weight: 500;'>
                                {rec.get('delivery_date', 'N/A')}
                            </div>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        
        # Reflection with Chain-of-Thought
        if "reflection" in msg and msg["reflection"]:
            with st.expander("🤔 Agent Reflection", expanded=False):
                if "chain_of_thought" in msg and msg["chain_of_thought"]:
                    st.markdown("#### 🧠 Chain of Thought")
                    st.markdown(
                        f'<div style="background-color: #f0f8ff; padding: 15px; '
                        f'border-left: 4px solid #4CAF50; border-radius: 5px; margin-bottom: 15px;">'
                        f'{msg["chain_of_thought"]}'
                        f'</div>',
                        unsafe_allow_html=True
                    )
                    st.markdown("---")
                    st.markdown("#### ✅ Final Reflection")
                
                st.markdown(
                    f'<div style="background-color: #f9f9f9; padding: 15px; '
                    f'border-left: 4px solid #2196F3; border-radius: 5px;">'
                    f'{msg["reflection"]}'
                    f'</div>',
                    unsafe_allow_html=True
                )
        
        # SQL Query
        if "sql" in msg and msg["sql"]:
            with st.expander("💾 Generated SQL", expanded=False):
                st.code(msg["sql"], language="sql")
        
        # Rate Data
        if "data" in msg and msg["data"]:
            with st.expander("📊 Rate Data", expanded=False):
                df = pd.DataFrame(msg["data"])
                st.dataframe(df, use_container_width=True, height=300)
                
                csv = df.to_csv(index=False)
                msg_idx = st.session_state.messages.index(msg) if msg in st.session_state.messages else 0
                st.download_button(
                    label="📥 Download CSV",
                    data=csv,
                    file_name=f"fedex_rates_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv",
                    key=f"download_csv_{msg_idx}"
                )
        
        # Weather Information
        if "weather_summary" in msg and msg["weather_summary"]:
            with st.expander("🌤️ Weather Information", expanded=False):
                st.markdown(msg["weather_summary"])
        
        # Supervisor Decision
        if "supervisor" in msg and msg["supervisor"]:
            st.markdown(
                f'<div style="background-color: #fff3e0; padding: 15px; '
                f'border-left: 4px solid #FF9800; border-radius: 5px; margin-top: 10px;">'
                f'<h4 style="margin-top: 0;">👔 Supervisor Review</h4>'
                f'<p>{msg["supervisor"]}</p>'
                f'</div>',
                unsafe_allow_html=True
            )
        
        # Performance Metrics
        if "timing" in msg and msg["timing"]:
            with st.expander("⏱️ Performance Metrics", expanded=False):
                timing = msg["timing"]
                total_time = msg.get("total_time", 0)
                
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Total", f"{total_time:.0f}ms")
                with col2:
                    st.metric("Parse", f"{timing.get('parse_request', 0):.0f}ms")
                with col3:
                    st.metric("SQL", f"{timing.get('sql_query', 0):.0f}ms")
                with col4:
                    st.metric("Recommend", f"{timing.get('generate_recommendation', 0):.0f}ms")


def process_user_query(user_input: str, agent: UnifiedFedExAgent) -> Dict[str, Any]:
    """Process user query using the unified agent."""
    try:
        logger.info(f"📝 Processing query: {user_input}")
        
        result = agent.process_request(user_input)
        
        if not result['success']:
            if result.get('needs_clarification'):
                return {
                    'success': False,
                    'clarification_message': result['clarification_message'],
                    'total_time': result.get('total_time', 0)
                }
            else:
                return {
                    'success': False,
                    'error_message': result.get('error_message', 'Unknown error'),
                    'total_time': result.get('total_time', 0)
                }
        
        # Build response text
        rec = result.get('recommendation', {})
        if rec and rec.get('service') not in ['N/A', 'Information']:
            response_text = rec.get('recommendation', 'No recommendation available.')
        elif rec and rec.get('service') == 'Information':
            response_text = rec.get('recommendation', 'Information query processed.')
        else:
            response_text = "I couldn't find suitable shipping options for your request."
        
        if result.get('reflection'):
            response_text += f"\n\n**💭 Agent Reflection:** {result['reflection']}"
        
        supervisor = result.get('supervisor', {})
        if supervisor.get('final_message'):
            response_text += f"\n\n**👔 Supervisor Review:** {supervisor['final_message']}"
        
        # Add weather information to response if available
        if result.get('weather_summary'):
            response_text += f"\n\n**🌤️ Weather Information:**\n{result['weather_summary']}"
        
        return {
            'success': True,
            'content': response_text,
            'recommendation': rec,
            'reflection': result.get('reflection', ''),
            'chain_of_thought': result.get('chain_of_thought', ''),
            'supervisor': supervisor.get('final_message', ''),
            'sql': result.get('sql_query', ''),
            'data': result.get('rate_results', {}).get('data', []),
            'weather_summary': result.get('weather_summary', ''),
            'weather_info': result.get('weather_info', {}),
            'timing': result.get('timing', {}),
            'total_time': result.get('total_time', 0)
        }
        
    except Exception as e:
        logger.error(f"❌ Query processing error: {e}")
        return {
            'success': False,
            'error_message': f"Error processing query: {str(e)}",
            'total_time': 0
        }


def main():
    """Main Streamlit application with modern UI."""
    # Page configuration
    st.set_page_config(
        page_title="FedEx Shipping Assistant",
        page_icon="📦",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Custom CSS for modern dark theme
    st.markdown("""
    <style>
    /* Dark theme colors */
    :root {
        --primary-color: #4B0082;
        --secondary-color: #667eea;
        --accent-color: #764ba2;
        --dark-bg: #1e1e1e;
        --card-bg: #2d2d2d;
        --text-primary: #ffffff;
        --text-secondary: #cccccc;
    }
    
    /* Main app background */
    .main .block-container {
        background-color: var(--dark-bg);
        color: var(--text-primary);
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Custom header styling */
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 30px;
        border-radius: 15px;
        text-align: center;
        margin-bottom: 30px;
        box-shadow: 0 8px 16px rgba(0,0,0,0.3);
    }
    
    .main-header h1 {
        color: white;
        margin: 0;
        font-size: 42px;
        font-weight: 700;
    }
    
    .main-header p {
        color: rgba(255,255,255,0.9);
        margin: 10px 0 0 0;
        font-size: 18px;
    }
    
    /* Chat message styling - dark theme */
    .stChatMessage {
        background-color: var(--card-bg);
        border-radius: 15px;
        padding: 15px;
        margin: 10px 0;
        color: var(--text-primary);
        border: 1px solid #444;
    }
    
    /* Chat input styling */
    .stChatInputContainer {
        border-top: 2px solid #667eea;
        padding-top: 20px;
        background-color: var(--dark-bg);
    }
    
    /* Metric cards - dark theme */
    [data-testid="stMetricValue"] {
        font-size: 24px;
        font-weight: 600;
        color: var(--text-primary);
    }
    
    [data-testid="stMetricLabel"] {
        color: var(--text-secondary);
    }
    
    /* Expander styling - dark theme */
    .streamlit-expanderHeader {
        background-color: var(--card-bg);
        border-radius: 8px;
        font-weight: 600;
        color: var(--text-primary);
        border: 1px solid #444;
    }
    
    .streamlit-expanderContent {
        background-color: var(--dark-bg);
        color: var(--text-primary);
    }
    
    /* Button styling */
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 10px 24px;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(102,126,234,0.4);
    }
    
    /* Sidebar styling - dark theme */
    [data-testid="stSidebar"] {
        background-color: #2a2a2a;
    }
    
    [data-testid="stSidebar"] .stMarkdown {
        color: var(--text-primary);
    }
    
    /* Dataframe styling - dark theme */
    .stDataFrame {
        background-color: var(--card-bg);
        border: 1px solid #444;
    }
    
    /* Code block styling - dark theme */
    .stCode {
        background-color: #1a1a1a;
        border: 1px solid #444;
    }
    
    /* Info boxes - dark theme */
    .info-box {
        background-color: #1a237e;
        padding: 15px;
        border-left: 4px solid #2196F3;
        border-radius: 5px;
        margin: 10px 0;
        color: white;
    }
    
    .success-box {
        background-color: #1b5e20;
        padding: 15px;
        border-left: 4px solid #4CAF50;
        border-radius: 5px;
        margin: 10px 0;
        color: white;
    }
    
    .warning-box {
        background-color: #e65100;
        padding: 15px;
        border-left: 4px solid #FF9800;
        border-radius: 5px;
        margin: 10px 0;
        color: white;
    }
    
    /* Text elements - dark theme */
    .stMarkdown {
        color: var(--text-primary);
    }
    
    .stText {
        color: var(--text-primary);
    }
    
    /* Selectbox and input styling */
    .stSelectbox > div > div {
        background-color: var(--card-bg);
        color: var(--text-primary);
        border: 1px solid #444;
    }
    
    .stTextInput > div > div > input {
        background-color: var(--card-bg);
        color: var(--text-primary);
        border: 1px solid #444;
    }
    
    /* Calendar widget styling */
    .calendar-container {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 20px;
        border-radius: 15px;
        text-align: center;
        box-shadow: 0 4px 6px rgba(0,0,0,0.3);
        margin: 10px 0;
    }
    
    .calendar-month {
        color: rgba(255,255,255,0.9);
        font-size: 16px;
        margin: 5px 0;
    }
    
    .calendar-dates {
        display: grid;
        grid-template-columns: repeat(7, 1fr);
        gap: 5px;
        margin-top: 10px;
    }
    
    .calendar-date {
        padding: 8px;
        border-radius: 5px;
        color: rgba(255,255,255,0.8);
        font-size: 12px;
    }
    
    .calendar-date.today {
        background-color: rgba(255,255,255,0.3);
        color: white;
        font-weight: bold;
    }
    
    .calendar-date.other-month {
        color: rgba(255,255,255,0.4);
    }
    
    /* Author info styling */
    .author-info {
        background: linear-gradient(135deg, #4B0082 0%, #6A5ACD 100%);
        padding: 15px;
        border-radius: 10px;
        text-align: center;
        margin-top: 20px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.2);
    }
    
    .author-info h4 {
        color: white;
        margin: 0 0 5px 0;
        font-size: 16px;
    }
    
    .author-info p {
        color: rgba(255,255,255,0.8);
        margin: 0;
        font-size: 12px;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Render sidebar
    render_sidebar()
    
    # Main header
    st.markdown("""
    <div class='main-header'>
        <h1>📦 FedEx Shipping Assistant</h1>
        <p>Get instant shipping rates with AI-powered recommendations</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Initialize session state
    initialize_session_state()
    
    # Initialize agent
    if st.session_state.agent is None:
        with st.spinner("🚀 Initializing AI Assistant..."):
            st.session_state.agent = initialize_agent()
            st.success("✅ AI Assistant ready!")
            time.sleep(0.5)
            st.rerun()
    
    # Quick tips
    with st.expander("💡 Quick Tips", expanded=False):
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("""
            **Example Queries:**
            - "What is the cheapest rate for 10 lbs to New York?"
            - "Send 5 lbs package from SF to Denver, budget $100"
            - "Compare all services for Zone 5, 20 lbs"
            - "What are different weight categories?"
            """)
        with col2:
            st.markdown("""
            **Features:**
            - 🎯 Intelligent zone lookup
            - 💰 Budget-aware recommendations
            - ⚡ Real-time rate comparison
            - 🤔 Reflection & verification
            """)
    
    # Display chat messages
    for msg in st.session_state.messages:
        render_chat_message(msg)
    
    # Chat input with modern placeholder
    if prompt := st.chat_input("💬 Ask about shipping rates, delivery times, or service comparisons..."):
        # Add user message
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user", avatar="👤"):
            st.markdown(prompt)
        
        # Process query
        with st.chat_message("assistant", avatar="🤖"):
            with st.spinner("🔍 Analyzing your request..."):
                result = process_user_query(prompt, st.session_state.agent)
            
            if not result['success']:
                if 'clarification_message' in result:
                    st.markdown(
                        f'<div class="info-box">{result["clarification_message"]}</div>',
                        unsafe_allow_html=True
                    )
                    return
                else:
                    st.error(f"❌ {result['error_message']}")
                    return
            
            # Display response
            st.markdown(result['content'])
            
            # Display professional shipping recommendation
            if result.get('recommendation') and result['recommendation'].get('service') not in ['N/A', 'Information']:
                rec = result['recommendation']
                
                st.markdown("### 📦 Shipping Recommendation")
                
                # Clean shipping recommendation without borders
                st.markdown(f"""
                <div style='padding: 15px 0; margin: 10px 0;'>
                    
                    <div style='display: flex; justify-content: space-between; margin-bottom: 10px;'>
                        <div>
                            <div style='color: #666; font-size: 11px; margin-bottom: 2px; font-weight: bold;'>SERVICE</div>
                            <div style='color: #333; font-size: 16px; font-weight: 600;'>
                                {rec.get('service', 'N/A').replace('_', ' ')}
                            </div>
                        </div>
                        <div style='text-align: right;'>
                            <div style='color: #666; font-size: 11px; margin-bottom: 2px; font-weight: bold;'>TOTAL COST</div>
                            <div style='color: #2E8B57; font-size: 20px; font-weight: 700;'>
                                ${rec.get('estimated_cost', 0):.2f}
                            </div>
                        </div>
                    </div>
                    
                    <div style='display: flex; justify-content: space-between;'>
                        <div>
                            <div style='color: #666; font-size: 11px; margin-bottom: 2px; font-weight: bold;'>DELIVERY TIME</div>
                            <div style='color: #333; font-size: 13px; font-weight: 500;'>
                                {rec.get('delivery_time', 'N/A')}
                            </div>
                        </div>
                        <div style='text-align: right;'>
                            <div style='color: #666; font-size: 11px; margin-bottom: 2px; font-weight: bold;'>DELIVERY DATE</div>
                            <div style='color: #333; font-size: 13px; font-weight: 500;'>
                                {rec.get('delivery_date', 'N/A')}
                            </div>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                # User confirmation with weather
                if rec.get('needs_confirmation', False):
                    st.markdown("---")
                    
                    col1, col2, col3 = st.columns([1, 2, 1])
                    with col2:
                        st.markdown("### 🤔 Proceed with this rate?")
                        
                        if st.button("✅ Yes, proceed", key=f"proceed_{len(st.session_state.messages)}"):
                            st.success("✅ Great choice! Your shipment will be processed.")
                            
                            # Show delivery date weather prominently
                            if result.get('delivery_weather') and result['delivery_weather'].get('success'):
                                delivery_weather = result['delivery_weather']['weather_info']
                                st.markdown("### 🌤️ Weather for Delivery Day")
                                st.markdown(f"""
                                <div style='padding: 15px 0; margin: 10px 0;'>
                                    
                                    <div style='display: grid; grid-template-columns: 1fr 1fr; gap: 10px; margin-bottom: 10px;'>
                                        <div>
                                            <div style='color: #666; font-size: 11px; margin-bottom: 2px; font-weight: bold;'>TEMPERATURE</div>
                                            <div style='color: #333; font-size: 16px; font-weight: 600;'>
                                                {delivery_weather['current_temp']}°F
                                            </div>
                                        </div>
                                        <div>
                                            <div style='color: #666; font-size: 11px; margin-bottom: 2px; font-weight: bold;'>CONDITIONS</div>
                                            <div style='color: #333; font-size: 13px; font-weight: 500;'>
                                                {delivery_weather['description']}
                                            </div>
                                        </div>
                                        <div>
                                            <div style='color: #666; font-size: 11px; margin-bottom: 2px; font-weight: bold;'>HUMIDITY</div>
                                            <div style='color: #333; font-size: 13px; font-weight: 500;'>
                                                {delivery_weather['humidity']}%
                                            </div>
                                        </div>
                                        <div>
                                            <div style='color: #666; font-size: 11px; margin-bottom: 2px; font-weight: bold;'>WIND SPEED</div>
                                            <div style='color: #333; font-size: 13px; font-weight: 500;'>
                                                {delivery_weather['wind_speed']} mph
                                            </div>
                                        </div>
                                    </div>
                                    
                                    <div style='background: #f8f9fa; padding: 10px; margin-top: 8px;'>
                                        <div style='color: #666; font-size: 11px; margin-bottom: 3px; font-weight: bold;'>📦 SHIPPING RECOMMENDATION</div>
                                        <div style='color: #333; font-size: 13px; font-weight: 500;'>
                                            {delivery_weather['shipping_recommendation']}
                                        </div>
                                    </div>
                                </div>
                                """, unsafe_allow_html=True)
                            else:
                                st.info("🌤️ Weather information not available for delivery date.")
                            
                        if st.button("❌ No, show other options", key=f"decline_{len(st.session_state.messages)}"):
                            st.info("Let me show you alternative shipping options...")
            
            # Show reflection
            if result.get('reflection'):
                with st.expander("🤔 Agent Reflection", expanded=False):
                    if result.get('chain_of_thought'):
                        st.markdown("#### 🧠 Chain of Thought")
                        st.markdown(
                            f'<div style="background-color: #f0f8ff; padding: 15px; '
                            f'border-left: 4px solid #4CAF50; border-radius: 5px; margin-bottom: 15px;">'
                            f'{result["chain_of_thought"]}'
                            f'</div>',
                            unsafe_allow_html=True
                        )
                        st.markdown("---")
                        st.markdown("#### ✅ Final Reflection")
                    
                    st.markdown(
                        f'<div style="background-color: #f9f9f9; padding: 15px; '
                        f'border-left: 4px solid #2196F3; border-radius: 5px;">'
                        f'{result["reflection"]}'
                        f'</div>',
                        unsafe_allow_html=True
                    )
            
            # Show SQL
            if result.get('sql'):
                with st.expander("💾 Generated SQL", expanded=False):
                    st.code(result['sql'], language="sql")
            
            # Show data
            if result.get('data'):
                with st.expander("📊 Rate Data", expanded=False):
                    df = pd.DataFrame(result['data'])
                    st.dataframe(df, use_container_width=True, height=300)
                    
                    csv = df.to_csv(index=False)
                    msg_idx = len(st.session_state.messages)
                    st.download_button(
                        label="📥 Download CSV",
                        data=csv,
                        file_name=f"fedex_rates_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                        mime="text/csv",
                        key=f"download_csv_{msg_idx}"
                    )
            
            # Show supervisor
            if result.get('supervisor'):
                st.markdown(
                    f'<div style="background-color: #fff3e0; padding: 15px; '
                    f'border-left: 4px solid #FF9800; border-radius: 5px; margin-top: 10px;">'
                    f'<h4 style="margin-top: 0;">👔 Supervisor Review</h4>'
                    f'<p>{result["supervisor"]}</p>'
                    f'</div>',
                    unsafe_allow_html=True
                )
            
            # Show performance
            if result.get('timing'):
                with st.expander("⏱️ Performance Metrics", expanded=False):
                    timing = result['timing']
                    total_time = result.get('total_time', 0)
                    
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        st.metric("Total", f"{total_time:.0f}ms")
                    with col2:
                        st.metric("Parse", f"{timing.get('parse_request', 0):.0f}ms")
                    with col3:
                        st.metric("SQL", f"{timing.get('sql_query', 0):.0f}ms")
                    with col4:
                        st.metric("Recommend", f"{timing.get('generate_recommendation', 0):.0f}ms")
        
        # Save to history
        msg_data = {
            "role": "assistant",
            "content": result['content'],
            "recommendation": result.get('recommendation', {}),
            "reflection": result.get('reflection', ''),
            "chain_of_thought": result.get('chain_of_thought', ''),
            "sql": result.get('sql', ''),
            "data": result.get('data', []),
            "supervisor": result.get('supervisor', ''),
            "timing": result.get('timing', {}),
            "total_time": result.get('total_time', 0)
        }
        st.session_state.messages.append(msg_data)


if __name__ == "__main__":
    main()
