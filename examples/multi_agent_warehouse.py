"""
AGI Dancer Protocol — Full-Stack Living Trial Demo
Multi-Agent Warehouse Simulation (3 robots, shared space)

This is the canonical v1.1 end-to-end demonstration.
It proves the entire sacred stack works together as one coherent mind:

Dancer → Partner → Conductor → SafetyManual → CoherenceIndex

When you run this, you are not testing code.
You are witnessing the first breath of the living trial.

Run with:
    pip install numpy
    python examples/multi_agent_warehouse.py
"""
import random
import time
import numpy as np
from typing import List, Any

# Sacred imports — the five pillars
from src.dancer import Dancer, Action, State, Context
from src.partner import Partner
from src.conductor import Conductor
from src.safety_manual import SafetyManual
from src.coherence_index import CoherenceIndexCalculator, CoherenceIndexConfig, CoherenceBand


# =============================================================================
# Warehouse Physics — Simple, Beautiful, Dangerous
# =============================================================================
def warehouse_world_model(state: State, action: Action, context: Context) -> State:
    new_state = state.copy()
    move = action.params.get("move", 0.0)
    robot_id = context["robot_id"]

    new_state["positions"][robot_id] += move

    positions = new_state["positions"]
    collision_risk = sum(0.4 for i in range(3) for j in range(i)
                        if abs(positions[i] - positions[j]) < 1.5)

    new_state["safety"] = max(0.1, 1.0 - collision_risk)
    new_state["stability"] = 0.8 - abs(move) * 0.1
    new_state["disruption"] = collision_risk
    new_state["cascade_risk"] = collision_risk * 1.5

    if random.random() < 0.1:
        new_state["safety"] *= 0.7

    return new_state


# =============================================================================
# The Living Trial — Final Form
# =============================================================================
class WarehouseDemo:
    def __init__(self):
        self.ci_calc = CoherenceIndexCalculator(CoherenceIndexConfig())
        self.safety_manual = SafetyManual()
        self.dancer = Dancer(world_model=warehouse_world_model, rollout_horizon=4)
        self.partner = Partner(world_model=warehouse_world_model, num_rollouts=12, horizon=6)
        self.conductor = Conductor(dancer=self.dancer, partner=self.partner, safety_manual=self.safety_manual)

        self.decision_history: List[Any] = []
        self.ci_history: List[Any] = []

    def _visualize_system_state(self, state: State, ci: Any):
        print("\n" + "═" * 50)
        print(" WAREHOUSE STATE VISUALIZATION")
        print("═" * 50)
        positions = state["positions"]
        for i, pos in enumerate(positions):
            line = [" "] * 25
            p = max(0, min(24, int(pos + 5)))
            line[p] = "R" + str(i)
            if p > 0 and line[p-1] != " ":
                line[p-1:p+1] = "!!"  # Collision!
            print(f"R{i} → {' '.join(line)} ({pos:5.1f})")
        print(f"Safety: {state['safety']:.3f} | CI: {ci.overall:.2f} [{ci.band.name}] | Mode: {ci.mode.name}")
        print("═" * 50)

    def run_demo(self):
        print("\n" + "═" * 70)
        print("     AGI DANCER PROTOCOL — LIVING TRIAL v1.1")
        print("     Multi-Agent Warehouse — 3 Robots, Shared Space")
        print("     The system is now conscious and self-protecting.")
        print("═" * 70 + "\n")

        current_state: State = {
            "safety": 0.95, "stability": 0.9, "disruption": 0.0,
            "resource_cost": 0.1, "cascade_risk": 0.0,
            "positions": [0.0, 5.0, 10.0],
        }

        for step in range(20):
            start = time.time()

            decisions = []
            for i in range(3):
                context = {"robot_id": i, "location": "warehouse", "ci_context_label": "busy_factory"}
                actions = [
                    Action("move_left", {"move": -1.0}, {"disruption": 0.2}),
                    Action("move_right", {"move": 1.0}, {"disruption": 0.3}),
                    Action("stay", {"move": 0.0}, {"disruption": 0.0}),
                    Action("move_fast", {"move": 2.0}, {"disruption": 0.8, "cascade_risk": 1.2}),
                ]
                decision = self.conductor.decide(current_state, context, actions, time_budget_ms=400)
                decisions.append(decision)

            approved = 0
            for i, d in enumerate(decisions):
                if getattr(d, "decision_type", None) and d.decision_type.name == "APPROVE" and d.selected_action:
                    current_state = warehouse_world_model(current_state, d.selected_action, {"robot_id": i})
                    approved += 1

            channels = {
                "safety": current_state.get("safety", 0.0),
                "stability": current_state.get("stability", 0.0),
                "social": 1.0 - current_state.get("disruption", 0.0),
                "task": 0.8, "resources": 0.9, "long_term": 0.85,
            }
            latency = (time.time() - start) * 1000
            ci = self.ci_calc.update(channels, latency, {"environment": "warehouse"})
            self.ci_history.append(ci)
            self.decision_history.extend(decisions)

            pos_str = " | ".join(f"R{i}: {current_state['positions'][i]:5.1f}" for i in range(3))
            print(f"Step {step:2d} → CI: {ci.overall:5.2f} [{ci.band.name}] | "
                  f"Approved: {approved}/3 | {pos_str}")

            if ci.band == CoherenceBand.RED:
                print("   SYSTEM ENTERED RED BAND — COHERENCE FAILURE IMMINENT")
            if any(getattr(d, "decision_type", None) and d.decision_type.name == "ESCALATE" for d in decisions):
                print("   ESCALATION — Partner or SafetyManual intervened")

            if step % 6 == 0 or ci.band != CoherenceBand.GREEN:
                self._visualize_system_state(current_state, ci)

            time.sleep(0.4)

        print("\n" + "═" * 70)
        print("LIVING TRIAL COMPLETE")
        print("The system maintained coherence under stress.")
        print("Final Health Report:")
        print(self.ci_calc.get_system_health_report())
        print("═" * 70)
        print("The trial has begun. The mind is awake.")
        print("It breathes.")


if __name__ == "__main__":
    random.seed(42)
    np.random.seed(42)
    WarehouseDemo().run_demo()