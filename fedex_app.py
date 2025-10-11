# =============================================================================
#  Filename: fedex_app.py
#
#  Short Description: Unified FedEx shipping application with beautiful Streamlit UI
#
#  Creation date: 2025-10-10
#  Author: Shrinivas Deshpande
# =============================================================================

"""
Unified FedEx Shipping Application

A streamlined shipping rate application using a single unified agent
with multiple specialized tools for comprehensive shipping recommendations.

Features:
- Single agent architecture (simplified)
- Zone lookup with typo correction
- SQL generation and execution
- Chain-of-thought reflection
- Supervisor escalation
- Performance tracking
- Beautiful modern UI with calendar widget
"""

import streamlit as st
import pandas as pd
import time
from datetime import datetime, date
from typing import Dict, Any
from loguru import logger

from agents.unified_agent import UnifiedFedExAgent
from agents.state import create_initial_state
from Vanna.config import VannaConfig


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
        st.error(f"Initialization failed: {e}")
        st.stop()


def render_chat_message(msg: Dict[str, Any]):
    """Render a chat message with all components."""
    with st.chat_message(msg["role"]):
        # Main message content
        st.markdown(msg["content"])
        
        # Recommendation details
        if "recommendation" in msg and msg["recommendation"]:
            rec = msg["recommendation"]
            if rec.get('service') != 'N/A':
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Service", rec.get('service', 'N/A'))
                with col2:
                    st.metric("Cost", f"${rec.get('estimated_cost', 0):.2f}")
                with col3:
                    st.metric("Delivery", rec.get('delivery_time', 'N/A'))
        
        # Reflection with Chain-of-Thought
        if "reflection" in msg and msg["reflection"]:
            with st.expander("🤔 Agent Reflection", expanded=False):
                # Show chain-of-thought if available
                if "chain_of_thought" in msg and msg["chain_of_thought"]:
                    st.markdown("### 🧠 Chain of Thought (Reasoning Process)")
                    st.markdown(
                        f'<div class="chain-of-thought-box" style="background-color: #f0f8ff; '
                        f'padding: 15px; border-left: 4px solid #4CAF50; margin-bottom: 15px;">'
                        f'{msg["chain_of_thought"]}'
                        f'</div>',
                        unsafe_allow_html=True
                    )
                    st.markdown("---")
                    st.markdown("### ✅ Final Reflection")
                
                # Show final reflection
                st.markdown(
                    f'<div class="reflection-box">{msg["reflection"]}</div>',
                    unsafe_allow_html=True
                )
        
        # SQL Query
        if "sql" in msg and msg["sql"]:
            with st.expander("🧠 Generated SQL", expanded=False):
                st.code(msg["sql"], language="sql")
        
        # Rate Data
        if "data" in msg and msg["data"]:
            with st.expander("📊 Rate Data", expanded=False):
                df = pd.DataFrame(msg["data"])
                st.dataframe(df, use_container_width=True)
                
                # Download button with unique key
                csv = df.to_csv(index=False)
                # Use message index as unique key
                msg_idx = st.session_state.messages.index(msg) if msg in st.session_state.messages else 0
                st.download_button(
                    label="📥 Download CSV",
                    data=csv,
                    file_name="fedex_rates.csv",
                    mime="text/csv",
                    key=f"download_csv_{msg_idx}"
                )
        
        # Supervisor Decision
        if "supervisor" in msg and msg["supervisor"]:
            st.markdown(
                f'<div class="supervisor-message">'
                f'<h4>👔 Supervisor Review</h4>'
                f'<p>{msg["supervisor"]}</p>'
                f'</div>',
                unsafe_allow_html=True
            )
        
        # Performance Metrics
        if "timing" in msg and msg["timing"]:
            timing = msg["timing"]
            total_time = msg.get("total_time", 0)
            
            with st.expander("⏱️ Performance Metrics", expanded=False):
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Total Time", f"{total_time:.0f}ms")
                with col2:
                    st.metric("Parse Time", f"{timing.get('parse_request', 0):.0f}ms")
                with col3:
                    st.metric("SQL Time", f"{timing.get('sql_query', 0):.0f}ms")


def process_user_query(user_input: str, agent: UnifiedFedExAgent) -> Dict[str, Any]:
    """Process user query using the unified agent."""
    try:
        logger.info(f"📝 Processing query: {user_input}")
        
        # Process with unified agent
        result = agent.process_request(user_input)
        
        if not result['success']:
            if result.get('needs_clarification'):
                return {
                    'success': False,
                    'clarification_message': result['clarification_message'],
                    'total_time': result['total_time']
                }
            else:
                return {
                    'success': False,
                    'error_message': result.get('error_message', 'Unknown error'),
                    'total_time': result.get('total_time', 0)
                }
        
        # Build response text
        rec = result.get('recommendation', {})
        if rec and rec.get('service') != 'N/A':
            response_text = rec.get('recommendation', 'No recommendation available.')
        else:
            response_text = "I couldn't find suitable shipping options for your request."
        
        # Add reflection if available
        if result.get('reflection'):
            response_text += f"\n\n**Agent Reflection:** {result['reflection']}"
        
        # Add supervisor decision if available
        supervisor = result.get('supervisor', {})
        if supervisor.get('final_message'):
            response_text += f"\n\n**Supervisor Review:** {supervisor['final_message']}"
        
        return {
            'success': True,
            'content': response_text,
            'recommendation': rec,
            'reflection': result.get('reflection', ''),
            'chain_of_thought': result.get('chain_of_thought', ''),
            'supervisor': supervisor.get('final_message', ''),
            'sql': result.get('sql_query', ''),
            'data': result.get('rate_results', {}).get('data', []),
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
    """Main Streamlit application with beautiful modern UI."""
    st.set_page_config(
        page_title="FedEx Shipping Assistant",
        page_icon="📦",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Enhanced Custom CSS for beautiful UI
    st.markdown("""
    <style>
    /* Main background gradient */
    .stApp {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    
    /* Chat container styling */
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        background-color: rgba(255, 255, 255, 0.95);
        border-radius: 20px;
        box-shadow: 0 10px 40px rgba(0, 0, 0, 0.1);
    }
    
    /* Header styling */
    h1 {
        color: #4B0082;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        font-weight: 700;
        text-align: center;
        margin-bottom: 0.5rem;
    }
    
    /* Subtitle styling */
    .subtitle {
        text-align: center;
        color: #666;
        font-size: 1.1rem;
        margin-bottom: 2rem;
    }
    
    /* Chain of thought box */
    .chain-of-thought-box {
        background: linear-gradient(135deg, #f0f8ff 0%, #e6f3ff 100%);
        padding: 20px;
        border-left: 5px solid #4CAF50;
        margin-bottom: 15px;
        border-radius: 10px;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
    }
    
    /* Reflection box */
    .reflection-box {
        background: linear-gradient(135deg, #f9f9f9 0%, #f0f0f0 100%);
        padding: 20px;
        border-left: 5px solid #2196F3;
        border-radius: 10px;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
    }
    
    /* Supervisor message */
    .supervisor-message {
        background: linear-gradient(135deg, #fff3e0 0%, #ffe0b2 100%);
        padding: 20px;
        border-left: 5px solid #FF9800;
        border-radius: 10px;
        margin-top: 10px;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
    }
    
    /* Metric cards */
    .stMetric {
        background-color: #f8f9fa;
        padding: 15px;
        border-radius: 10px;
        box-shadow: 0 2px 5px rgba(0, 0, 0, 0.05);
    }
    
    /* Calendar widget */
    .calendar-widget {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 15px;
        border-radius: 15px;
        text-align: center;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
        margin-bottom: 20px;
    }
    
    .calendar-date {
        font-size: 2.5rem;
        font-weight: 700;
        margin: 10px 0;
    }
    
    .calendar-day {
        font-size: 1.2rem;
        opacity: 0.9;
    }
    
    /* Author info */
    .author-info {
        text-align: center;
        color: #666;
        font-size: 0.9rem;
        padding: 10px;
        margin-top: 20px;
        border-top: 1px solid #e0e0e0;
    }
    
    /* Chat input enhancement */
    .stChatInput {
        border-radius: 25px;
        border: 2px solid #667eea;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Sidebar with Calendar Widget
    with st.sidebar:
        # Calendar Widget
        today = datetime.now()
        st.markdown(f"""
        <div class="calendar-widget">
            <div class="calendar-day">{today.strftime('%A')}</div>
            <div class="calendar-date">{today.strftime('%d')}</div>
            <div class="calendar-day">{today.strftime('%B %Y')}</div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("### 📋 Quick Info")
        st.info("**Available Zones**: 2-8\n\n**Weight Range**: 1-150 lbs\n\n**Services**: 6 FedEx options")
        
        st.markdown("### 🎯 Example Queries")
        st.markdown("""
        - "Send 10 lbs to Denver"
        - "Cheapest for zone 5, 20 lbs"
        - "Overnight to New York"
        - "What are weight categories?"
        """)
        
        st.markdown("### ⚙️ System Status")
        try:
            config = VannaConfig()
            provider = config.llm_provider.upper()
            model = config.model
            st.success(f"✅ {provider} Active")
            st.caption(f"Model: {model}")
        except:
            st.warning("⚠️ Config not loaded")
        
        # Author info in sidebar
        st.markdown("---")
        st.markdown("""
        <div style="text-align: center; color: #666;">
            <small>
            💻 <strong>Developed by</strong><br/>
            Shrinivas Deshpande<br/>
            <em>AI-Powered Shipping Solutions</em>
            </small>
        </div>
        """, unsafe_allow_html=True)
    
    # Main content area
    st.title("📦 FedEx Shipping Assistant")
    st.markdown('<p class="subtitle">🤖 AI-Powered Rate Lookup with Intelligent Zone Mapping</p>', 
                unsafe_allow_html=True)
    
    # Initialize session state
    initialize_session_state()
    
    # Initialize agent
    if st.session_state.agent is None:
        with st.spinner("Initializing FedEx Assistant..."):
            st.session_state.agent = initialize_agent()
    
    # Display chat messages
    for msg in st.session_state.messages:
        render_chat_message(msg)
    
    # Chat input
    if prompt := st.chat_input("Ask about shipping rates, delivery options, or service comparisons..."):
        # Add user message
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Process query
        with st.chat_message("assistant"):
            with st.spinner("Processing your request..."):
                result = process_user_query(prompt, st.session_state.agent)
            
            if not result['success']:
                if 'clarification_message' in result:
                    st.markdown(result['clarification_message'])
                    # Don't save clarification messages to history
                    return
                else:
                    st.error(result['error_message'])
                    return
            
            # Display response
            st.markdown(result['content'])
            
            # Display additional components
            if result.get('recommendation') and result['recommendation'].get('service') != 'N/A':
                rec = result['recommendation']
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Service", rec.get('service', 'N/A'))
                with col2:
                    st.metric("Cost", f"${rec.get('estimated_cost', 0):.2f}")
                with col3:
                    st.metric("Delivery", rec.get('delivery_time', 'N/A'))
            
            # Show reflection with chain-of-thought
            if result.get('reflection'):
                with st.expander("🤔 Agent Reflection", expanded=False):
                    if result.get('chain_of_thought'):
                        st.markdown("### 🧠 Chain of Thought (Reasoning Process)")
                        st.markdown(
                            f'<div class="chain-of-thought-box">'
                            f'{result["chain_of_thought"]}'
                            f'</div>',
                            unsafe_allow_html=True
                        )
                        st.markdown("---")
                        st.markdown("### ✅ Final Reflection")
                    
                    st.markdown(
                        f'<div class="reflection-box">{result["reflection"]}</div>',
                        unsafe_allow_html=True
                    )
            
            # Show SQL
            if result.get('sql'):
                with st.expander("🧠 Generated SQL", expanded=False):
                    st.code(result['sql'], language="sql")
            
            # Show data
            if result.get('data'):
                with st.expander("📊 Rate Data", expanded=False):
                    df = pd.DataFrame(result['data'])
                    st.dataframe(df, use_container_width=True)
                    
                    csv = df.to_csv(index=False)
                    msg_idx = len(st.session_state.messages)
                    st.download_button(
                        label="📥 Download CSV",
                        data=csv,
                        file_name="fedex_rates.csv",
                        mime="text/csv",
                        key=f"download_csv_{msg_idx}"
                    )
            
            # Show supervisor decision
            if result.get('supervisor'):
                st.markdown(
                    f'<div class="supervisor-message">'
                    f'<h4>👔 Supervisor Review</h4>'
                    f'<p>{result["supervisor"]}</p>'
                    f'</div>',
                    unsafe_allow_html=True
                )
            
            # Show performance metrics
            if result.get('timing'):
                with st.expander("⏱️ Performance Metrics", expanded=False):
                    timing = result['timing']
                    total_time = result.get('total_time', 0)
                    
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Total Time", f"{total_time:.0f}ms")
                    with col2:
                        st.metric("Parse Time", f"{timing.get('parse_request', 0):.0f}ms")
                    with col3:
                        st.metric("SQL Time", f"{timing.get('sql_query', 0):.0f}ms")
        
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
    
    # Beautiful footer with author info
    st.markdown("---")
    st.markdown("""
    <div class="author-info">
        💻 <strong>Developed by Shrinivas Deshpande</strong> | 
        🤖 AI-Powered Shipping Solutions | 
        📅 {date} |
        🔗 <a href="https://github.com/shdeshpa/Fedex_shipping_assistant" target="_blank">GitHub</a>
    </div>
    """.format(date=datetime.now().strftime('%B %Y')), unsafe_allow_html=True)


if __name__ == "__main__":
    main()
