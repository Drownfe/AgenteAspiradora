# app.py

from flask import Flask, render_template, redirect, url_for, jsonify
from simulation.simulator import Simulator

app = Flask(__name__)

# Instancia global del simulador
simulator = Simulator(
    env_rows=8,
    env_cols=8,
    obstacle_prob=0.15,
    dirt_prob=0.3,
    initial_battery=100,
    low_battery_threshold=20,
)


@app.route("/", methods=["GET"])
def index():
    """
    Muestra el estado actual inicial (primer render).
    """
    state = simulator.get_state()
    return render_template("index.html", state=state)


@app.route("/step", methods=["POST"])
def step():
    """
    Ruta de respaldo (manual) que hace un paso y recarga la página.
    La dejamos por si acaso, aunque en el front nuevo usamos /step_json.
    """
    simulator.run_step()
    return redirect(url_for("index"))


@app.route("/step_json", methods=["POST"])
def step_json():
    """
    Ejecuta un paso de simulación y devuelve el estado en JSON.
    Esta es la ruta que usa el front para el modo automático.
    """
    state = simulator.run_step()
    return jsonify(state)


@app.route("/reset", methods=["POST"])
def reset():
    """
    Reinicia la simulación con un nuevo mapa.
    """
    simulator.reset()
    return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(debug=True)
