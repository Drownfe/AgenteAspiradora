# 🧹 Agente Reactivo: Robot Aspiradora  
### Simulación interactiva con Python + Flask | Inteligencia Artificial | Proyecto académico  
Repositorio oficial → **https://github.com/Drownfe/AgenteAspiradora**

---

## 📌 Introducción

Este proyecto implementa un **agente reactivo simple** (tipo robot aspiradora) que opera dentro de un entorno simulado.  
El agente **percibe**, **decide** y **actúa** con base en reglas locales, sin memoria de largo plazo.

Incluye:

- 🧱 Obstáculos  
- 🟫 Zonas sucias  
- 🔌 Estación de carga  
- 🧹 Robot que decide y actúa en tiempo real  
- 🎨 Interfaz visual moderna

---

## 🎯 Objetivo

Demostrar el funcionamiento de un **agente reactivo** mediante reglas IF-THEN, aplicado a un robot aspiradora autónomo.

---

## 🧠 Arquitectura

```
AgenteAspiradora/
│
├── app.py
├── simulation/
│   └── simulator.py
├── agent/
│   ├── environment.py
│   └── robot_agent.py
├── static/
│   ├── css/styles.css
│   └── js/main.js
├── templates/
│   ├── base.html
│   └── index.html
└── README.md
```

---

## 🚀 Instalación

### 1️⃣ Clonar el repositorio
```
git clone https://github.com/Drownfe/AgenteAspiradora
cd AgenteAspiradora
```

### 2️⃣ (Opcional) Entorno virtual
```
python -m venv venv
source venv/bin/activate       # Linux/Mac
venv\Scripts\activate        # Windows
```

### 3️⃣ Instalar dependencias
```
pip install -r requirements.txt
```

---

## ▶️ Ejecutar la aplicación

```
python app.py
```

Abrir en navegador:

👉 http://127.0.0.1:5000/

---

## 🕹️ Cómo usar

### Panel izquierdo → Habitación
- 🧹 Robot  
- 🧱 Paredes  
- 🟫 Suciedad  
- 🔌 Base  
- ⬜ Limpio  

Botones:
- **Ejecutar un paso**
- **Auto** (simulación continua)
- **Reset**

### Panel derecho → Estado
- 🔋 Batería
- 🧽 Progreso de limpieza
- 🟫 Celdas sucias restantes
- 🧭 Orientación
- 👁 Percepciones
- 🎯 Acción tomada
- 🟢 Estado general

---

## 🤖 Reglas del Agente

1. Si batería baja **y no en base** → ir a base  
2. Si está en base y batería < 100% → recargar  
3. Si celda actual sucia → limpiar  
4. Si frente libre → avanzar  
5. Si izquierda libre → girar izquierda  
6. Si derecha libre → girar derecha  
7. Sino → girar hasta encontrar salida  

---

## 💡 Retorno a la base

El robot evalúa las 4 direcciones posibles y elige la que más reduce la distancia a la base, evitando atascos.

---

## 🎨 Interfaz

- Tema dark moderno  
- Barras de batería y progreso  
- Panel informativo tipo dashboard  
- Estado dinámico con emojis  
- Grid estilo “cartilla”  

---

## 🧪 Pruebas recomendadas

- Recorrido completo  
- Limpieza total  
- Administración de batería  
- Retorno correcto a base  
- No quedarse atascado  