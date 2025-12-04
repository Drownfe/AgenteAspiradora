// static/js/main.js

function renderState(state) {
    const env = state.environment;
    const gridDiv = document.getElementById("grid");
    if (!gridDiv) return;

    const robotPos = env.robot_position;
    const robotRow = robotPos[0];
    const robotCol = robotPos[1];

    // Tamaño de columnas del grid
    gridDiv.style.gridTemplateColumns = `repeat(${env.cols}, 1fr)`;

    // Render de la grilla tipo cartilla
    let html = "";
    for (let r = 0; r < env.rows; r++) {
        for (let c = 0; c < env.cols; c++) {
            const cell = env.grid[r][c];
            let classes = "cell ";
            let symbol = "⬜";

            if (r === robotRow && c === robotCol) {
                classes += "robot ";
                symbol = "🧹";
            } else if (cell === "WALL") {
                classes += "wall ";
                symbol = "🧱";
            } else if (cell === "DIRT") {
                classes += "dirt ";
                symbol = "🟫";
            } else if (cell === "BASE") {
                classes += "base ";
                symbol = "🔌";
            } else {
                classes += "empty ";
                symbol = "⬜";
            }

            html += `<div class="${classes}">${symbol}</div>`;
        }
    }
    gridDiv.innerHTML = html;

    // Panel derecho: datos básicos
    const stepSpan = document.getElementById("step-count");
    const orientationSpan = document.getElementById("orientation");
    const progressSpan = document.getElementById("progress");
    const lastActionSpan = document.getElementById("last-action");
    const dirtyRemainingSpan = document.getElementById("dirty-remaining");

    if (stepSpan) stepSpan.textContent = state.step_count;
    if (orientationSpan) orientationSpan.textContent = state.agent.orientation;

    const dirtyRemaining = env.dirty_cells;
    if (dirtyRemainingSpan) dirtyRemainingSpan.textContent = dirtyRemaining;

    if (progressSpan) {
        const p = (state.progress * 100).toFixed(1);
        progressSpan.textContent = `${p}%`;
    }

    if (lastActionSpan) {
        lastActionSpan.textContent = state.last_action || "-";
    }

    // Progreso: barra visual
    const progressBar = document.getElementById("progress-bar");
    if (progressBar) {
        const p = Math.max(0, Math.min(100, state.progress * 100));
        progressBar.style.width = `${p}%`;
    }

    // Percepciones
    const perc = state.last_perception || {};
    const percBattery = document.getElementById("perc-battery");
    const percFront = document.getElementById("perc-front");
    const percDirt = document.getElementById("perc-dirt");
    const percBase = document.getElementById("perc-base");

    if (percBattery) percBattery.textContent = perc.battery || "-";

    if (percFront) {
        if (Object.prototype.hasOwnProperty.call(perc, "front_obstacle")) {
            percFront.textContent = perc.front_obstacle ? "Sí" : "No";
        } else {
            percFront.textContent = "-";
        }
    }

    if (percDirt) {
        if (Object.prototype.hasOwnProperty.call(perc, "on_dirt")) {
            percDirt.textContent = perc.on_dirt ? "Sí" : "No";
        } else {
            percDirt.textContent = "-";
        }
    }

    if (percBase) {
        if (Object.prototype.hasOwnProperty.call(perc, "on_base")) {
            percBase.textContent = perc.on_base ? "Sí" : "No";
        } else {
            percBase.textContent = "-";
        }
    }

    // Batería
    updateBattery(state.agent.battery_level);

    // Estado general (pill)
    updateStatus(state);
}

function updateBattery(level) {
    const bar = document.getElementById("battery-level");
    const text = document.getElementById("battery-text");
    if (!bar || !text) return;

    bar.style.width = `${level}%`;
    bar.classList.remove("low", "medium", "high");

    if (level <= 20) {
        bar.classList.add("low");
    } else if (level <= 60) {
        bar.classList.add("medium");
    } else {
        bar.classList.add("high");
    }

    text.textContent = `${level}%`;
}

function updateStatus(state) {
    const statusDiv = document.getElementById("agent-status");
    if (!statusDiv) return;

    const perc = state.last_perception || {};
    const batteryLevel = state.agent.battery_level;
    const done = state.done;
    const lastAction = state.last_action || "";
    const onBase = !!perc.on_base;
    const batteryLabel = perc.battery || "high";

    let text = "En espera";
    let gradient = "linear-gradient(90deg, #1d4ed8, #22c55e)";

    if (done) {
        text = "✔ Habitación limpia";
        gradient = "linear-gradient(90deg, #22c55e, #16a34a)";
    } else if (batteryLevel <= 0) {
        text = "⚠ Sin batería";
        gradient = "linear-gradient(90deg, #ef4444, #b91c1c)";
    } else if (onBase && batteryLevel < 100) {
        text = "🔌 Cargando en base";
        gradient = "linear-gradient(90deg, #0f766e, #22c55e)";
    } else if (batteryLabel === "low" && !onBase) {
        text = "🪫 Buscando la base";
        gradient = "linear-gradient(90deg, #f97316, #ef4444)";
    } else if (lastAction === "clean") {
        text = "🧽 Limpiando";
        gradient = "linear-gradient(90deg, #0ea5e9, #22c55e)";
    } else {
        text = "🚗 Recorriendo la habitación";
        gradient = "linear-gradient(90deg, #1d4ed8, #6366f1)";
    }

    statusDiv.textContent = text;
    statusDiv.style.backgroundImage = gradient;
}

document.addEventListener("DOMContentLoaded", () => {
    const stateScript = document.getElementById("initial-state");
    if (!stateScript) return;

    let state = JSON.parse(stateScript.textContent);

    renderState(state);

    const btnStep = document.getElementById("btn-step");
    const btnAuto = document.getElementById("btn-auto");

    let autoRunning = false;
    let intervalId = null;

    function stopAuto() {
        autoRunning = false;
        if (btnAuto) btnAuto.textContent = "▶️ Auto";
        if (intervalId) {
            clearInterval(intervalId);
            intervalId = null;
        }
    }

    if (btnStep) {
        btnStep.addEventListener("click", () => {
            fetch("/step_json", { method: "POST" })
                .then((r) => r.json())
                .then((newState) => {
                    state = newState;
                    renderState(state);

                    if (state.done || state.agent.battery_level <= 0) {
                        stopAuto();
                    }
                })
                .catch((err) => console.error("Error en step_json:", err));
        });
    }

    if (btnAuto) {
        btnAuto.addEventListener("click", () => {
            autoRunning = !autoRunning;

            if (autoRunning) {
                btnAuto.textContent = "⏸ Pausar";
                intervalId = setInterval(() => {
                    fetch("/step_json", { method: "POST" })
                        .then((r) => r.json())
                        .then((newState) => {
                            state = newState;
                            renderState(state);

                            if (state.done || state.agent.battery_level <= 0) {
                                stopAuto();
                            }
                        })
                        .catch((err) => console.error("Error en step_json:", err));
                }, 400);
            } else {
                stopAuto();
            }
        });
    }
});
