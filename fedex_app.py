# =============================================================================
#  Filename: fedex_app.py
#
#  Short Description: Unified FedEx shipping application with Streamlit UI
#
#  Creation date: 2025-10-10
#  Author: Asif Qamar
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
"""

import streamlit as st
import pandas as pd
import time
from typing import Dict, Any
from loguru import logger

from agents.unified_agent import UnifiedFedExAgent
from agents.state import create_initial_state


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
    """Main Streamlit application."""
    st.set_page_config(
        page_title="FedEx Shipping Assistant",
        page_icon="📦",
        layout="wide"
    )
    
    # Custom CSS
    st.markdown("""
    <style>
    .chain-of-thought-box {
        background-color: #f0f8ff;
        padding: 15px;
        border-left: 4px solid #4CAF50;
        margin-bottom: 15px;
        border-radius: 5px;
    }
    .reflection-box {
        background-color: #f9f9f9;
        padding: 15px;
        border-left: 4px solid #2196F3;
        border-radius: 5px;
    }
    .supervisor-message {
        background-color: #fff3e0;
        padding: 15px;
        border-left: 4px solid #FF9800;
        border-radius: 5px;
        margin-top: 10px;
    }
    </style>
    """, unsafe_allow_html=True)
    
    st.title("📦 FedEx Shipping Assistant")
    st.markdown("Ask me about shipping rates, delivery times, and service options!")
    
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


if __name__ == "__main__":
    main()
