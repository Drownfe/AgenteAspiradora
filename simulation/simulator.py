# simulation/simulator.py

"""
Orquesta la simulación: entorno + agente.
"""

from typing import Dict, Any, List, Tuple

from agent.environment import Environment
from agent.robot_agent import RobotAgent


class Simulator:
    def __init__(
        self,
        env_rows: int = 8,
        env_cols: int = 8,
        obstacle_prob: float = 0.1,
        dirt_prob: float = 0.2,
        initial_battery: int = 100,
        low_battery_threshold: int = 20,
    ) -> None:

        self.environment = Environment(
            rows=env_rows,
            cols=env_cols,
            obstacle_prob=obstacle_prob,
            dirt_prob=dirt_prob,
        )

        self.agent = RobotAgent(
            initial_orientation="N",
            initial_battery=initial_battery,
            low_battery_threshold=low_battery_threshold,
        )

        self.step_count: int = 0
        self.last_perception: Dict[str, Any] = {}
        self.last_action: str = "none"

        # Costos de batería
        # go_to_base es barato para que alcance a volver con batería baja
        self.battery_costs = {
            "clean": -4,
            "move_forward": -3,
            "turn_left": -2,
            "turn_right": -2,
            "go_to_base": -1,
            "stop": 0,
        }
        # Recarga rápida en la base
        self.recharge_amount: int = 8

        self.initial_dirty_cells: int = max(self.environment.count_dirty_cells(), 1)

    # -------------------------------------------------------------- CONTROL

    def reset(self) -> None:
        """
        Nuevo mapa + agente reseteado.
        """
        self.environment.generate_random_map()
        self.agent.reset(orientation="N", battery_level=100)
        self.step_count = 0
        self.last_perception = {}
        self.last_action = "none"
        self.initial_dirty_cells = max(self.environment.count_dirty_cells(), 1)

    def run_step(self) -> Dict[str, Any]:
        """
        Ejecuta un paso y devuelve el nuevo estado.

        Si ya no hay batería o ya se limpió todo, no hace nada más.
        """
        if self.agent.battery_level <= 0 or self.environment.count_dirty_cells() == 0:
            return self.get_state()

        # 1. Percibir
        perception = self.agent.perceive(self.environment)
        self.last_perception = perception

        # 2. Decidir acción
        action = self.agent.decide_action(perception)
        self.last_action = action

        # 3. Aplicar acción
        self._apply_action(action)

        # 4. Contador de pasos
        self.step_count += 1

        # 5. Estado actual
        return self.get_state()

    # ------------------------------------------------------- APLICAR ACCIONES

    def _apply_action(self, action: str) -> None:
        """
        Aplica el efecto de la acción sobre batería + entorno.
        """
        cost = self.battery_costs.get(action, 0)
        self.agent.update_battery(cost)

        # Si la batería llegó a 0, este paso termina aquí
        if self.agent.battery_level <= 0:
            self.agent.set_battery_level(0)
            return

        if action == "clean":
            self.environment.clean_current_cell()

        elif action == "move_forward":
            self.environment.move_robot_forward(self.agent.orientation)

        elif action == "turn_left":
            new_orientation = self._rotate_orientation(self.agent.orientation, "left")
            self.agent.set_orientation(new_orientation)

        elif action == "turn_right":
            new_orientation = self._rotate_orientation(self.agent.orientation, "right")
            self.agent.set_orientation(new_orientation)

        elif action == "go_to_base":
            self._go_to_base_step()

        elif action == "stop":
            # No cambia posición ni orientación
            pass

        # Si está en la base, recargar batería
        if self.environment.is_robot_on_base():
            self.agent.update_battery(self.recharge_amount)

    def _rotate_orientation(self, current: str, direction: str) -> str:
        directions = ["N", "E", "S", "W"]
        if current not in directions:
            return current
        idx = directions.index(current)
        if direction == "left":
            idx = (idx - 1) % 4
        elif direction == "right":
            idx = (idx + 1) % 4
        return directions[idx]

    def _go_to_base_step(self) -> None:
        """
        Paso para acercarse a la base:
        - Mira las 4 direcciones posibles.
        - Elige una celda libre que reduzca la distancia a la base.
        - Se orienta hacia ella y avanza.
        Si todas las celdas alrededor son paredes, no se mueve.
        """
        robot_r, robot_c = self.environment.get_robot_position()
        base_r, base_c = self.environment.base_position

        # Direcciones absolutas con sus deltas (fila, col)
        candidates: List[Tuple[str, int, int]] = [
            ("N", -1, 0),
            ("S", 1, 0),
            ("W", 0, -1),
            ("E", 0, 1),
        ]

        best_dir = None
        best_dist = None

        for direction, dr, dc in candidates:
            nr = robot_r + dr
            nc = robot_c + dc

            # Ignorar si es obstáculo (pared)
            if self.environment.is_obstacle(nr, nc):
                continue

            # Distancia al cuadrado desde la celda candidata a la base
            dist_sq = (base_r - nr) ** 2 + (base_c - nc) ** 2

            if best_dist is None or dist_sq < best_dist:
                best_dist = dist_sq
                best_dir = direction

        # Si encontramos al menos una dirección viable, orientamos y avanzamos
        if best_dir is not None:
            self.agent.set_orientation(best_dir)
            self.environment.move_robot_forward(self.agent.orientation)
        # Si no hay ninguna celda libre alrededor, se queda donde está.

    # --------------------------------------------------------------- ESTADO UI

    def get_state(self) -> Dict[str, Any]:
        env_dict = self.environment.to_dict()
        agent_state = self.agent.get_state()

        dirty_now = env_dict["dirty_cells"]
        progress = 1 - (dirty_now / self.initial_dirty_cells)

        done = dirty_now == 0 and self.initial_dirty_cells > 0

        return {
            "step_count": self.step_count,
            "environment": env_dict,
            "agent": agent_state,
            "last_perception": self.last_perception,
            "last_action": self.last_action,
            "progress": progress,
            "done": done,
        }
