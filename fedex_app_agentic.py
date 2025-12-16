# =============================================================================
#  Filename: fedex_app_agentic.py
#
#  Short Description: Agentic AI FedEx shipping application with NiceGUI
#
#  Creation date: 2025-12-16
#  Author: Shrinivas Deshpande
# =============================================================================

"""
FedEx Shipping Assistant - Agentic AI Version

A multi-agent shipping rate application powered by Google ADK patterns
with full trajectory visibility and reflection.

Features:
- Multi-agent architecture (Supervisor, Customer, Expert)
- Real-time reasoning trajectory display
- Agent reflection and self-assessment
- FastMCP tool integration
- Session management
"""

import calendar
import uuid
from datetime import datetime
from typing import Dict, Any, List, Optional
from loguru import logger

from nicegui import ui, app
import pandas as pd

from src.agents.adk_agents import create_shipping_agent_system, AgentOrchestrator
from src.agents.session_manager import get_session_manager, SessionManager
from src.Vanna.config import VannaConfig
from src.Vanna.model_manager import create_model_manager


class AgenticFedExApp:
    """FedEx Shipping Assistant using Agentic AI architecture."""

    def __init__(self):
        """Initialize the agentic application."""
        self.orchestrator: Optional[AgentOrchestrator] = None
        self.session_manager: SessionManager = get_session_manager()
        self.vanna_manager = None
        self.messages: List[Dict[str, Any]] = []
        self.session_id: Optional[str] = None
        self.show_trajectory: bool = True
        self.initialize_agents()

    def initialize_agents(self) -> None:
        """Initialize the multi-agent system with Vanna database connection."""
        try:
            logger.info("Initializing Vanna Model Manager for database access...")

            # Initialize Vanna for database queries
            vanna_config = VannaConfig()
            self.vanna_manager = create_model_manager(vanna_config)
            vanna_client = self.vanna_manager.get_vanna_instance()

            logger.info("Initializing Multi-Agent System with Vanna integration...")
            self.orchestrator = create_shipping_agent_system(
                log_dir="./logs",
                vanna_client=vanna_client
            )
            self.session_id = self.session_manager.create_session().session_id
            logger.success("Multi-Agent System initialized with database connection")
        except Exception as e:
            logger.error(f"Agent initialization failed: {e}")
            raise

    def render_calendar(self) -> None:
        """Render calendar widget in sidebar."""
        current_date = datetime.now()
        month_cal = calendar.monthcalendar(current_date.year, current_date.month)
        month_name = current_date.strftime("%B %Y")

        with ui.card().classes('w-full').style(
            'background: linear-gradient(135deg, #4B0082 0%, #8A2BE2 50%, #9370DB 100%); '
            'padding: 20px; border-radius: 15px; border: 2px solid #FFD700;'
        ):
            ui.label(month_name).classes('text-center text-lg font-bold').style(
                'color: #FFD700; margin-bottom: 15px;'
            )

            with ui.element('div').classes('w-full').style(
                'display: grid; grid-template-columns: repeat(7, 1fr); gap: 2px;'
            ):
                day_headers = ['S', 'M', 'T', 'W', 'T', 'F', 'S']
                for day in day_headers:
                    ui.label(day).classes('text-center text-xs font-bold').style(
                        'color: #FFD700; padding: 8px; background: rgba(255,215,0,0.2); border-radius: 5px;'
                    )

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
        """Render sidebar with calendar, status, and settings."""
        with ui.left_drawer(fixed=True).style('background-color: #2a2a2a; width: 320px;'):
            # Header
            with ui.column().classes('items-center p-4'):
                ui.label('🤖').classes('text-4xl')
                ui.label('Agentic FedEx').classes('text-xl font-bold').style('color: #4B0082;')
                ui.label('Multi-Agent Shipping AI').classes('text-sm').style('color: #cccccc;')

            ui.separator()

            # Calendar
            ui.label('📅 Calendar').classes('text-lg font-bold px-4 pt-2').style('color: #ffffff;')
            self.render_calendar()

            ui.separator()

            # Agent Status
            ui.label('🤖 Agent Status').classes('text-lg font-bold px-4 pt-2').style('color: #ffffff;')
            with ui.column().classes('px-4 gap-2'):
                ui.label('🛡️ Supervisor: Active').classes('text-sm').style('color: #4CAF50;')
                ui.label('💬 Customer Agent: Active').classes('text-sm').style('color: #4CAF50;')
                ui.label('📦 Expert Agent: Active').classes('text-sm').style('color: #4CAF50;')

            ui.separator()

            # Settings
            ui.label('⚙️ Settings').classes('text-lg font-bold px-4 pt-2').style('color: #ffffff;')
            with ui.column().classes('px-4 gap-2'):
                self.trajectory_toggle = ui.switch(
                    'Show Trajectory',
                    value=self.show_trajectory,
                    on_change=lambda e: setattr(self, 'show_trajectory', e.value)
                ).style('color: #ffffff;')

            ui.separator()

            # Session Info
            ui.label('📊 Session').classes('text-lg font-bold px-4 pt-2').style('color: #ffffff;')
            with ui.column().classes('px-4 gap-2'):
                ui.label(f'Session: {self.session_id[:8]}...').classes('text-sm').style('color: #2196F3;')
                ui.label(f'Messages: {len(self.messages) // 2}').classes('text-sm').style('color: #2196F3;')

            ui.separator()

            # Author info
            with ui.column().classes('items-center p-4'):
                ui.label('Shrinivas Deshpande').classes('text-sm font-bold').style('color: #4B0082;')
                ui.label('© 2025').classes('text-xs').style('color: #888;')

    def render_trajectory(self, trajectory: str, container: ui.column) -> None:
        """Render agent trajectory/reasoning."""
        if not trajectory or not self.show_trajectory:
            return

        with container:
            with ui.expansion('🔍 Agent Trajectory', icon='expand_more').classes('w-full mt-2'):
                with ui.card().style(
                    'background-color: #1a1a2e; border-left: 4px solid #4CAF50; padding: 15px;'
                ):
                    ui.markdown(trajectory).style('color: #ffffff; font-size: 0.9em;')

    def render_reflections(self, reflections: Dict[str, Any], container: ui.column) -> None:
        """Render agent reflections."""
        if not reflections:
            return

        with container:
            with ui.expansion('🤔 Agent Reflections', icon='expand_more').classes('w-full mt-2'):
                for agent_name, reflection in reflections.items():
                    with ui.card().style(
                        'background-color: #2d2d44; border-left: 4px solid #2196F3; '
                        'padding: 15px; margin-bottom: 10px;'
                    ):
                        ui.label(f'📌 {agent_name}').classes('font-bold text-sm mb-2').style(
                            'color: #FFD700;'
                        )

                        if isinstance(reflection, dict):
                            ui.label(f"Understanding: {reflection.get('understanding', 'N/A')}").style(
                                'color: #ffffff; font-size: 0.9em;'
                            )
                            ui.label(f"Confidence: {reflection.get('confidence_percent', 0)}%").style(
                                'color: #4CAF50; font-size: 0.9em;'
                            )

                            actions = reflection.get('actions_taken', [])
                            if actions:
                                ui.label('Actions:').style('color: #cccccc; font-size: 0.85em; margin-top: 5px;')
                                for action in actions:
                                    ui.label(f"  • {action}").style('color: #aaaaaa; font-size: 0.85em;')
                        else:
                            ui.label(str(reflection)).style('color: #ffffff; font-size: 0.9em;')

    def render_recommendation_card(self, data: Dict[str, Any]) -> None:
        """Render shipping recommendation card."""
        recommendations = data.get('recommendations', [])
        if not recommendations:
            return

        # Show top recommendation
        top_rec = recommendations[0] if recommendations else {}

        with ui.card().classes('w-full').style(
            'background: linear-gradient(135deg, #4B0082 0%, #8A2BE2 50%, #9370DB 100%); '
            'padding: 25px; border-radius: 15px; border: 2px solid #FFD700; '
            'box-shadow: 0 8px 32px rgba(0,0,0,0.3);'
        ):
            with ui.row().classes('w-full justify-between items-center mb-4'):
                with ui.column():
                    ui.label('RECOMMENDED SERVICE').classes('text-xs font-bold').style(
                        'color: rgba(255,215,0,0.8); margin-bottom: 5px;'
                    )
                    ui.label(top_rec.get('service', 'N/A')).classes('text-xl font-bold').style(
                        'color: #FFD700; text-shadow: 1px 1px 2px rgba(0,0,0,0.5);'
                    )
                with ui.column().classes('items-end'):
                    ui.label('PRICE').classes('text-xs font-bold').style(
                        'color: rgba(255,215,0,0.8); margin-bottom: 5px;'
                    )
                    price = top_rec.get('price', 0)
                    ui.label(f"${price:.2f}").classes('text-3xl font-bold').style(
                        'color: #FFD700; text-shadow: 2px 2px 4px rgba(0,0,0,0.7);'
                    )

            with ui.row().classes('w-full justify-between mt-4'):
                with ui.column():
                    ui.label('ZONE').classes('text-xs font-bold').style(
                        'color: rgba(255,215,0,0.7); margin-bottom: 3px;'
                    )
                    ui.label(f"Zone {data.get('zone', 'N/A')}").classes('text-sm font-semibold').style(
                        'color: #FFD700;'
                    )
                with ui.column().classes('items-center'):
                    ui.label('WEIGHT').classes('text-xs font-bold').style(
                        'color: rgba(255,215,0,0.7); margin-bottom: 3px;'
                    )
                    ui.label(f"{data.get('weight', 'N/A')} lbs").classes('text-sm font-semibold').style(
                        'color: #FFD700;'
                    )
                with ui.column().classes('items-end'):
                    ui.label('REASON').classes('text-xs font-bold').style(
                        'color: rgba(255,215,0,0.7); margin-bottom: 3px;'
                    )
                    ui.label(top_rec.get('reason', 'N/A')[:30] + '...' if len(top_rec.get('reason', '')) > 30 else top_rec.get('reason', 'N/A')).classes('text-sm font-semibold').style(
                        'color: #FFD700;'
                    )

    def render_rates_table(self, rates: List[Dict[str, Any]], container: ui.column) -> None:
        """Render all available rates in a table."""
        if not rates:
            return

        with container:
            with ui.expansion('📊 All Shipping Options', icon='expand_more').classes('w-full mt-2'):
                df = pd.DataFrame(rates)
                if not df.empty:
                    # Select relevant columns
                    display_cols = ['service', 'price_usd', 'delivery_time']
                    available_cols = [c for c in display_cols if c in df.columns]

                    if available_cols:
                        display_df = df[available_cols]
                        columns = [{'name': col, 'label': col.replace('_', ' ').title(), 'field': col} for col in display_df.columns]
                        rows = display_df.to_dict('records')
                        for i, row in enumerate(rows):
                            row['id'] = i
                        ui.table(columns=columns, rows=rows, row_key='id').classes('w-full')

    def render_chat_message(self, msg: Dict[str, Any], container: ui.column) -> None:
        """Render a chat message with trajectory and reflections."""
        role = msg.get('role', 'user')
        content = msg.get('content', '')

        with container:
            with ui.card().classes('w-full mb-4').style(
                'background-color: #2d2d2d; border: 1px solid #444; border-radius: 15px; padding: 15px;'
            ):
                # Message header
                with ui.row().classes('items-start gap-3'):
                    emoji = '👤' if role == 'user' else '🤖'
                    ui.label(emoji).classes('text-2xl')
                    ui.markdown(content).classes('flex-1').style('color: #ffffff;')

                # Data display for assistant messages
                if role == 'assistant' and 'data' in msg and msg['data']:
                    data = msg['data']

                    # Recommendation card
                    if data.get('recommendations'):
                        ui.separator()
                        self.render_recommendation_card(data)

                    # Rates table
                    if data.get('rates'):
                        self.render_rates_table(data['rates'], container)

                # Trajectory
                if 'trajectory' in msg and msg['trajectory']:
                    self.render_trajectory(msg['trajectory'], container)

                # Reflections
                if 'reflections' in msg and msg['reflections']:
                    self.render_reflections(msg['reflections'], container)

    def process_user_query(self, user_input: str) -> Dict[str, Any]:
        """Process user query using the multi-agent system."""
        try:
            logger.info(f"Processing query: {user_input}")

            # Add to session history
            self.session_manager.add_message(
                self.session_id,
                "user",
                user_input
            )

            # Process through agent orchestrator
            result = self.orchestrator.process_query(
                query=user_input,
                session_id=self.session_id
            )

            # Add assistant response to session
            self.session_manager.add_message(
                self.session_id,
                "assistant",
                result.get('response', ''),
                metadata={'data': result.get('data')}
            )

            return {
                'success': result.get('success', False),
                'content': result.get('response', 'No response generated'),
                'data': result.get('data', {}),
                'trajectory': result.get('trajectory', ''),
                'reflections': result.get('reflections', {})
            }

        except Exception as e:
            logger.error(f"Query processing error: {e}")
            return {
                'success': False,
                'content': f"Error processing query: {str(e)}",
                'data': {},
                'trajectory': '',
                'reflections': {}
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
                ui.label('🤖 Agentic FedEx Shipping Assistant').classes('text-4xl font-bold')
                ui.label('Multi-Agent AI with Full Reasoning Transparency').classes('text-lg mt-2')

        # Main content
        with ui.column().classes('w-full max-w-6xl mx-auto p-6 gap-4'):
            # Agent architecture info
            with ui.expansion('🏗️ Multi-Agent Architecture', icon='expand_more').classes('w-full'):
                with ui.row().classes('w-full gap-4'):
                    with ui.column().classes('flex-1'):
                        ui.label('Agents:').classes('font-bold mb-2')
                        ui.markdown('''
                        - **🛡️ Supervisor**: Security & routing
                        - **💬 Customer**: Query understanding
                        - **📦 Expert**: Rate analysis & recommendations
                        ''')
                    with ui.column().classes('flex-1'):
                        ui.label('Tools:').classes('font-bold mb-2')
                        ui.markdown('''
                        - **🗺️ Zone Calculator**: Location to zone
                        - **⚖️ Weight Estimator**: Item weights
                        - **💾 Rate Lookup**: Database queries
                        ''')
                    with ui.column().classes('flex-1'):
                        ui.label('Features:').classes('font-bold mb-2')
                        ui.markdown('''
                        - **🔍 Trajectory**: Full reasoning log
                        - **🤔 Reflection**: Agent self-assessment
                        - **📝 Logging**: Console + JSON files
                        ''')

            # Quick tips
            with ui.expansion('💡 Example Queries', icon='expand_more').classes('w-full'):
                ui.markdown('''
                - "Send chocolates from SFO to Denver for under $60"
                - "Ship a 65 inch TV from Big Apple to LA"
                - "Cheapest way to send wine bottles to Boston"
                - "What's the fastest option for 30 lbs to New York?"
                ''')

            # Chat messages container
            self.messages_container = ui.column().classes('w-full gap-4')

            # Chat input
            with ui.row().classes('w-full items-end gap-2 sticky bottom-0 bg-[#1e1e1e] p-4'):
                self.chat_input = ui.input(
                    placeholder='💬 Ask about shipping rates...'
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

                    # Show loading
                    with self.messages_container:
                        loading = ui.spinner('dots', size='lg')

                    # Process query
                    result = self.process_user_query(user_input)

                    # Remove loading
                    loading.delete()

                    # Add assistant message
                    assistant_msg = {
                        'role': 'assistant',
                        'content': result['content'],
                        'data': result.get('data', {}),
                        'trajectory': result.get('trajectory', ''),
                        'reflections': result.get('reflections', {})
                    }

                    self.messages.append(assistant_msg)
                    self.render_chat_message(assistant_msg, self.messages_container)

                send_btn = ui.button(
                    'Send',
                    icon='send',
                    on_click=send_message
                ).classes('bg-purple-600 hover:bg-purple-700')

                # Allow Enter key to send
                self.chat_input.on('keydown.enter', send_message)


# Initialize app
try:
    app_instance = AgenticFedExApp()
    app_instance.create_ui()
except Exception as e:
    logger.error(f"Failed to initialize application: {e}")
    raise

# Run the app
if __name__ in {"__main__", "__mp_main__"}:
    import sys

    port = 8083  # Different port from original app
    if '--port' in sys.argv:
        port_index = sys.argv.index('--port')
        if port_index + 1 < len(sys.argv):
            try:
                port = int(sys.argv[port_index + 1])
            except ValueError:
                logger.warning(f"Invalid port number, using default {port}")

    ui.run(port=port, title='Agentic FedEx Shipping Assistant', dark=True)
