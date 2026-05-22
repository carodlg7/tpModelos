import tkinter as tk
from tkinter import ttk, messagebox
import random

# --- CONFIGURACIÓN DE PLANTILLAS ---
TEMPLATES = {
    "Guía 1: 1PS Clásicos": {
        1: {
            "title": "P1: Sistema M/M/1 Base",
            "desc": "Llegadas y servicios uno a uno. Servidor estable sin abandonos.",
            "type": "1PS", "servers": 1, "arr": "45", "ser": "40",
            "breaks": False, "impatience": False, "priority": False, "security": False,
            "init_q": 0, "init_wait": 0, "limit_type": "Eventos", "limit_val": "30"
        },
        2: {
            "title": "P2: Servidor con Descansos",
            "desc": "El servidor trabaja durante un intervalo y descansa. El servicio se detiene y se reanuda.",
            "type": "1PS", "servers": 1, "arr": "45", "ser": "40",
            "breaks": True, "work": "100", "rest": "50",
            "impatience": False, "priority": False, "security": False,
            "init_q": 0, "init_wait": 0, "limit_type": "Eventos", "limit_val": "30"
        },
        3: {
            "title": "P3: Abandono de Cola",
            "desc": "Los clientes abandonan la cola si esperan más de un límite especificado.",
            "type": "1PS", "servers": 1, "arr": "45", "ser": "40",
            "breaks": False, "impatience": True, "max_wait": "120",
            "priority": False, "security": False,
            "init_q": 0, "init_wait": 0, "limit_type": "Eventos", "limit_val": "30"
        },
        4: {
            "title": "P4: Prioridades (A y B)",
            "desc": "Clientes A y B. Clientes A tienen prioridad de atención sobre clientes B.",
            "type": "1PS", "servers": 1, "arr": "45", "ser": "40",
            "breaks": False, "impatience": False, "priority": True, "security": False,
            "init_q": 0, "init_wait": 0, "limit_type": "Eventos", "limit_val": "30"
        },
        5: {
            "title": "P5: Zona de Seguridad",
            "desc": "El cliente debe trasladarse desde la cola al PS con un delay de traslado.",
            "type": "1PS", "servers": 1, "arr": "45", "ser": "40",
            "breaks": False, "impatience": False, "priority": False, "security": True, "travel": "15",
            "init_q": 0, "init_wait": 0, "limit_type": "Eventos", "limit_val": "30"
        }
    },
    "Guía 2: Multi-PS (+1PS)": {
        1: {
            "title": "Multi-PS P1: Subpuestos Independientes",
            "desc": "Tres tipos de servicios independientes. Cada uno tiene su propia cola y servidor.",
            "type": "Independientes", "servers": 3, "arr": "45, 25, 15", "ser": "40, 20, 10",
            "breaks": False, "impatience": False, "priority": False, "security": False,
            "init_q": 0, "init_wait": 0, "limit_type": "Eventos", "limit_val": "40"
        },
        2: {
            "title": "Multi-PS P2: Servidores en Paralelo",
            "desc": "Una sola cola compartida. Los clientes son atendidos por el primer puesto libre disponible (PS1, PS2 o PS3).",
            "type": "Paralelo", "servers": 3, "arr": "60", "ser": "240",
            "breaks": False, "impatience": False, "priority": False, "security": False,
            "init_q": 4, "init_wait": 0, "limit_type": "Eventos", "limit_val": "30"
        },
        3: {
            "title": "Multi-PS P3: Servidores Secuenciales (Tándem)",
            "desc": "Línea de producción en serie. Cola 1 -> PS1 -> Cola 2 -> PS2 -> Cola 3 -> PS3 -> Salida.",
            "type": "Secuencial", "servers": 3, "arr": "35", "ser": "20, 11, 7",
            "breaks": False, "impatience": False, "priority": False, "security": False,
            "init_q": 0, "init_wait": 0, "limit_type": "Tiempo", "limit_val": "300"
        }
    },
    "Guía 3: UNLaR 2026": {
        1: {
            "title": "UNLaR P1: Descansos + Impaciencia",
            "desc": "Llegadas/servicios de 1 min. Descansos cada 100s. Clientes abandonan si esperan 10 min (600s). Evalúa V(0) -> q=100 con 10s de espera previa.",
            "type": "1PS", "servers": 1, "arr": "60", "ser": "60",
            "breaks": True, "work": "100", "rest": "50",
            "impatience": True, "max_wait": "600", "priority": False, "security": False,
            "init_q": 100, "init_wait": 10, "limit_type": "Tiempo", "limit_val": "3600"
        },
        2: {
            "title": "UNLaR P2: Descarte en Producción",
            "desc": "Máquina produce piezas cada 60s. PS las procesa en 50+-10s. PS tiene descansos de 30s cada 5 min (300s). Descarte si espera > 3 min (180s).",
            "type": "1PS", "servers": 1, "arr": "60", "ser": "40-60",
            "breaks": True, "work": "300", "rest": "30",
            "impatience": True, "max_wait": "180", "priority": False, "security": False,
            "init_q": 0, "init_wait": 0, "limit_type": "Tiempo", "limit_val": "7200"
        },
        3: {
            "title": "UNLaR P3: Desvío Inmediato si está Ocupado",
            "desc": "Si la máquina está procesando, la pieza entrante no espera en cola; es desviada en ese mismo instante (tiempo de espera límite = 0s).",
            "type": "1PS", "servers": 1, "arr": "45", "ser": "40",
            "breaks": False, "impatience": True, "max_wait": "0", "priority": False, "security": False,
            "init_q": 0, "init_wait": 0, "limit_type": "Eventos", "limit_val": "40"
        },
        4: {
            "title": "UNLaR P4: Armado de Sillas en Tándem",
            "desc": "Población finita: 6 sillas iniciales. Procesos secuenciales: Armar (30-40 min), Lijar (10-20 min) y Lustrar (5-30 min).",
            "type": "Secuencial", "servers": 3, "arr": "999999", "ser": "30-40, 10-20, 5-30",
            "breaks": False, "impatience": False, "priority": False, "security": False,
            "init_q": 6, "init_wait": 0, "limit_type": "Tiempo", "limit_val": "21600"
        }
    }
}

# ==========================================
# CLASES DE ENTIDADES Y LOGICA (POO)
# ==========================================

class Cliente:
    """Clase que representa una Entidad (Cliente o Pieza de producción)"""
    def __init__(self, cliente_id, arrival_time, client_type="Normal"):
        self.id = cliente_id
        self.arrival_time = arrival_time
        self.type = client_type  # "Normal", "A", "B"
        self.abandoned = False
        self.finished_time = None

class Servidor:
    """Clase que representa un Puesto de Servicio (PS)"""
    def __init__(self, srv_id):
        self.id = srv_id
        self.busy = False
        self.present = True
        self.remanente = 0
        self.cliente_actual = None

    def iniciar_servicio(self, cliente):
        self.busy = True
        self.cliente_actual = cliente
        self.remanente = 0

    def finalizar_servicio(self):
        cli = self.cliente_actual
        self.busy = False
        self.cliente_actual = None
        self.remanente = 0
        return cli

    def pausar_servicio(self, curr_t, fin_servicio_time):
        self.present = False
        if self.busy:
            self.remanente = fin_servicio_time - curr_t
            self.busy = False
            return True  # Retorna True si interrumpió una actividad en progreso
        return False

    def reanudar_servicio(self):
        self.present = True
        if self.remanente > 0:
            self.busy = True
            return self.remanente
        return 0

class Cola:
    """Clase para gestionar las filas de espera con políticas FIFO y Prioridades"""
    def __init__(self, cola_id=0, con_prioridad=False):
        self.id = cola_id
        self.clientes = []
        self.con_prioridad = con_prioridad

    def encolar(self, cliente):
        self.clientes.append(cliente)

    def desencolar(self):
        if not self.clientes:
            return None
        if self.con_prioridad:
            # Clientes Tipo A tienen prioridad de atención absoluta sobre Tipo B
            idx_a = next((i for i, c in enumerate(self.clientes) if c.type == "A"), None)
            if idx_a is not None:
                return self.clientes.pop(idx_a)
        return self.clientes.pop(0)

    def remover_por_cliente_id(self, c_id):
        for i, c in enumerate(self.clientes):
            if c.id == c_id:
                return self.clientes.pop(i)
        return None

    def __len__(self):
        return len(self.clientes)

class Evento:
    """Clase para modelar una Actividad en la Lista de Eventos Futuros (FEL)"""
    def __init__(self, tipo, tiempo, srv_id=0, client=None, client_id=None, q_idx=0):
        self.tipo = tipo  # "LLEGADA", "FIN_SERV", "SALIDA_SRV", "LLEGADA_SRV", "LLEGADA_PS", "ABANDONO"
        self.tiempo = tiempo
        self.srv_id = srv_id
        self.client = client
        self.client_id = client_id
        self.q_idx = q_idx

# ==========================================
# MOTOR GENERAL DE SIMULACIÓN POR EVENTOS
# ==========================================

class MotorSimulacion:
    def __init__(self, parent_app):
        self.app = parent_app
        self.sys_type = parent_app.sys_type.get()
        self.n_srv = parent_app.servers_count.get()
        
        self.has_breaks = parent_app.has_breaks.get()
        self.has_impatience = parent_app.has_impatience.get()
        self.has_priority = parent_app.has_priority.get()
        self.has_security = parent_app.has_security.get()
        
        self.start_sec = parent_app.parse_time(parent_app.start_time.get())
        self.curr_t = self.start_sec
        
        self.fel = []
        self.history = {}
        self.next_client_id = 1
        
        # Parseo de Servidores que descansan
        self.break_target_str = parent_app.break_target.get()
        if self.break_target_str == "Todos":
            self.break_srv_ids = list(range(self.n_srv))
        elif self.break_target_str.startswith("Solo PS"):
            try:
                idx = int(self.break_target_str.split(" ")[-1]) - 1
                self.break_srv_ids = [idx] if idx < self.n_srv else []
            except:
                self.break_srv_ids = [0]
        else:
            self.break_srv_ids = []
        
        # Inicialización de Colas según Topología
        if self.sys_type in ["Independientes", "Secuencial"]:
            self.colas = [Cola(i, self.has_priority) for i in range(self.n_srv)]
        else:
            self.colas = [Cola(0, self.has_priority)]
            
        # Inicialización de Servidores
        self.servers = [Servidor(i) for i in range(self.n_srv)]
        
        # Variables de control lógico de estados
        self.security_occupied = False
        self.abandonos_count = 0
        self.atendidos_count = 0
        self.desviados_count = 0
        self.descansos_ocurridos = 0
        self.tiempo_segundo_descanso = 99999999
        self.atendidos_antes_segundo_descanso = 0

    def parsear_rango_tiempo(self, input_str, idx=0):
        input_str = input_str.strip()
        if "," in input_str:
            parts = input_str.split(",")
            target = parts[idx] if idx < len(parts) else parts[-1]
            return self._evaluar_expresion_tiempo(target)
        return self._evaluar_expresion_tiempo(input_str)

    def _evaluar_expresion_tiempo(self, s):
        s = s.strip()
        if "+-" in s:
            base, dev = map(float, s.split("+-"))
            return random.randint(max(0, int(base - dev)), int(base + dev))
        if "-" in s:
            low, high = map(float, s.split("-"))
            return random.randint(int(low), int(high))
        return int(float(s))

    def inicializar_v0(self):
        init_q = self.app.init_q_size.get()
        init_wait = self.app.init_wait_sec.get()
        
        if init_q > 0:
            for _ in range(init_q):
                c_arr = self.curr_t - init_wait
                c_id = self.next_client_id
                self.next_client_id += 1
                
                cli = Cliente(c_id, c_arr, "Normal")
                self.history[c_id] = cli
                self.colas[0].encolar(cli)
                
                # Planificar impaciencia inicial
                if self.has_impatience:
                    limit = self.parsear_rango_tiempo(self.app.max_wait.get(), 0)
                    if limit > 0:
                        self.fel.append(Evento("ABANDONO", c_arr + limit, client_id=c_id, q_idx=0))

        # Programar Primeras Llegadas
        if self.sys_type == "Independientes":
            for i in range(self.n_srv):
                self.fel.append(Evento(f"LLEGADA_{i}", self.curr_t))
        elif self.sys_type == "Secuencial" and self.app.arr_interval.get() == "999999":
            # Población finita sin nuevos flujos externos (UNLaR P4 Sillas)
            pass
        else:
            self.fel.append(Evento("LLEGADA", self.curr_t))

        # Programar primer ciclo de descansos para los servidores seleccionados
        if self.has_breaks:
            for s_id in self.break_srv_ids:
                w_time = self.parsear_rango_tiempo(self.app.work_time.get(), s_id)
                self.fel.append(Evento("SALIDA_SRV", self.curr_t + w_time, srv_id=s_id))

    def ejecutar_paso(self):
        if not self.fel:
            return None
        self.fel.sort(key=lambda x: x.tiempo)
        ev = self.fel.pop(0)
        self.curr_t = ev.tiempo

        # --- ENRUTADOR DE EVENTOS (POLIMORFISMO DE LOGICA) ---
        if ev.tipo in ["LLEGADA", "LLEGADA_A", "LLEGADA_B"]:
            self._evento_llegada(ev)
        elif ev.tipo.startswith("LLEGADA_") and not ev.tipo.endswith("_SRV") and not ev.tipo.endswith("_PS"):
            self._evento_llegada_independiente(ev)
        elif "FIN_SERV" in ev.tipo:
            self._evento_fin_servicio(ev)
        elif ev.tipo == "LLEGADA_PS":
            self._evento_llegada_ps(ev)
        elif ev.tipo == "ABANDONO":
            self._evento_abandono(ev)
        elif ev.tipo == "SALIDA_SRV":
            self._evento_salida_servidor(ev)
        elif ev.tipo == "LLEGADA_SRV":
            self._evento_llegada_servidor(ev)

        return ev

    # --- CONTROLADORES DE EVENTO ---

    def _evento_llegada(self, ev):
        c_id = self.next_client_id
        self.next_client_id += 1
        c_type = "A" if ev.tipo == "LLEGADA_A" else ("B" if ev.tipo == "LLEGADA_B" else "Normal")
        cliente = Cliente(c_id, self.curr_t, c_type)
        self.history[c_id] = cliente

        # Agenda siguiente arribo externo
        if not (self.sys_type == "Secuencial" and self.app.arr_interval.get() == "999999"):
            next_t = "LLEGADA"
            if self.has_priority:
                next_t = "LLEGADA_A" if random.random() > 0.5 else "LLEGADA_B"
            self.fel.append(Evento(next_t, self.curr_t + self.parsear_rango_tiempo(self.app.arr_interval.get(), 0)))

        # Desvío inmediato si ocupado (UNLaR P3)
        if self.has_impatience and self.app.max_wait.get().strip() == "0":
            if any(s.busy for s in self.servers):
                self.desviados_count += 1
                cliente.abandoned = True
                ev.tipo = "LLEGADA_DESVIADA"
                return
            else:
                srv = self.servers[0]
                srv.iniciar_servicio(cliente)
                self.fel.append(Evento("FIN_SERV", self.curr_t + self.parsear_rango_tiempo(self.app.ser_duration.get(), 0), srv_id=0))
                return

        # Zona de Seguridad (P5)
        if self.has_security:
            if not any(s.busy for s in self.servers) and not self.security_occupied:
                self.security_occupied = True
                self.fel.append(Evento("LLEGADA_PS", self.curr_t + self.parsear_rango_tiempo(self.app.travel_time.get(), 0), client=cliente))
            else:
                self.colas[0].encolar(cliente)
            return

        # Servidores Paralelos
        if self.sys_type == "Paralelo":
            free_s = next((s for s in self.servers if not s.busy and s.present), None)
            if free_s:
                free_s.iniciar_servicio(cliente)
                self.fel.append(Evento(f"FIN_SERV_{free_s.id}", self.curr_t + self.parsear_rango_tiempo(self.app.ser_duration.get(), free_s.id), srv_id=free_s.id))
            else:
                self.colas[0].encolar(cliente)
                if self.has_impatience:
                    self.fel.append(Evento("ABANDONO", self.curr_t + self.parsear_rango_tiempo(self.app.max_wait.get(), 0), client_id=c_id, q_idx=0))
            return

        # Servidores Secuenciales
        if self.sys_type == "Secuencial":
            self.colas[0].encolar(cliente)
            srv = self.servers[0]
            if not srv.busy and srv.present:
                srv.iniciar_servicio(self.colas[0].desencolar())
                self.fel.append(Evento("FIN_SERV_0", self.curr_t + self.parsear_rango_tiempo(self.app.ser_duration.get(), 0), srv_id=0))
            return

        # 1PS Estándar
        srv = self.servers[0]
        if not srv.busy and srv.present:
            srv.iniciar_servicio(cliente)
            self.fel.append(Evento("FIN_SERV", self.curr_t + self.parsear_rango_tiempo(self.app.ser_duration.get(), 0), srv_id=0))
        else:
            self.colas[0].encolar(cliente)
            if self.has_impatience:
                self.fel.append(Evento("ABANDONO", self.curr_t + self.parsear_rango_tiempo(self.app.max_wait.get(), 0), client_id=c_id, q_idx=0))

    def _evento_llegada_independiente(self, ev):
        idx = int(ev.tipo.split("_")[1])
        c_id = self.next_client_id
        self.next_client_id += 1
        cliente = Cliente(c_id, self.curr_t, "Normal")
        self.history[c_id] = cliente

        # Reprogramar llegada en canal
        self.fel.append(Evento(f"LLEGADA_{idx}", self.curr_t + self.parsear_rango_tiempo(self.app.arr_interval.get(), idx)))

        srv = self.servers[idx]
        if not srv.busy and srv.present:
            srv.iniciar_servicio(cliente)
            self.fel.append(Evento(f"FIN_SERV_{idx}", self.curr_t + self.parsear_rango_tiempo(self.app.ser_duration.get(), idx), srv_id=idx))
        else:
            self.colas[idx].encolar(cliente)

    def _evento_fin_servicio(self, ev):
        srv_id = ev.srv_id
        srv = self.servers[srv_id]
        cli_terminado = srv.finalizar_servicio()

        if cli_terminado:
            cli_terminado.finished_time = self.curr_t
            self.atendidos_count += 1
            if self.curr_t < self.tiempo_segundo_descanso:
                self.atendidos_antes_segundo_descanso += 1

        # Comportamiento Secuencial (Tándem)
        if self.sys_type == "Secuencial":
            next_s = srv_id + 1
            if next_s < self.n_srv:
                cli_terminado.arrival_time = self.curr_t
                self.colas[next_s].encolar(cli_terminado)
                
                next_srv = self.servers[next_s]
                if not next_srv["busy"] if isinstance(next_srv, dict) else not next_srv.busy:
                    if next_srv.present:
                        next_srv.iniciar_servicio(self.colas[next_s].desencolar())
                        self.fel.append(Evento(f"FIN_SERV_{next_s}", self.curr_t + self.parsear_rango_tiempo(self.app.ser_duration.get(), next_s), srv_id=next_s))

            # Servidor actual atiende el siguiente de su propia cola
            if len(self.colas[srv_id]) > 0 and srv.present:
                srv.iniciar_servicio(self.colas[srv_id].desencolar())
                self.fel.append(Evento(f"FIN_SERV_{srv_id}", self.curr_t + self.parsear_rango_tiempo(self.app.ser_duration.get(), srv_id), srv_id=srv_id))

        # Comportamiento Zona de Seguridad (P5)
        elif self.has_security:
            self.security_occupied = False
            if len(self.colas[0]) > 0:
                self.security_occupied = True
                self.fel.append(Evento("LLEGADA_PS", self.curr_t + self.parsear_rango_tiempo(self.app.travel_time.get(), 0), client=self.colas[0].desencolar()))

        # Sistemas de Canal Único o Servidores en Paralelo
        else:
            q_idx = srv_id if self.sys_type == "Independientes" else 0
            active_q = self.colas[q_idx]

            if len(active_q) > 0 and srv.present:
                next_c = active_q.desencolar()
                
                if self.has_impatience:
                    # Limpiar el evento de abandono que ya no ocurrirá
                    self.fel = [x for x in self.fel if not (x.tipo == "ABANDONO" and x.client_id == next_c.id)]

                srv.iniciar_servicio(next_c)
                f_ev = f"FIN_SERV_{srv_id}" if self.sys_type in ["Independientes", "Paralelo"] else "FIN_SERV"
                self.fel.append(Evento(f_ev, self.curr_t + self.parsear_rango_tiempo(self.app.ser_duration.get(), srv_id), srv_id=srv_id))

    def _evento_llegada_ps(self, ev):
        self.security_occupied = False
        srv = self.servers[0]
        srv.iniciar_servicio(ev.client)
        self.fel.append(Evento("FIN_SERV", self.curr_t + self.parsear_rango_tiempo(self.app.ser_duration.get(), 0), srv_id=0))

    def _evento_abandono(self, ev):
        q_idx = ev.q_idx
        cli_removido = self.colas[q_idx].remover_por_cliente_id(ev.client_id)
        if cli_removido:
            cli_removido.abandoned = True
            self.abandonos_count += 1

    def _evento_salida_servidor(self, ev):
        srv_id = ev.srv_id
        srv = self.servers[srv_id]
        
        # Detener servicio en curso buscando el tiempo restante del srv_id correspondiente
        target_ev = "FIN_SERV" if self.sys_type == "1PS" else f"FIN_SERV_{srv_id}"
        is_busy = srv.pausar_servicio(self.curr_t, next((x.tiempo for x in self.fel if x.tipo == target_ev and x.srv_id == srv_id), 0))
        if is_busy:
            # Eliminar el evento de Fin de servicio de este servidor de la lista FEL
            self.fel = [x for x in self.fel if not (x.tipo == target_ev and x.srv_id == srv_id)]

        self.descansos_ocurridos += 1
        if self.descansos_ocurridos == 2:
            self.tiempo_segundo_descanso = self.curr_t

        self.fel.append(Evento("LLEGADA_SRV", self.curr_t + self.parsear_rango_tiempo(self.app.rest_time.get(), srv_id), srv_id=srv_id))

    def _evento_llegada_servidor(self, ev):
        srv_id = ev.srv_id
        srv = self.servers[srv_id]
        
        # Reprogramar siguiente salida si está habilitado para descansar
        if srv_id in self.break_srv_ids:
            w_time = self.parsear_rango_tiempo(self.app.work_time.get(), srv_id)
            self.fel.append(Evento("SALIDA_SRV", self.curr_t + w_time, srv_id=srv_id))

        remanente = srv.reanudar_servicio()
        if remanente > 0:
            target_ev = "FIN_SERV" if self.sys_type == "1PS" else f"FIN_SERV_{srv_id}"
            self.fel.append(Evento(target_ev, self.curr_t + remanente, srv_id=srv_id))
        elif not srv.busy:
            # Atender siguiente si quedó libre durante la ausencia
            q_idx = srv_id if self.sys_type == "Independientes" else 0
            active_q = self.colas[q_idx]
            if len(active_q) > 0:
                next_c = active_q.desencolar()
                if self.has_impatience:
                    self.fel = [x for x in self.fel if not (x.tipo == "ABANDONO" and x.client_id == next_c.id)]
                
                srv.iniciar_servicio(next_c)
                target_ev = "FIN_SERV" if self.sys_type == "1PS" else f"FIN_SERV_{srv_id}"
                self.fel.append(Evento(target_ev, self.curr_t + self.parsear_rango_tiempo(self.app.ser_duration.get(), srv_id), srv_id=srv_id))

# ==========================================
# INTERFAZ GRÁFICA DE ESCRITORIO (TKINTER)
# ==========================================

class SimuladorColasApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Simulador General de Sistemas de Colas - UNLaR 2026")
        self.root.geometry("1400x820")
        self.root.configure(bg="#f8fafc")

        # Variables de control de UI
        self.sys_type = tk.StringVar(value="1PS")
        self.servers_count = tk.IntVar(value=1)
        self.arr_interval = tk.StringVar(value="45")
        self.ser_duration = tk.StringVar(value="40")
        
        self.has_breaks = tk.BooleanVar(value=False)
        self.work_time = tk.StringVar(value="100")
        self.rest_time = tk.StringVar(value="50")
        self.break_target = tk.StringVar(value="Todos") # Objetivo de descanso
        
        self.has_impatience = tk.BooleanVar(value=False)
        self.max_wait = tk.StringVar(value="120")
        
        self.has_priority = tk.BooleanVar(value=False)
        self.has_security = tk.BooleanVar(value=False)
        self.travel_time = tk.StringVar(value="15")
        
        self.init_q_size = tk.IntVar(value=0)
        self.init_wait_sec = tk.IntVar(value=0)
        
        self.limit_type = tk.StringVar(value="Eventos")
        self.limit_val = tk.StringVar(value="30")
        self.start_time = tk.StringVar(value="08:00:00")

        self.setup_ui()
        self.load_template(None)

        # Monitorear cambios en la cantidad de servidores para actualizar la UI de descansos
        self.servers_count.trace_add("write", lambda *args: self.actualizar_combobox_descansos())

    def setup_ui(self):
        self.root.grid_columnconfigure(0, weight=1, minsize=320)
        self.root.grid_columnconfigure(1, weight=1, minsize=350)
        self.root.grid_columnconfigure(2, weight=2, minsize=650)
        self.root.grid_rowconfigure(0, weight=1)

        # COLUMNA 1: Selección de Problemas y Enunciado
        col1 = tk.Frame(self.root, bg="white", relief="flat", padx=15, pady=15, highlightbackground="#e2e8f0", highlightthickness=1)
        col1.grid(row=0, column=0, sticky="nsew", padx=4, pady=4)

        tk.Label(col1, text="1. SELECCIONAR CASO", font=("Segoe UI", 11, "bold"), bg="white", fg="#4f46e5").pack(anchor="w", pady=(0, 10))

        tk.Label(col1, text="Guía de Trabajos Prácticos:", bg="white", font=("Segoe UI", 9, "bold")).pack(anchor="w")
        self.guide_combo = ttk.Combobox(col1, values=list(TEMPLATES.keys()), state="readonly")
        self.guide_combo.current(0)
        self.guide_combo.pack(fill="x", pady=(0, 10))
        self.guide_combo.bind("<<ComboboxSelected>>", self.on_guide_change)

        tk.Label(col1, text="Problema de la Guía:", bg="white", font=("Segoe UI", 9, "bold")).pack(anchor="w")
        self.problem_combo = ttk.Combobox(col1, state="readonly")
        self.problem_combo.pack(fill="x", pady=(0, 15))
        self.problem_combo.bind("<<ComboboxSelected>>", self.on_problem_change)

        desc_lbl_frame = tk.LabelFrame(col1, text="Enunciado y Reglas de Negocio", bg="#f8fafc", font=("Segoe UI", 8, "bold"), relief="flat")
        desc_lbl_frame.pack(fill="both", expand=True, pady=10)
        
        self.desc_text = tk.Text(desc_lbl_frame, bg="#f8fafc", fg="#334155", font=("Segoe UI", 9, "italic"), wrap="word", relief="flat", padx=5, pady=5)
        self.desc_text.pack(fill="both", expand=True)

        help_box = tk.Frame(col1, bg="#eff6ff", highlightbackground="#bfdbfe", highlightthickness=1, padx=10, pady=10)
        help_box.pack(fill="x", side="bottom", pady=5)
        tk.Label(help_box, text="SOPORTE DE TIEMPOS ALEATORIOS", font=("Segoe UI", 8, "bold"), bg="#eff6ff", fg="#1e40af").pack(anchor="w")
        tk.Label(help_box, text="• Fijo: 45\n• Rango: 40-60\n• Uniforme: 50+-10\n• Múltiples PS (por comas): 40, 20, 10", 
                 font=("Segoe UI", 8), bg="#eff6ff", fg="#1e40af", justify="left").pack(anchor="w", pady=2)

        # COLUMNA 2: Personalización de Parámetros
        col2 = tk.Frame(self.root, bg="white", relief="flat", padx=15, pady=15, highlightbackground="#e2e8f0", highlightthickness=1)
        col2.grid(row=0, column=1, sticky="nsew", padx=4, pady=4)

        tk.Label(col2, text="2. AJUSTES DEL MOTOR", font=("Segoe UI", 11, "bold"), bg="white", fg="#4f46e5").pack(anchor="w", pady=(0, 10))

        s_frame = tk.LabelFrame(col2, text="Arquitectura de Servidores", bg="white", font=("Segoe UI", 8, "bold"), relief="solid", borderwidth=1, padx=8, pady=8)
        s_frame.pack(fill="x", pady=5)

        tk.Label(s_frame, text="Topología del Sistema:", bg="white", font=("Segoe UI", 8)).grid(row=0, column=0, sticky="w")
        self.topo_combo = ttk.Combobox(s_frame, textvariable=self.sys_type, values=["1PS", "Independientes", "Paralelo", "Secuencial"], state="readonly", width=15)
        self.topo_combo.grid(row=0, column=1, sticky="e", pady=2)

        tk.Label(s_frame, text="Cantidad de Puestos (PS):", bg="white", font=("Segoe UI", 8)).grid(row=1, column=0, sticky="w")
        self.srv_spin = tk.Spinbox(s_frame, from_=1, to=10, textvariable=self.servers_count, width=5)
        self.srv_spin.grid(row=1, column=1, sticky="e", pady=2)

        b_frame = tk.LabelFrame(col2, text="Intervalos de Tiempo", bg="white", font=("Segoe UI", 8, "bold"), relief="solid", borderwidth=1, padx=8, pady=8)
        b_frame.pack(fill="x", pady=5)

        tk.Label(b_frame, text="Llegada de Clientes (seg):", bg="white", font=("Segoe UI", 8)).grid(row=0, column=0, sticky="w")
        tk.Entry(b_frame, textvariable=self.arr_interval, width=15).grid(row=0, column=1, sticky="e", pady=2)

        tk.Label(b_frame, text="Duración del Servicio (seg):", bg="white", font=("Segoe UI", 8)).grid(row=1, column=0, sticky="w")
        tk.Entry(b_frame, textvariable=self.ser_duration, width=15).grid(row=1, column=1, sticky="e", pady=2)

        m_frame = tk.LabelFrame(col2, text="Eventos Especiales y Modificadores", bg="white", font=("Segoe UI", 8, "bold"), relief="solid", borderwidth=1, padx=8, pady=8)
        m_frame.pack(fill="x", pady=5)

        tk.Checkbutton(m_frame, text="Servidor con Descansos (Roturas)", variable=self.has_breaks, bg="white", font=("Segoe UI", 8, "bold")).pack(anchor="w")
        self.breaks_subframe = tk.Frame(m_frame, bg="white")
        self.breaks_subframe.pack(fill="x", padx=15, pady=2)
        
        tk.Label(self.breaks_subframe, text="Trabaja:", bg="white", font=("Segoe UI", 8)).grid(row=0, column=0, sticky="w")
        tk.Entry(self.breaks_subframe, textvariable=self.work_time, width=8).grid(row=0, column=1, padx=2, sticky="w")
        tk.Label(self.breaks_subframe, text="Descansa:", bg="white", font=("Segoe UI", 8)).grid(row=0, column=2, sticky="w")
        tk.Entry(self.breaks_subframe, textvariable=self.rest_time, width=8).grid(row=0, column=3, padx=2, sticky="w")
        
        # Selector de Servidor que Descansa
        tk.Label(self.breaks_subframe, text="Aplica a:", bg="white", font=("Segoe UI", 8)).grid(row=1, column=0, pady=4, sticky="w")
        self.break_target_combo = ttk.Combobox(self.breaks_subframe, textvariable=self.break_target, state="readonly", width=12)
        self.break_target_combo.grid(row=1, column=1, columnspan=3, pady=4, sticky="ew")

        tk.Checkbutton(m_frame, text="Clientes con Impaciencia / Abandono", variable=self.has_impatience, bg="white", font=("Segoe UI", 8, "bold")).pack(anchor="w", pady=(5,0))
        self.imp_subframe = tk.Frame(m_frame, bg="white")
        self.imp_subframe.pack(fill="x", padx=15, pady=2)
        tk.Label(self.imp_subframe, text="Tiempo límite en Cola (seg):", bg="white", font=("Segoe UI", 8)).grid(row=0, column=0)
        tk.Entry(self.imp_subframe, textvariable=self.max_wait, width=10).grid(row=0, column=1, padx=5)

        tk.Checkbutton(m_frame, text="Clientes con Prioridad (Cola A y B)", variable=self.has_priority, bg="white", font=("Segoe UI", 8, "bold")).pack(anchor="w", pady=(5,0))
        
        tk.Checkbutton(m_frame, text="Zona de Seguridad (Delay Traslado)", variable=self.has_security, bg="white", font=("Segoe UI", 8, "bold")).pack(anchor="w", pady=(5,0))
        self.sec_subframe = tk.Frame(m_frame, bg="white")
        self.sec_subframe.pack(fill="x", padx=15, pady=2)
        tk.Label(self.sec_subframe, text="Tiempo de traslado (seg):", bg="white", font=("Segoe UI", 8)).grid(row=0, column=0)
        tk.Entry(self.sec_subframe, textvariable=self.travel_time, width=10).grid(row=0, column=1, padx=5)

        v0_frame = tk.LabelFrame(col2, text="Condiciones Iniciales V(0)", bg="white", font=("Segoe UI", 8, "bold"), relief="solid", borderwidth=1, padx=8, pady=8)
        v0_frame.pack(fill="x", pady=5)
        
        tk.Label(v0_frame, text="Cola inicial (q):", bg="white", font=("Segoe UI", 8)).grid(row=0, column=0, sticky="w")
        tk.Entry(v0_frame, textvariable=self.init_q_size, width=10).grid(row=0, column=1, sticky="e", pady=2)
        
        tk.Label(v0_frame, text="Espera previa en cola (seg):", bg="white", font=("Segoe UI", 8)).grid(row=1, column=0, sticky="w")
        tk.Entry(v0_frame, textvariable=self.init_wait_sec, width=10).grid(row=1, column=1, sticky="e", pady=2)

        l_frame = tk.LabelFrame(col2, text="Parada del Experimento", bg="white", font=("Segoe UI", 8, "bold"), relief="solid", borderwidth=1, padx=8, pady=8)
        l_frame.pack(fill="x", pady=5)

        self.limit_combo = ttk.Combobox(l_frame, textvariable=self.limit_type, values=["Eventos", "Tiempo"], state="readonly", width=10)
        self.limit_combo.grid(row=0, column=0, pady=2)
        tk.Entry(l_frame, textvariable=self.limit_val, width=12).grid(row=0, column=1, padx=5, pady=2)

        self.btn_run = tk.Button(col2, text="🚀 EJECUTAR SIMULACIÓN", command=self.run_simulation, 
                                 bg="#4f46e5", fg="white", font=("Segoe UI", 10, "bold"), relief="flat", pady=10, cursor="hand2")
        self.btn_run.pack(side="bottom", fill="x", pady=5)

        # COLUMNA 3: Matriz de Estados y Métricas
        col3 = tk.Frame(self.root, bg="#f1f5f9", padx=15, pady=15)
        col3.grid(row=0, column=2, sticky="nsew", padx=4, pady=4)

        logs_frame = tk.Frame(col3, bg="#f1f5f9")
        logs_frame.pack(fill="both", expand=True)

        tk.Label(logs_frame, text="MATRIZ DE ESTADOS DE SIMULACIÓN", font=("Segoe UI", 11, "bold"), bg="#f1f5f9", fg="#1e293b").pack(anchor="w", pady=(0, 5))

        self.tree_frame = tk.Frame(logs_frame)
        self.tree_frame.pack(fill="both", expand=True)

        self.metrics_frame = tk.LabelFrame(col3, text="📊 Métricas y Respuestas de la Guía", font=("Segoe UI", 9, "bold"), bg="white", relief="solid", borderwidth=1, padx=15, pady=10)
        self.metrics_frame.pack(fill="x", side="bottom", pady=(10, 0))

        self.lbl_abandonos = tk.Label(self.metrics_frame, text="• Abandonos Totales: -", font=("Segoe UI", 9), bg="white")
        self.lbl_abandonos.pack(anchor="w")
        self.lbl_servidos = tk.Label(self.metrics_frame, text="• Clientes Atendidos Totales: -", font=("Segoe UI", 9), bg="white")
        self.lbl_servidos.pack(anchor="w")
        
        self.ans_unlar_a = tk.Label(self.metrics_frame, text="• Rta A: -", font=("Segoe UI", 9, "bold"), bg="white", fg="#4f46e5")
        self.ans_unlar_a.pack(anchor="w", pady=(4,0))
        self.ans_unlar_b = tk.Label(self.metrics_frame, text="• Rta B: -", font=("Segoe UI", 9, "bold"), bg="white", fg="#4f46e5")
        self.ans_unlar_b.pack(anchor="w")

    def actualizar_combobox_descansos(self):
        """Actualiza dinámicamente las opciones del selector de descanso según la cantidad de puestos"""
        try:
            n = self.servers_count.get()
        except:
            n = 1
        vals = ["Todos"]
        for i in range(n):
            vals.append(f"Solo PS {i+1}")
        
        self.break_target_combo.config(values=vals)
        if self.break_target.get() not in vals:
            self.break_target.set("Todos")

    def on_guide_change(self, event):
        guide = self.guide_combo.get()
        problems = list(TEMPLATES[guide].keys())
        self.problem_combo.config(values=[f"Problema {p}" for p in problems])
        self.problem_combo.current(0)
        self.on_problem_change(None)

    def on_problem_change(self, event):
        guide = self.guide_combo.get()
        prob_num = int(self.problem_combo.get().split(" ")[1])
        template = TEMPLATES[guide][prob_num]
        
        self.desc_text.delete("1.0", tk.END)
        self.desc_text.insert(tk.END, f"{template['title']}\n\n{template['desc']}")
        self.load_template(template)

    def load_template(self, t):
        if t is None:
            t = TEMPLATES["Guía 1: 1PS Clásicos"][1]
            self.guide_combo.current(0)
            self.on_guide_change(None)
            return

        self.sys_type.set(t["type"])
        self.servers_count.set(t["servers"])
        self.arr_interval.set(t["arr"])
        self.ser_duration.set(t["ser"])
        
        self.has_breaks.set(t["breaks"])
        if t["breaks"]:
            self.work_time.set(t["work"])
            self.rest_time.set(t["rest"])
        
        self.has_impatience.set(t["impatience"])
        if t["impatience"]:
            self.max_wait.set(t["max_wait"])
            
        self.has_priority.set(t["priority"])
        
        self.has_security.set(t["security"])
        if t["security"]:
            self.travel_time.set(t["travel"])
            
        self.init_q_size.set(t["init_q"])
        self.init_wait_sec.set(t["init_wait"])
        
        self.limit_type.set(t["limit_type"])
        self.limit_val.set(t["limit_val"])
        
        # Forzar restauración del objetivo de descanso por defecto al cargar plantilla
        self.break_target.set("Todos")
        self.actualizar_combobox_descansos()

    def format_time(self, seconds):
        h = int(seconds // 3600)
        m = int((seconds % 3600) // 60)
        s = int(seconds % 60)
        return f"{h:02d}:{m:02d}:{s:02d}"

    def parse_time(self, t_str):
        h, m, s = map(int, t_str.split(":"))
        return h * 3600 + m * 60 + s

    def run_simulation(self):
        """Instancia el motor OOP y ejecuta la simulación registrando las iteraciones"""
        for widget in self.tree_frame.winfo_children():
            widget.destroy()

        columns = ["Hora", "Evento", "Próx. Llegada", "Próx. Fin Serv"]
        syst = self.sys_type.get()
        n_srv = self.servers_count.get()

        if self.has_breaks.get():
            columns.append("Pausa/Rem.")
        columns.append("Colas")
        columns.append("Est. Servidores")
        if self.has_security.get():
            columns.append("Z. Seg.")

        self.tree = ttk.Treeview(self.tree_frame, columns=columns, show="headings")
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=100, anchor="center")
            
        sb = ttk.Scrollbar(self.tree_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=sb.set)
        self.tree.pack(side="left", expand=True, fill="both")
        sb.pack(side="right", fill="y")

        # INSTANCIA DEL MOTOR (POO)
        motor = MotorSimulacion(self)
        motor.inicializar_v0()

        # Condición de Parada
        lim_type = self.limit_type.get()
        lim_val = motor.parsear_rango_tiempo(self.limit_val.get())
        
        iterations = 0
        safety_max = 2000

        while iterations < safety_max:
            # Evaluar límites de parada del experimento
            if not motor.fel:
                break
            motor.fel.sort(key=lambda x: x.tiempo)
            if lim_type == "Tiempo" and motor.fel[0].tiempo > motor.start_sec + lim_val:
                break
            if lim_type == "Eventos" and iterations >= lim_val:
                break

            # Procesamiento polimórfico del evento más próximo
            ev = motor.ejecutar_paso()
            if not ev:
                break

            # --- RENDERIZADO EN TABLA ---
            n_l = next((x.tiempo for x in motor.fel if "LLEGADA" in x.tipo), None)
            n_f = next((x.tiempo for x in motor.fel if "FIN_SERV" in x.tipo or x.tipo == "LLEGADA_PS"), None)

            row = [
                self.format_time(motor.curr_t),
                ev.tipo,
                self.format_time(n_l) if n_l else "--",
                self.format_time(n_f) if n_f else "--"
            ]

            # Remanente (Solo P2)
            if motor.has_breaks:
                row.append(f"{int(motor.servers[0].remanente)}s" if motor.servers[0].remanente > 0 else "-")

            # Colas
            if syst in ["Independientes", "Secuencial"]:
                row.append(" / ".join(str(len(q)) for q in motor.colas))
            elif motor.has_priority:
                q_a = sum(1 for c in motor.colas[0].clientes if c.type == "A")
                q_b = sum(1 for c in motor.colas[0].clientes if c.type == "B")
                row.append(f"A:{q_a} B:{q_b}")
            else:
                row.append(len(motor.colas[0]))

            # Estado Servidores
            states = []
            for s in motor.servers:
                if not s.present:
                    states.append("Desc")
                else:
                    states.append("1" if s.busy else "0")
            row.append(" | ".join(states))

            # Zona Seguridad
            if motor.has_security:
                row.append("1" if motor.security_occupied else "0")

            self.tree.insert("", "end", values=row)

            # Limpiar remanente tras renderizar la reanudación
            if ev.tipo == "LLEGADA_SRV":
                motor.servers[ev.srv_id].remanente = 0

            iterations += 1

        # --- ACTUALIZAR MÉTRICAS GENERALES Y DE EXAMEN ---
        self.lbl_abandonos.config(text=f"• Abandonos Totales (Clientes/Piezas): {motor.abandonos_count + motor.desviados_count}")
        self.lbl_servidos.config(text=f"• Clientes Atendidos Totales: {motor.atendidos_count}")

        # Respuestas automáticas analíticas para UNLaR
        hist_values = list(motor.history.values())
        rta_a_val = sum(1 for c in hist_values if c.abandoned and c.arrival_time <= motor.start_sec + 3600)
        self.ans_unlar_a.config(text=f"• Rta A (Abandonos en 1 hora): {rta_a_val} unidades descartadas/desviadas.")
        
        self.ans_unlar_b.config(text=f"• Rta B (Atendidos antes de 2do descanso): {motor.atendidos_antes_segundo_descanso} unidades.")

        if syst == "Secuencial":
            self.ans_unlar_a.config(text=f"• Sillas terminadas completas (Lustradas): {motor.atendidos_count} unidades.")
            self.ans_unlar_b.config(text=f"• Colas secuenciales restantes: " + " | ".join(f"Cola {i}: {len(q)}" for i, q in enumerate(motor.colas)))
        elif motor.has_impatience and self.max_wait.get().strip() == "0":
            self.ans_unlar_a.config(text=f"• Relación de Piezas: {motor.atendidos_count} Procesadas vs {motor.desviados_count} Desviadas.")
            pct = (motor.desviados_count / max(1, motor.desviados_count + motor.atendidos_count)) * 100
            self.ans_unlar_b.config(text=f"• Proporción de desvíos: {pct:.1f}% de la producción.")

if __name__ == "__main__":
    root = tk.Tk()
    app = SimuladorColasApp(root)
    root.mainloop()