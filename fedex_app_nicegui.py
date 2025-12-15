# =============================================================================
#  Filename: fedex_app_nicegui.py
#
#  Short Description: Modern FedEx shipping application with NiceGUI
#
#  Creation date: 2025-01-27
#  Author: Shrinivas Deshpande
# =============================================================================

"""
FedEx Shipping Assistant - Modern NiceGUI Application

A beautiful, intuitive shipping rate application with AI-powered recommendations.

Features:
- Modern, aesthetic UI design
- Calendar widget with current date
- Real-time chat interface
- Performance metrics
- Interactive data visualization
"""

import calendar
from datetime import datetime
from typing import Dict, Any, List
from loguru import logger

from nicegui import ui, app
import pandas as pd

from src.agents.unified_agent import UnifiedFedExAgent


class FedExNiceGUIApp:
    """FedEx Shipping Assistant using NiceGUI."""
    
    def __init__(self):
        """Initialize the NiceGUI application."""
        self.agent: UnifiedFedExAgent | None = None
        self.messages: List[Dict[str, Any]] = []
        self.initialize_agent()
    
    def initialize_agent(self) -> None:
        """Initialize the unified FedEx agent."""
        try:
            logger.info("🚀 Initializing Unified FedEx Agent")
            self.agent = UnifiedFedExAgent()
            logger.success("✅ Agent initialized successfully")
        except Exception as e:
            logger.error(f"❌ Agent initialization failed: {e}")
            raise
    
    def render_calendar(self) -> None:
        """Render calendar widget in sidebar."""
        current_date = datetime.now()
        month_cal = calendar.monthcalendar(current_date.year, current_date.month)
        month_name = current_date.strftime("%B %Y")
        
        with ui.card().classes('w-full').style('background: linear-gradient(135deg, #4B0082 0%, #8A2BE2 50%, #9370DB 100%); padding: 20px; border-radius: 15px; border: 2px solid #FFD700;'):
            ui.label(month_name).classes('text-center text-lg font-bold').style('color: #FFD700; margin-bottom: 15px;')
            
            # Calendar grid container
            with ui.element('div').classes('w-full').style('display: grid; grid-template-columns: repeat(7, 1fr); gap: 2px;'):
                # Day headers - single letters
                day_headers = ['S', 'M', 'T', 'W', 'T', 'F', 'S']
                for day in day_headers:
                    ui.label(day).classes('text-center text-xs font-bold').style(
                        'color: #FFD700; padding: 8px; background: rgba(255,215,0,0.2); border-radius: 5px;'
                    )
                
                # Calendar days
                for week in month_cal:
                    for day in week:
                        if day == 0:
                            ui.label('').style('padding: 8px;')
                        elif day == current_date.day:
                            ui.label(str(day)).classes('text-center font-bold').style(
                                'background: #FFD700; color: #4B0082; padding: 8px; border-radius: 5px;'
                            )
                        else:
                            ui.label(str(day)).classes('text-center').style(
                                'color: #FFD700; padding: 8px; background: rgba(255,255,255,0.1); border-radius: 5px;'
                            )
    
    def render_sidebar(self) -> None:
        """Render sidebar with calendar and status."""
        with ui.left_drawer(fixed=True).style('background-color: #2a2a2a; width: 300px;'):
            # Header
            with ui.column().classes('items-center p-4'):
                ui.label('📦').classes('text-4xl')
                ui.label('FedEx Assistant').classes('text-xl font-bold').style('color: #4B0082;')
                ui.label('AI-Powered Shipping').classes('text-sm').style('color: #cccccc;')
            
            ui.separator()
            
            # Calendar
            ui.label('📅 Calendar').classes('text-lg font-bold px-4 pt-2').style('color: #ffffff;')
            self.render_calendar()
            
            ui.separator()
            
            # Status
            ui.label('📊 Status').classes('text-lg font-bold px-4 pt-2').style('color: #ffffff;')
            with ui.column().classes('px-4 gap-2'):
                if self.agent:
                    config = self.agent.config
                    ui.label(f'🟢 {config.llm_provider.upper()} Active').classes('text-sm').style('color: #4CAF50;')
                    ui.label(f'💬 {len(self.messages) // 2} Queries').classes('text-sm').style('color: #2196F3;')
            
            ui.separator()
            
            # Author info
            with ui.column().classes('items-center p-4'):
                ui.label('Shrinivas Deshpande').classes('text-sm font-bold').style('color: #4B0082;')
                ui.label('© 2025').classes('text-xs').style('color: #888;')
            
            ui.separator()
            
            # Designer credit
            with ui.column().classes('items-center p-4'):
                ui.label('Designed by Shrinivas Deshpande').classes('text-sm font-bold').style('color: #FFD700;')
    
    def render_recommendation_card(self, rec: Dict[str, Any]) -> None:
        """Render shipping recommendation card."""
        with ui.card().classes('w-full').style(
            'background: linear-gradient(135deg, #4B0082 0%, #8A2BE2 50%, #9370DB 100%); '
            'padding: 25px; border-radius: 15px; border: 2px solid #FFD700; box-shadow: 0 8px 32px rgba(0,0,0,0.3);'
        ):
            with ui.row().classes('w-full justify-between items-center mb-4'):
                with ui.column():
                    ui.label('SERVICE').classes('text-xs font-bold').style('color: rgba(255,215,0,0.8); margin-bottom: 5px;')
                    ui.label(rec.get('service', 'N/A').replace('_', ' ')).classes('text-xl font-bold').style(
                        'color: #FFD700; text-shadow: 1px 1px 2px rgba(0,0,0,0.5);'
                    )
                with ui.column().classes('items-end'):
                    ui.label('TOTAL COST').classes('text-xs font-bold').style('color: rgba(255,215,0,0.8); margin-bottom: 5px;')
                    ui.label(f"${rec.get('estimated_cost', 0):.2f}").classes('text-3xl font-bold').style(
                        'color: #FFD700; text-shadow: 2px 2px 4px rgba(0,0,0,0.7);'
                    )
            
            with ui.row().classes('w-full justify-between mt-4'):
                with ui.column():
                    ui.label('DELIVERY TIME').classes('text-xs font-bold').style('color: rgba(255,215,0,0.7); margin-bottom: 3px;')
                    ui.label(rec.get('delivery_time', 'N/A')).classes('text-sm font-semibold').style(
                        'color: #FFD700; text-shadow: 1px 1px 2px rgba(0,0,0,0.5);'
                    )
                with ui.column().classes('items-end'):
                    ui.label('DELIVERY DATE').classes('text-xs font-bold').style('color: rgba(255,215,0,0.7); margin-bottom: 3px;')
                    ui.label(rec.get('delivery_date', 'N/A')).classes('text-sm font-semibold').style(
                        'color: #FFD700; text-shadow: 1px 1px 2px rgba(0,0,0,0.5);'
                    )
    
    def render_chat_message(self, msg: Dict[str, Any], container: ui.column) -> None:
        """Render a chat message."""
        role = msg.get('role', 'user')
        content = msg.get('content', '')
        
        with container:
            with ui.card().classes('w-full mb-4').style(
                'background-color: #2d2d2d; border: 1px solid #444; border-radius: 15px; padding: 15px;'
            ):
                with ui.row().classes('items-start gap-3'):
                    ui.label('👤' if role == 'user' else '🤖').classes('text-2xl')
                    ui.markdown(content).classes('flex-1').style('color: #ffffff;')
                
                # Recommendation
                if 'recommendation' in msg and msg['recommendation']:
                    rec = msg['recommendation']
                    if rec.get('service') not in ['N/A', 'Information']:
                        ui.separator()
                        self.render_recommendation_card(rec)
                
                # Reflection
                if 'reflection' in msg and msg['reflection']:
                    with ui.expansion('🤔 Agent Reflection', icon='expand_more').classes('w-full mt-2'):
                        if 'chain_of_thought' in msg and msg['chain_of_thought']:
                            ui.label('🧠 Chain of Thought').classes('font-bold text-sm mb-2').style('color: #4CAF50;')
                            with ui.card().style('background-color: #f0f8ff; border-left: 4px solid #4CAF50; padding: 15px; margin-bottom: 15px;'):
                                ui.markdown(msg['chain_of_thought']).style('color: #000;')
                            ui.separator()
                            ui.label('✅ Final Reflection').classes('font-bold text-sm mb-2').style('color: #2196F3;')
                        with ui.card().style('background-color: #f9f9f9; border-left: 4px solid #2196F3; padding: 15px;'):
                            ui.markdown(msg['reflection']).style('color: #000;')
                
                # SQL Query
                if 'sql' in msg and msg['sql']:
                    with ui.expansion('💾 Generated SQL', icon='expand_more').classes('w-full mt-2'):
                        ui.code(msg['sql'], language='sql').classes('w-full')
                
                # Rate Data
                if 'data' in msg and msg['data']:
                    with ui.expansion('📊 Rate Data', icon='expand_more').classes('w-full mt-2'):
                        df = pd.DataFrame(msg['data'])
                        # Create table with proper columns
                        columns = [{'name': col, 'label': col, 'field': col} for col in df.columns]
                        rows = df.to_dict('records')
                        # Add index as id for row_key
                        for i, row in enumerate(rows):
                            row['id'] = i
                        ui.table(columns=columns, rows=rows, row_key='id').classes('w-full')
                        
                        csv = df.to_csv(index=False)
                        filename = f"fedex_rates_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
                        ui.button('📥 Download CSV', on_click=lambda: ui.download(csv.encode('utf-8'), filename=filename))
                
                # Weather Information
                if 'weather_summary' in msg and msg['weather_summary']:
                    with ui.expansion('🌤️ Weather Information', icon='expand_more').classes('w-full mt-2'):
                        ui.markdown(msg['weather_summary']).style('color: #ffffff;')
                
                # Supervisor Decision
                if 'supervisor' in msg and msg['supervisor']:
                    with ui.card().style('background-color: #fff3e0; border-left: 4px solid #FF9800; padding: 15px; margin-top: 10px;'):
                        ui.label('👔 Supervisor Review').classes('font-bold mb-2')
                        ui.markdown(msg['supervisor']).style('color: #000;')
                
                # Performance Metrics
                if 'timing' in msg and msg['timing']:
                    with ui.expansion('⏱️ Performance Metrics', icon='expand_more').classes('w-full mt-2'):
                        timing = msg['timing']
                        total_time = msg.get('total_time', 0)
                        with ui.row().classes('w-full gap-4'):
                            with ui.column():
                                ui.label('Total').classes('text-xs').style('color: #cccccc;')
                                ui.label(f'{total_time:.0f}ms').classes('text-lg font-semibold').style('color: #ffffff;')
                            with ui.column():
                                ui.label('Parse').classes('text-xs').style('color: #cccccc;')
                                ui.label(f"{timing.get('parse_request', 0):.0f}ms").classes('text-lg font-semibold').style('color: #ffffff;')
                            with ui.column():
                                ui.label('SQL').classes('text-xs').style('color: #cccccc;')
                                ui.label(f"{timing.get('sql_query', 0):.0f}ms").classes('text-lg font-semibold').style('color: #ffffff;')
                            with ui.column():
                                ui.label('Recommend').classes('text-xs').style('color: #cccccc;')
                                ui.label(f"{timing.get('generate_recommendation', 0):.0f}ms").classes('text-lg font-semibold').style('color: #ffffff;')
    
    def process_user_query(self, user_input: str) -> Dict[str, Any]:
        """Process user query using the unified agent."""
        try:
            logger.info(f"📝 Processing query: {user_input}")
            
            result = self.agent.process_request(user_input)
            
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
    
    def create_ui(self) -> None:
        """Create the main UI."""
        # Custom CSS
        ui.add_head_html('''
            <style>
                body {
                    background-color: #1e1e1e;
                    color: #ffffff;
                }
                .nicegui-content {
                    background-color: #1e1e1e;
                }
            </style>
        ''')
        
        # Render sidebar
        self.render_sidebar()
        
        # Main header
        with ui.header().classes('bg-gradient-to-r from-purple-600 to-purple-800 text-white p-6'):
            with ui.column().classes('items-center w-full'):
                ui.label('📦 FedEx Shipping Assistant').classes('text-4xl font-bold')
                ui.label('Get instant shipping rates with AI-powered recommendations').classes('text-lg mt-2')
        
        # Main content
        with ui.column().classes('w-full max-w-6xl mx-auto p-6 gap-4'):
            # Quick tips
            with ui.expansion('💡 Quick Tips', icon='expand_more').classes('w-full'):
                with ui.row().classes('w-full gap-4'):
                    with ui.column().classes('flex-1'):
                        ui.label('Example Queries:').classes('font-bold mb-2')
                        ui.markdown('''
                        - "What is the cheapest rate for 10 lbs to New York?"
                        - "Send 5 lbs package from SF to Denver, budget $100"
                        - "Compare all services for Zone 5, 20 lbs"
                        - "What are different weight categories?"
                        ''')
                    with ui.column().classes('flex-1'):
                        ui.label('Features:').classes('font-bold mb-2')
                        ui.markdown('''
                        - 🎯 Intelligent zone lookup
                        - 💰 Budget-aware recommendations
                        - ⚡ Real-time rate comparison
                        - 🤔 Reflection & verification
                        ''')
            
            # Chat messages container
            self.messages_container = ui.column().classes('w-full gap-4')
            
            # Chat input
            with ui.row().classes('w-full items-end gap-2 sticky bottom-0 bg-[#1e1e1e] p-4'):
                self.chat_input = ui.input(
                    placeholder='💬 Ask about shipping rates, delivery times, or service comparisons...'
                ).classes('flex-1').style('background-color: #2d2d2d; color: #ffffff;')
                
                async def send_message():
                    user_input = self.chat_input.value
                    if not user_input.strip():
                        return
                    
                    # Clear input
                    self.chat_input.value = ''
                    
                    # Add user message
                    user_msg = {'role': 'user', 'content': user_input}
                    self.messages.append(user_msg)
                    self.render_chat_message(user_msg, self.messages_container)
                    
                    # Process query
                    result = self.process_user_query(user_input)
                    
                    # Add assistant message
                    if not result['success']:
                        if 'clarification_message' in result:
                            assistant_msg = {
                                'role': 'assistant',
                                'content': result['clarification_message']
                            }
                        else:
                            assistant_msg = {
                                'role': 'assistant',
                                'content': f"❌ {result['error_message']}"
                            }
                    else:
                        assistant_msg = {
                            'role': 'assistant',
                            'content': result['content'],
                            'recommendation': result.get('recommendation', {}),
                            'reflection': result.get('reflection', ''),
                            'chain_of_thought': result.get('chain_of_thought', ''),
                            'sql': result.get('sql', ''),
                            'data': result.get('data', []),
                            'supervisor': result.get('supervisor', ''),
                            'timing': result.get('timing', {}),
                            'total_time': result.get('total_time', 0),
                            'weather_summary': result.get('weather_summary', '')
                        }
                    
                    self.messages.append(assistant_msg)
                    self.render_chat_message(assistant_msg, self.messages_container)
                
                send_btn = ui.button('Send', icon='send', on_click=send_message).classes('bg-purple-600 hover:bg-purple-700')
                
                # Allow Enter key to send
                self.chat_input.on('keydown.enter', send_message)


# Initialize app and create UI
try:
    app_instance = FedExNiceGUIApp()
    app_instance.create_ui()
except Exception as e:
    logger.error(f"❌ Failed to initialize application: {e}")
    raise

# Run the app
if __name__ in {"__main__", "__mp_main__"}:
    import sys
    # Allow port to be specified via command line: python fedex_app_nicegui.py --port 8081
    port = 8082  # Default port
    if '--port' in sys.argv:
        port_index = sys.argv.index('--port')
        if port_index + 1 < len(sys.argv):
            try:
                port = int(sys.argv[port_index + 1])
            except ValueError:
                logger.warning(f"Invalid port number, using default {port}")
    ui.run(port=port, title='FedEx Shipping Assistant', dark=True)

