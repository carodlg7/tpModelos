import tkinter as tk
from tkinter import ttk, messagebox
import random

# --- DATOS DE LOS PROBLEMAS ---
PROBLEMS_DATA = {
    1: {
        "title": "Problema 1: Sistema M/M/1 Estándar",
        "desc": "Los clientes llegan uno a uno a intervalos aleatorios para recibir servicio. Si el puesto de servicio (PS) está ocupado, hacen cola. Al terminar un servicio, el siguiente cliente ingresa instantáneamente. El servidor nunca abandona su puesto."
    },
    2: {
        "title": "Problema 2: Servidor con Descansos",
        "desc": "Igual al problema 1, pero el servidor trabaja durante intervalos aleatorios y descansa entre ellos. Si el servidor sale durante un servicio, el tiempo restante se pausa y se reanuda cuando el servidor regresa."
    },
    3: {
        "title": "Problema 3: Abandono por Impaciencia",
        "desc": "Igual que el problema 1, pero si un cliente espera en cola más de un tiempo determinado (ej. 10 minutos), abandona la cola y sale del sistema sin regresar."
    },
    4: {
        "title": "Problema 4: Prioridad (Tipos A y B)",
        "desc": "Llegan dos tipos de clientes. Los de tipo A tienen prioridad sobre los B para entrar al PS. No se discrimina entre tipos una vez que el cliente ya está dentro del PS recibiendo servicio."
    },
    5: {
        "title": "Problema 5: Zona de Seguridad",
        "desc": "El PS está alejado de la cola. Un cliente solo puede avanzar al PS cuando el anterior sale. Mientras el cliente camina hacia el PS (tiempo de traslado), la zona de seguridad está ocupada y nadie más puede avanzar."
    }
}

class SimuladorColasApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Simulador de Sistemas de Colas - Ingeniería en Sistemas")
        self.root.geometry("1200x800")
        self.root.configure(bg="#f1f5f9")

        # Variables de control
        self.active_problem = tk.IntVar(value=1)
        self.params = {
            "startTime": tk.StringVar(value="08:00:00"),
            "maxEvents": tk.StringVar(value="30"),
            "arrivalInterval": tk.StringVar(value="45"),
            "serviceDuration": tk.StringVar(value="40"),
            "workDuration": tk.StringVar(value="100"),
            "restDuration": tk.StringVar(value="50"),
            "maxWaitTime": tk.StringVar(value="120"),
            "travelToPSTime": tk.StringVar(value="15")
        }

        self.setup_ui()

    def setup_ui(self):
        # --- PANEL LATERAL (Sidebar) ---
        sidebar = tk.Frame(self.root, bg="white", width=350, relief="flat", padx=20, pady=20)
        sidebar.pack(side="left", fill="y")
        sidebar.pack_propagate(False)

        tk.Label(sidebar, text="CONFIGURACIÓN", font=("Segoe UI", 10, "bold"), bg="white", fg="#475569").pack(anchor="w", pady=(0, 10))

        # Selector
        tk.Label(sidebar, text="Seleccionar Problema:", bg="white", font=("Segoe UI", 9)).pack(anchor="w")
        self.problem_combo = ttk.Combobox(sidebar, values=[f"Problema {i}" for i in range(1, 6)], state="readonly")
        self.problem_combo.current(0)
        self.problem_combo.pack(fill="x", pady=(0, 10))
        self.problem_combo.bind("<<ComboboxSelected>>", self.on_problem_change)

        # CUADRO DE DESCRIPCIÓN
        desc_frame = tk.LabelFrame(sidebar, text="Descripción del Enunciado", font=("Segoe UI", 8, "bold"), bg="#f8fafc", padx=10, pady=10, relief="flat")
        desc_frame.pack(fill="x", pady=5)
        
        self.desc_label = tk.Label(desc_frame, text=PROBLEMS_DATA[1]["desc"], font=("Segoe UI", 9, "italic"), 
                                   bg="#f8fafc", fg="#334155", wraplength=280, justify="left")
        self.desc_label.pack(fill="x")

        # CUADRO DE AYUDA (Rangos Aleatorios)
        help_box = tk.Frame(sidebar, bg="#fffbeb", highlightbackground="#fef3c7", highlightthickness=1, padx=10, pady=10)
        help_box.pack(fill="x", pady=10)
        tk.Label(help_box, text="Tip: Usa '10-25' para rangos\naleatorios en segundos.", 
                 font=("Segoe UI", 8, "bold"), bg="#fffbeb", fg="#92400e").pack()

        # Inputs
        self.inputs_container = tk.Frame(sidebar, bg="white")
        self.inputs_container.pack(fill="x", pady=5)
        self.refresh_inputs()

        # Botón
        btn_simular = tk.Button(sidebar, text="Simular Sistema", command=self.run_simulation, 
                                bg="#4f46e5", fg="white", font=("Segoe UI", 10, "bold"), 
                                relief="flat", pady=12, cursor="hand2")
        btn_simular.pack(side="bottom", fill="x", pady=10)

        # --- PANEL PRINCIPAL ---
        self.main_panel = tk.Frame(self.root, bg="#f1f5f9", padx=20, pady=20)
        self.main_panel.pack(side="right", expand=True, fill="both")
        
        self.setup_table_panel()

    def on_problem_change(self, event):
        val = int(self.problem_combo.get().split(" ")[1])
        self.active_problem.set(val)
        # Actualizar descripción
        self.desc_label.config(text=PROBLEMS_DATA[val]["desc"])
        self.refresh_inputs()

    def refresh_inputs(self):
        for widget in self.inputs_container.winfo_children():
            widget.destroy()

        fields = [
            ("Intervalo Llegada (seg)", "arrivalInterval"),
            ("Tiempo Servicio (seg)", "serviceDuration"),
        ]

        p = self.active_problem.get()
        if p == 2:
            fields += [("Tiempo Trabajo (seg)", "workDuration"), ("Tiempo Descanso (seg)", "restDuration")]
        elif p == 3:
            fields += [("Límite Espera (seg)", "maxWaitTime")]
        elif p == 5:
            fields += [("Traslado a PS (seg)", "travelToPSTime")]
        
        fields.append(("Cantidad de Eventos", "maxEvents"))

        for label, key in fields:
            f = tk.Frame(self.inputs_container, bg="white")
            f.pack(fill="x", pady=2)
            tk.Label(f, text=label, bg="white", font=("Segoe UI", 8), fg="#64748b").pack(anchor="w")
            tk.Entry(f, textvariable=self.params[key], font=("Segoe UI", 9), relief="solid", borderwidth=1).pack(fill="x")

    def setup_table_panel(self):
        for widget in self.main_panel.winfo_children():
            widget.destroy()

        title_lbl = tk.Label(self.main_panel, text=PROBLEMS_DATA[self.active_problem.get()]["title"], 
                             font=("Segoe UI", 16, "bold"), bg="#f1f5f9", fg="#1e293b")
        title_lbl.pack(anchor="w", pady=(0, 20))

        # Columnas
        cols = ["Hora", "Evento", "Próx. Llegada", "Próx. Fin Serv"]
        p = self.active_problem.get()
        if p == 2: cols.append("Pausa/Rem.")
        cols.append("Cola")
        cols.append("Est. PS")
        if p == 2: cols.append("Servidor")
        if p == 5: cols.append("Z. Seg.")

        # Estilo de tabla
        style = ttk.Style()
        style.configure("Treeview.Heading", font=("Segoe UI", 9, "bold"))
        style.configure("Treeview", font=("Segoe UI", 9), rowheight=25)

        self.tree = ttk.Treeview(self.main_panel, columns=cols, show="headings")
        for col in cols:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=110, anchor="center")

        sb = ttk.Scrollbar(self.main_panel, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=sb.set)
        
        self.tree.pack(side="left", expand=True, fill="both")
        sb.pack(side="right", fill="y")

    def get_val(self, key):
        raw = self.params[key].get().strip()
        if "-" in raw:
            try:
                low, high = map(int, raw.split("-"))
                return random.randint(low, high)
            except: return 0
        try: return int(raw)
        except: return 0

    def format_time(self, seconds):
        return f"{int(seconds // 3600):02d}:{int((seconds % 3600) // 60):02d}:{int(seconds % 60):02d}"

    def parse_time(self, t_str):
        h, m, s = map(int, t_str.split(":"))
        return h * 3600 + m * 60 + s

    def run_simulation(self):
        self.setup_table_panel()
        p = self.active_problem.get()
        curr_t = self.parse_time(self.params["startTime"].get())
        max_ev = self.get_val("maxEvents")
        
        state = {
            "ps": False, "q": [], "qA": [], "qB": [], 
            "srv": True, "z_seg": False, "rem": 0
        }

        fel = [{"type": "LLEGADA", "time": curr_t}]
        if p == 2: fel.append({"type": "SALIDA_SRV", "time": curr_t + self.get_val("workDuration")})

        for _ in range(max_ev):
            if not fel: break
            fel.sort(key=lambda x: x["time"])
            ev = fel.pop(0)
            curr_t = ev["time"]

            # Lógica de procesamiento
            if ev["type"] in ["LLEGADA", "LLEGADA_A", "LLEGADA_B"]:
                nt = "LLEGADA"
                if p == 4: nt = "LLEGADA_A" if random.random() > 0.5 else "LLEGADA_B"
                fel.append({"type": nt, "time": curr_t + self.get_val("arrivalInterval")})

                if p == 4:
                    if not state["ps"]:
                        state["ps"] = True
                        fel.append({"type": "FIN_SERV", "time": curr_t + self.get_val("serviceDuration")})
                    else:
                        (state["qA"] if ev["type"]=="LLEGADA_A" else state["qB"]).append(curr_t)
                elif p == 5:
                    if not state["ps"] and not state["z_seg"]:
                        state["z_seg"] = True
                        fel.append({"type": "LLEGADA_PS", "time": curr_t + self.get_val("travelToPSTime")})
                    else:
                        state["q"].append(curr_t)
                elif p == 3:
                    if not state["ps"]:
                        state["ps"] = True
                        fel.append({"type": "FIN_SERV", "time": curr_t + self.get_val("serviceDuration")})
                    else:
                        state["q"].append(curr_t)
                        fel.append({"type": "ABANDONO", "time": curr_t + self.get_val("maxWaitTime"), "orig": curr_t})
                else: # P1 y P2
                    if not state["ps"] and (p != 2 or state["srv"]):
                        state["ps"] = True
                        fel.append({"type": "FIN_SERV", "time": curr_t + self.get_val("serviceDuration")})
                    else:
                        state["q"].append(curr_t)

            elif ev["type"] == "FIN_SERV":
                state["ps"] = False
                state["rem"] = 0
                if p == 4:
                    if state["qA"]:
                        state["qA"].pop(0); state["ps"] = True
                        fel.append({"type": "FIN_SERV", "time": curr_t + self.get_val("serviceDuration")})
                    elif state["qB"]:
                        state["qB"].pop(0); state["ps"] = True
                        fel.append({"type": "FIN_SERV", "time": curr_t + self.get_val("serviceDuration")})
                elif p == 5:
                    state["z_seg"] = False
                    if state["q"]:
                        state["q"].pop(0); state["z_seg"] = True
                        fel.append({"type": "LLEGADA_PS", "time": curr_t + self.get_val("travelToPSTime")})
                else:
                    if state["q"] and (p != 2 or state["srv"]):
                        target = state["q"].pop(0)
                        if p == 3: fel = [x for x in fel if not (x["type"]=="ABANDONO" and x["orig"]==target)]
                        state["ps"] = True
                        fel.append({"type": "FIN_SERV", "time": curr_t + self.get_val("serviceDuration")})

            elif ev["type"] == "SALIDA_SRV":
                state["srv"] = False
                if state["ps"]:
                    # Buscar si hay un fin de servicio programado para pausarlo
                    for i, x in enumerate(fel):
                        if x["type"] == "FIN_SERV":
                            state["rem"] = x["time"] - curr_t
                            fel.pop(i)
                            break
                fel.append({"type": "LLEGADA_SRV", "time": curr_t + self.get_val("restDuration")})

            elif ev["type"] == "LLEGADA_SRV":
                state["srv"] = True
                fel.append({"type": "SALIDA_SRV", "time": curr_t + self.get_val("workDuration")})
                
                if state["rem"] > 0:
                    # Reanudar servicio pausado
                    fel.append({"type": "FIN_SERV", "time": curr_t + state["rem"]})
                    # Importante: no resetear 'rem' aquí para que se vea en el log de esta fila, 
                    # se reseteará en el siguiente evento FIN_SERV
                elif not state["ps"] and state["q"]:
                    # Si estaba libre pero hay gente esperando, atender
                    state["q"].pop(0)
                    state["ps"] = True
                    fel.append({"type": "FIN_SERV", "time": curr_t + self.get_val("serviceDuration")})

            elif ev["type"] == "LLEGADA_PS":
                state["z_seg"] = False; state["ps"] = True
                fel.append({"type": "FIN_SERV", "time": curr_t + self.get_val("serviceDuration")})

            elif ev["type"] == "ABANDONO":
                if ev["orig"] in state["q"]: state["q"].remove(ev["orig"])

            # Render de la fila
            n_l = next((x["time"] for x in fel if x["type"] in ["LLEGADA", "LLEGADA_A", "LLEGADA_B"]), None)
            n_f = next((x["time"] for x in fel if x["type"] in ["FIN_SERV", "LLEGADA_PS"]), None)
            
            row = [self.format_time(curr_t), ev["type"], 
                   self.format_time(n_l) if n_l else "--", 
                   self.format_time(n_f) if n_f else "--"]
            
            if p == 2: row.append(f"{int(state['rem'])}s" if state['rem']>0 else "-")
            
            if p == 4:
                row.append(f"A:{len(state['qA'])} B:{len(state['qB'])}")
            else:
                row.append(len(state["q"]))
                
            row.append("1" if state["ps"] else "0")
            
            if p == 2: row.append("Pres." if state["srv"] else "Desc.")
            if p == 5: row.append("1" if state["z_seg"] else "0")
            
            self.tree.insert("", "end", values=row)
            
            # Limpiar remanente solo después de haberlo mostrado en el evento de llegada del servidor
            if ev["type"] == "LLEGADA_SRV":
                state["rem"] = 0

if __name__ == "__main__":
    root = tk.Tk()
    app = SimuladorColasApp(root)
    root.mainloop()