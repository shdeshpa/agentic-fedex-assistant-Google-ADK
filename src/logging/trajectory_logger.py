"""
Trajectory Logger for FedEx Shipping Assistant.

Logs agent reasoning, tool calls, and decision trajectories to:
- Console (formatted output)
- JSON files (structured data for analysis)
"""

import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, asdict, field
from enum import Enum
from loguru import logger


class StepType(str, Enum):
    """Types of trajectory steps."""
    AGENT_START = "agent_start"
    AGENT_END = "agent_end"
    TOOL_CALL = "tool_call"
    TOOL_RESULT = "tool_result"
    REASONING = "reasoning"
    REFLECTION = "reflection"
    ERROR = "error"
    TRANSFER = "transfer"
    USER_INPUT = "user_input"
    AGENT_OUTPUT = "agent_output"


@dataclass
class TrajectoryStep:
    """Single step in agent reasoning trajectory."""
    timestamp: str
    step_type: StepType
    agent_name: str
    action: str
    input_data: Optional[Dict[str, Any]] = None
    output_data: Optional[Dict[str, Any]] = None
    reasoning: Optional[str] = None
    duration_ms: Optional[float] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Trajectory:
    """Complete trajectory for a request."""
    session_id: str
    request_id: str
    start_time: str
    end_time: Optional[str] = None
    user_query: str = ""
    steps: List[TrajectoryStep] = field(default_factory=list)
    final_result: Optional[Dict[str, Any]] = None
    success: bool = True
    error_message: Optional[str] = None


class TrajectoryLogger:
    """
    Logs agent reasoning and tool calls to console and JSON files.

    Features:
    - Real-time console output with formatting
    - JSON Lines (JSONL) file output for analysis
    - Session tracking
    - Step-by-step reasoning visibility
    """

    def __init__(
        self,
        log_dir: str = "./logs",
        console_enabled: bool = True,
        file_enabled: bool = True,
        log_level: str = "INFO"
    ):
        """
        Initialize Trajectory Logger.

        Args:
            log_dir: Directory for JSON log files
            console_enabled: Enable console output
            file_enabled: Enable file output
            log_level: Logging level (DEBUG, INFO, WARNING, ERROR)
        """
        self.log_dir = Path(log_dir)
        self.console_enabled = console_enabled
        self.file_enabled = file_enabled

        # Create log directory
        if file_enabled:
            self.log_dir.mkdir(parents=True, exist_ok=True)

        # Configure loguru for console output
        logger.remove()  # Remove default handler
        if console_enabled:
            logger.add(
                sys.stderr,
                format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{extra[agent]:15}</cyan> | {message}",
                level=log_level,
                colorize=True,
                filter=lambda record: "agent" in record["extra"]
            )
            # Also add a default handler for logs without agent
            logger.add(
                sys.stderr,
                format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | {message}",
                level=log_level,
                colorize=True,
                filter=lambda record: "agent" not in record["extra"]
            )

        # Active trajectories by session
        self._trajectories: Dict[str, Trajectory] = {}

        logger.info("Trajectory Logger initialized", agent="system")

    def start_trajectory(
        self,
        session_id: str,
        request_id: str,
        user_query: str
    ) -> Trajectory:
        """
        Start tracking a new trajectory.

        Args:
            session_id: Session identifier
            request_id: Unique request identifier
            user_query: Original user query

        Returns:
            New Trajectory object
        """
        trajectory = Trajectory(
            session_id=session_id,
            request_id=request_id,
            start_time=datetime.now().isoformat(),
            user_query=user_query
        )

        self._trajectories[request_id] = trajectory

        self._log_step(
            trajectory,
            TrajectoryStep(
                timestamp=datetime.now().isoformat(),
                step_type=StepType.USER_INPUT,
                agent_name="user",
                action="User Query",
                input_data={"query": user_query}
            )
        )

        return trajectory

    def log_agent_start(
        self,
        request_id: str,
        agent_name: str,
        input_data: Optional[Dict[str, Any]] = None
    ):
        """Log when an agent starts processing."""
        trajectory = self._trajectories.get(request_id)
        if not trajectory:
            return

        step = TrajectoryStep(
            timestamp=datetime.now().isoformat(),
            step_type=StepType.AGENT_START,
            agent_name=agent_name,
            action=f"Agent {agent_name} started",
            input_data=input_data
        )

        self._log_step(trajectory, step)

    def log_agent_end(
        self,
        request_id: str,
        agent_name: str,
        output_data: Optional[Dict[str, Any]] = None,
        duration_ms: Optional[float] = None
    ):
        """Log when an agent finishes processing."""
        trajectory = self._trajectories.get(request_id)
        if not trajectory:
            return

        step = TrajectoryStep(
            timestamp=datetime.now().isoformat(),
            step_type=StepType.AGENT_END,
            agent_name=agent_name,
            action=f"Agent {agent_name} completed",
            output_data=output_data,
            duration_ms=duration_ms
        )

        self._log_step(trajectory, step)

    def log_tool_call(
        self,
        request_id: str,
        agent_name: str,
        tool_name: str,
        input_data: Dict[str, Any]
    ):
        """Log a tool call."""
        trajectory = self._trajectories.get(request_id)
        if not trajectory:
            return

        step = TrajectoryStep(
            timestamp=datetime.now().isoformat(),
            step_type=StepType.TOOL_CALL,
            agent_name=agent_name,
            action=f"Calling tool: {tool_name}",
            input_data=input_data,
            metadata={"tool_name": tool_name}
        )

        self._log_step(trajectory, step)

    def log_tool_result(
        self,
        request_id: str,
        agent_name: str,
        tool_name: str,
        result: Dict[str, Any],
        duration_ms: Optional[float] = None
    ):
        """Log a tool result."""
        trajectory = self._trajectories.get(request_id)
        if not trajectory:
            return

        step = TrajectoryStep(
            timestamp=datetime.now().isoformat(),
            step_type=StepType.TOOL_RESULT,
            agent_name=agent_name,
            action=f"Tool {tool_name} result",
            output_data=result,
            duration_ms=duration_ms,
            metadata={"tool_name": tool_name}
        )

        self._log_step(trajectory, step)

    def log_reasoning(
        self,
        request_id: str,
        agent_name: str,
        reasoning: str,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """Log agent reasoning/thinking."""
        trajectory = self._trajectories.get(request_id)
        if not trajectory:
            return

        step = TrajectoryStep(
            timestamp=datetime.now().isoformat(),
            step_type=StepType.REASONING,
            agent_name=agent_name,
            action="Reasoning",
            reasoning=reasoning,
            metadata=metadata or {}
        )

        self._log_step(trajectory, step)

    def log_reflection(
        self,
        request_id: str,
        agent_name: str,
        reflection: Dict[str, Any]
    ):
        """Log agent reflection (self-assessment)."""
        trajectory = self._trajectories.get(request_id)
        if not trajectory:
            return

        step = TrajectoryStep(
            timestamp=datetime.now().isoformat(),
            step_type=StepType.REFLECTION,
            agent_name=agent_name,
            action="Reflection",
            output_data=reflection,
            reasoning=reflection.get("summary", "")
        )

        self._log_step(trajectory, step)

    def log_transfer(
        self,
        request_id: str,
        from_agent: str,
        to_agent: str,
        reason: str
    ):
        """Log agent transfer/handoff."""
        trajectory = self._trajectories.get(request_id)
        if not trajectory:
            return

        step = TrajectoryStep(
            timestamp=datetime.now().isoformat(),
            step_type=StepType.TRANSFER,
            agent_name=from_agent,
            action=f"Transfer to {to_agent}",
            reasoning=reason,
            metadata={"to_agent": to_agent}
        )

        self._log_step(trajectory, step)

    def log_error(
        self,
        request_id: str,
        agent_name: str,
        error: str,
        details: Optional[Dict[str, Any]] = None
    ):
        """Log an error."""
        trajectory = self._trajectories.get(request_id)
        if not trajectory:
            return

        step = TrajectoryStep(
            timestamp=datetime.now().isoformat(),
            step_type=StepType.ERROR,
            agent_name=agent_name,
            action="Error",
            reasoning=error,
            metadata=details or {}
        )

        self._log_step(trajectory, step)
        trajectory.success = False
        trajectory.error_message = error

    def end_trajectory(
        self,
        request_id: str,
        final_result: Optional[Dict[str, Any]] = None
    ) -> Optional[Trajectory]:
        """
        End and save a trajectory.

        Args:
            request_id: Request identifier
            final_result: Final output to save

        Returns:
            Completed Trajectory object
        """
        trajectory = self._trajectories.get(request_id)
        if not trajectory:
            return None

        trajectory.end_time = datetime.now().isoformat()
        trajectory.final_result = final_result

        # Log final output
        self._log_step(
            trajectory,
            TrajectoryStep(
                timestamp=datetime.now().isoformat(),
                step_type=StepType.AGENT_OUTPUT,
                agent_name="system",
                action="Final Result",
                output_data=final_result
            )
        )

        # Save to file
        if self.file_enabled:
            self._save_trajectory(trajectory)

        # Clean up
        del self._trajectories[request_id]

        return trajectory

    def _log_step(self, trajectory: Trajectory, step: TrajectoryStep):
        """Log a single step to console and add to trajectory."""
        trajectory.steps.append(step)

        if self.console_enabled:
            self._console_log(step)

    def _console_log(self, step: TrajectoryStep):
        """Format and output step to console."""
        agent = step.agent_name

        # Helper to safely format data (escape braces)
        def safe_str(data):
            if data is None:
                return "None"
            s = str(data)
            # Escape braces for logging
            return s.replace("{", "{{").replace("}", "}}")

        # Color-code by step type
        if step.step_type == StepType.AGENT_START:
            logger.bind(agent=agent).info(f">>> {step.action}")
        elif step.step_type == StepType.AGENT_END:
            msg = f"<<< {step.action} ({step.duration_ms:.0f}ms)" if step.duration_ms else f"<<< {step.action}"
            logger.bind(agent=agent).info(msg)
        elif step.step_type == StepType.TOOL_CALL:
            tool = step.metadata.get("tool_name", "unknown")
            logger.bind(agent=agent).info(f"[TOOL] Calling {tool}: {safe_str(step.input_data)}")
        elif step.step_type == StepType.TOOL_RESULT:
            tool = step.metadata.get("tool_name", "unknown")
            logger.bind(agent=agent).success(f"[TOOL] {tool} returned: {safe_str(self._truncate(step.output_data))}")
        elif step.step_type == StepType.REASONING:
            logger.bind(agent=agent).debug(f"[THINK] {step.reasoning}")
        elif step.step_type == StepType.REFLECTION:
            logger.bind(agent=agent).info(f"[REFLECT] {step.reasoning}")
        elif step.step_type == StepType.TRANSFER:
            to_agent = step.metadata.get("to_agent", "unknown")
            logger.bind(agent=agent).warning(f"[TRANSFER] -> {to_agent}: {step.reasoning}")
        elif step.step_type == StepType.ERROR:
            logger.bind(agent=agent).error(f"[ERROR] {step.reasoning}")
        elif step.step_type == StepType.USER_INPUT:
            query = step.input_data.get('query', '') if step.input_data else ''
            logger.bind(agent="user").info(f"[USER] {query}")
        elif step.step_type == StepType.AGENT_OUTPUT:
            logger.bind(agent=agent).success(f"[OUTPUT] {safe_str(self._truncate(step.output_data))}")

    def _truncate(self, data: Any, max_length: int = 200) -> str:
        """Truncate data for console display."""
        if data is None:
            return "None"
        s = str(data)
        if len(s) > max_length:
            return s[:max_length] + "..."
        return s

    def _save_trajectory(self, trajectory: Trajectory):
        """Save trajectory to JSON Lines file."""
        date_str = datetime.now().strftime("%Y%m%d")
        log_file = self.log_dir / f"trajectory_{date_str}.jsonl"

        # Convert to dict for JSON serialization
        trajectory_dict = asdict(trajectory)

        # Convert steps to dicts
        trajectory_dict["steps"] = [asdict(s) for s in trajectory.steps]

        with open(log_file, "a") as f:
            f.write(json.dumps(trajectory_dict) + "\n")

        logger.debug(f"Saved trajectory to {log_file}", agent="system")

    def get_trajectory(self, request_id: str) -> Optional[Trajectory]:
        """Get current trajectory by request ID."""
        return self._trajectories.get(request_id)

    def format_trajectory_markdown(self, trajectory: Trajectory) -> str:
        """Format trajectory as readable markdown."""
        lines = [
            f"# Trajectory: {trajectory.request_id}",
            f"**Session:** {trajectory.session_id}",
            f"**Query:** {trajectory.user_query}",
            f"**Start:** {trajectory.start_time}",
            f"**End:** {trajectory.end_time or 'In Progress'}",
            f"**Status:** {'Success' if trajectory.success else 'Failed'}",
            "",
            "## Steps",
            ""
        ]

        for i, step in enumerate(trajectory.steps, 1):
            lines.append(f"### Step {i}: {step.action}")
            lines.append(f"- **Agent:** {step.agent_name}")
            lines.append(f"- **Type:** {step.step_type.value}")
            lines.append(f"- **Time:** {step.timestamp}")

            if step.input_data:
                lines.append(f"- **Input:** `{json.dumps(step.input_data)}`")
            if step.output_data:
                lines.append(f"- **Output:** `{json.dumps(step.output_data)}`")
            if step.reasoning:
                lines.append(f"- **Reasoning:** {step.reasoning}")
            if step.duration_ms:
                lines.append(f"- **Duration:** {step.duration_ms:.2f}ms")

            lines.append("")

        if trajectory.final_result:
            lines.append("## Final Result")
            lines.append(f"```json\n{json.dumps(trajectory.final_result, indent=2)}\n```")

        return "\n".join(lines)
