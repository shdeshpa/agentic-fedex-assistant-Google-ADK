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
    """Render beautiful sidebar with calendar and info."""
    with st.sidebar:
        # Header with logo placeholder
        st.markdown("""
        <div style='text-align: center; padding: 20px 0;'>
            <h1 style='color: #4B0082; margin: 0;'>📦</h1>
            <h2 style='color: #4B0082; margin: 5px 0; font-size: 24px;'>FedEx Assistant</h2>
            <p style='color: #666; font-size: 14px; margin: 0;'>AI-Powered Shipping</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Calendar Widget
        st.markdown("### 📅 Today's Date")
        current_date = datetime.now()
        
        # Create a nice date display
        st.markdown(f"""
        <div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    padding: 20px; border-radius: 15px; text-align: center;
                    box-shadow: 0 4px 6px rgba(0,0,0,0.1);'>
            <div style='color: white; font-size: 48px; font-weight: bold; margin: 0;'>
                {current_date.strftime("%d")}
            </div>
            <div style='color: rgba(255,255,255,0.9); font-size: 18px; margin: 5px 0;'>
                {current_date.strftime("%B %Y")}
            </div>
            <div style='color: rgba(255,255,255,0.8); font-size: 14px;'>
                {current_date.strftime("%A")}
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Quick Stats
        st.markdown("### 📊 Quick Stats")
        if st.session_state.get('agent'):
            config = st.session_state.agent.config
            
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Provider", config.llm_provider.upper(), delta="Active")
            with col2:
                st.metric("Queries", len(st.session_state.messages) // 2)
            
            st.info(f"🤖 **Model**: {config.model}")
        
        st.markdown("---")
        
        # System Info
        st.markdown("### ⚙️ System Info")
        st.caption("🗄️ Database: fedex_rates.db")
        st.caption("🌐 Zones: 2-8")
        st.caption("⚖️ Weights: 1-150 lbs")
        st.caption("📦 Services: 6 tiers")
        
        st.markdown("---")
        
        # Author Info
        st.markdown("""
        <div style='text-align: center; padding: 10px 0; color: #666;'>
            <p style='margin: 5px 0; font-size: 12px;'>Created by</p>
            <p style='margin: 0; font-weight: bold; color: #4B0082;'>
                Shrinivas Deshpande
            </p>
            <p style='margin: 5px 0; font-size: 11px; color: #888;'>
                © 2025
            </p>
        </div>
        """, unsafe_allow_html=True)


def render_chat_message(msg: Dict[str, Any]):
    """Render a chat message with beautiful styling."""
    with st.chat_message(msg["role"], avatar="👤" if msg["role"] == "user" else "🤖"):
        # Main message content
        st.markdown(msg["content"])
        
        # Recommendation details with modern cards
        if "recommendation" in msg and msg["recommendation"]:
            rec = msg["recommendation"]
            if rec.get('service') != 'N/A' and rec.get('service') != 'Information':
                st.markdown("### 📦 Shipping Details")
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.markdown(f"""
                    <div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                                padding: 15px; border-radius: 10px; text-align: center;'>
                        <div style='color: rgba(255,255,255,0.8); font-size: 12px;'>SERVICE</div>
                        <div style='color: white; font-size: 16px; font-weight: bold; margin-top: 5px;'>
                            {rec.get('service', 'N/A').replace('_', ' ')}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col2:
                    st.markdown(f"""
                    <div style='background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
                                padding: 15px; border-radius: 10px; text-align: center;'>
                        <div style='color: rgba(255,255,255,0.8); font-size: 12px;'>COST</div>
                        <div style='color: white; font-size: 20px; font-weight: bold; margin-top: 5px;'>
                            ${rec.get('estimated_cost', 0):.2f}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col3:
                    st.markdown(f"""
                    <div style='background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
                                padding: 15px; border-radius: 10px; text-align: center;'>
                        <div style='color: rgba(255,255,255,0.8); font-size: 12px;'>DELIVERY</div>
                        <div style='color: white; font-size: 14px; font-weight: bold; margin-top: 5px;'>
                            {rec.get('delivery_time', 'N/A')}
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
    """Main Streamlit application with modern UI."""
    # Page configuration
    st.set_page_config(
        page_title="FedEx Shipping Assistant",
        page_icon="📦",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Custom CSS for modern design
    st.markdown("""
    <style>
    /* Main theme colors */
    :root {
        --primary-color: #4B0082;
        --secondary-color: #667eea;
        --accent-color: #764ba2;
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
        box-shadow: 0 8px 16px rgba(0,0,0,0.1);
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
    
    /* Chat message styling */
    .stChatMessage {
        background-color: #f8f9fa;
        border-radius: 15px;
        padding: 15px;
        margin: 10px 0;
    }
    
    /* Input styling */
    .stChatInputContainer {
        border-top: 2px solid #667eea;
        padding-top: 20px;
    }
    
    /* Metric cards */
    [data-testid="stMetricValue"] {
        font-size: 24px;
        font-weight: 600;
    }
    
    /* Expander styling */
    .streamlit-expanderHeader {
        background-color: #f0f2f6;
        border-radius: 8px;
        font-weight: 600;
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
    
    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background-color: #f8f9fa;
    }
    
    /* Info boxes */
    .info-box {
        background-color: #e3f2fd;
        padding: 15px;
        border-left: 4px solid #2196F3;
        border-radius: 5px;
        margin: 10px 0;
    }
    
    /* Success boxes */
    .success-box {
        background-color: #e8f5e9;
        padding: 15px;
        border-left: 4px solid #4CAF50;
        border-radius: 5px;
        margin: 10px 0;
    }
    
    /* Warning boxes */
    .warning-box {
        background-color: #fff3e0;
        padding: 15px;
        border-left: 4px solid #FF9800;
        border-radius: 5px;
        margin: 10px 0;
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
            
            # Display recommendation cards
            if result.get('recommendation') and result['recommendation'].get('service') not in ['N/A', 'Information']:
                rec = result['recommendation']
                
                st.markdown("### 📦 Shipping Details")
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.markdown(f"""
                    <div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                                padding: 15px; border-radius: 10px; text-align: center;'>
                        <div style='color: rgba(255,255,255,0.8); font-size: 12px;'>SERVICE</div>
                        <div style='color: white; font-size: 16px; font-weight: bold; margin-top: 5px;'>
                            {rec.get('service', 'N/A').replace('_', ' ')}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col2:
                    st.markdown(f"""
                    <div style='background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
                                padding: 15px; border-radius: 10px; text-align: center;'>
                        <div style='color: rgba(255,255,255,0.8); font-size: 12px;'>COST</div>
                        <div style='color: white; font-size: 20px; font-weight: bold; margin-top: 5px;'>
                            ${rec.get('estimated_cost', 0):.2f}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col3:
                    st.markdown(f"""
                    <div style='background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
                                padding: 15px; border-radius: 10px; text-align: center;'>
                        <div style='color: rgba(255,255,255,0.8); font-size: 12px;'>DELIVERY</div>
                        <div style='color: white; font-size: 14px; font-weight: bold; margin-top: 5px;'>
                            {rec.get('delivery_time', 'N/A')}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
            
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
