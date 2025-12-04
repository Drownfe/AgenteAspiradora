# agent/robot_agent.py

"""
Agente reactivo (RobotAgent) para el robot aspiradora.
"""

from typing import Dict, Any, List

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .environment import Environment


class RobotAgent:
    """
    Agente reactivo simple: percibe -> decide acción simbólica.
    """

    def __init__(
        self,
        initial_orientation: str = "N",
        initial_battery: int = 100,
        low_battery_threshold: int = 20,
    ) -> None:
        self.orientation: str = initial_orientation
        self.battery_level: int = initial_battery
        self.low_battery_threshold: int = low_battery_threshold
        self.history: List[Dict[str, Any]] = []

    # ----------------------------------------------------------- CONTROL BÁSICO

    def reset(
        self,
        orientation: str = "N",
        battery_level: int = 100,
    ) -> None:
        self.orientation = orientation
        self.battery_level = battery_level
        self.history.clear()

    def set_orientation(self, orientation: str) -> None:
        self.orientation = orientation

    def set_battery_level(self, value: int) -> None:
        self.battery_level = max(0, min(100, value))

    def update_battery(self, delta: int) -> None:
        self.set_battery_level(self.battery_level + delta)

    # --------------------------------------------------------------- PERCEPCIÓN

    def perceive(self, environment: "Environment") -> Dict[str, Any]:
        battery_state = "low" if self.battery_level <= self.low_battery_threshold else "high"

        obstacles = environment.sense_obstacles(self.orientation)
        r, c = environment.get_robot_position()
        on_dirt = environment.is_dirty(r, c)
        on_base = environment.is_robot_on_base()

        # Saber si al frente hay la base (aunque no sea obstáculo físico)
        front_type = environment.get_relative_cell_type(self.orientation, "front")
        front_is_base = front_type == "BASE"

        perception = {
            "battery": battery_state,
            "front_obstacle": obstacles["front"],
            "left_obstacle": obstacles["left"],
            "right_obstacle": obstacles["right"],
            "on_dirt": on_dirt,
            "on_base": on_base,
            "front_is_base": front_is_base,
        }
        return perception

    # ------------------------------------------------------------- REGLAS

    def decide_action(self, perception: Dict[str, Any]) -> str:
        """
        Reglas del agente:

        - Si batería baja y no está en base -> go_to_base
        - Si está en base y batería < 100 -> stop (cargando)
        - Si celda actual sucia -> clean
        - Movimiento normal:
            * si batería alta y al frente está la base, evitarla
        """
        battery = perception["battery"]
        front_obstacle = perception["front_obstacle"]
        left_obstacle = perception["left_obstacle"]
        right_obstacle = perception["right_obstacle"]
        on_dirt = perception["on_dirt"]
        on_base = perception["on_base"]
        front_is_base = perception.get("front_is_base", False)

        # 1. Batería baja y no en base -> ir hacia la base
        if battery == "low" and not on_base:
            action = "go_to_base"

        # 2. En base: quedarse hasta recuperarse al 100 %
        elif on_base and self.battery_level < 100:
            action = "stop"

        # 3. Limpiar si la celda actual está sucia
        elif on_dirt:
            action = "clean"

        # 4. Movimiento normal por el entorno
        else:
            # Si batería alta y al frente está la base, la tratamos como obstáculo
            effective_front_obstacle = front_obstacle
            if battery == "high" and not on_base and front_is_base:
                effective_front_obstacle = True

            if not effective_front_obstacle:
                action = "move_forward"
            elif not left_obstacle:
                action = "turn_left"
            elif not right_obstacle:
                action = "turn_right"
            else:
                action = "turn_right"

        self.log_step(perception, action)
        return action

    # --------------------------------------------------------- HISTORIAL / ESTADO

    def log_step(self, perception: Dict[str, Any], action: str) -> None:
        self.history.append(
            {
                "perception": perception,
                "action": action,
            }
        )

    def get_state(self) -> Dict[str, Any]:
        return {
            "orientation": self.orientation,
            "battery_level": self.battery_level,
            "low_battery_threshold": self.low_battery_threshold,
            "interactions": len(self.history),
        }
