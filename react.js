import React, { useState, useEffect, useMemo } from 'react';
import { 
  Play, 
  Settings, 
  Table as TableIcon, 
  Info, 
  Users, 
  Clock, 
  ShieldAlert, 
  Coffee,
  ArrowRight,
  RefreshCw,
  PauseCircle,
  HelpCircle
} from 'lucide-react';

// --- UTILIDADES ---
const formatTime = (seconds) => {
  const h = Math.floor(seconds / 3600);
  const m = Math.floor((seconds % 3600) / 60);
  const s = seconds % 60;
  return `${h}:${m.toString().padStart(2, '0')}:${s.toString().padStart(2, '0')}`;
};

const parseTime = (timeStr) => {
  const [h, m, s] = timeStr.split(':').map(Number);
  return h * 3600 + m * 60 + s;
};

/**
 * Obtiene un valor numérico a partir de un input que puede ser un número fijo o un rango (min-max).
 */
const getVal = (input) => {
  const str = String(input).trim();
  if (str.includes('-')) {
    const parts = str.split('-');
    const min = parseInt(parts[0]);
    const max = parseInt(parts[1]);
    if (!isNaN(min) && !isNaN(max)) {
      return Math.floor(Math.random() * (max - min + 1)) + min;
    }
  }
  const val = parseInt(str);
  return isNaN(val) ? 0 : val;
};

// --- CONFIGURACIÓN DE PROBLEMAS ---
const PROBLEMS = {
  1: {
    name: "Problema 1: M/M/1 Básico",
    desc: "Llegadas y servicios uno a uno. Servidor siempre presente.",
    events: ["Llegada", "Fin Servicio"],
    state: ["Estado PS", "Cola"]
  },
  2: {
    name: "Problema 2: Servidor con Descansos",
    desc: "El servicio se detiene si el servidor sale y se reanuda al volver.",
    events: ["Llegada", "Fin Servicio", "Salida Servidor", "Llegada Servidor"],
    state: ["Estado PS", "Cola", "Presencia Servidor"]
  },
  3: {
    name: "Problema 3: Abandono de Cola",
    desc: "Los clientes abandonan si esperan más de un tiempo límite.",
    events: ["Llegada", "Fin Servicio", "Abandono de Cola"],
    state: ["Estado PS", "Cola", "Tiempos de Abandono"]
  },
  4: {
    name: "Problema 4: Prioridad (A y B)",
    desc: "Clientes A tienen prioridad sobre clientes B.",
    events: ["Llegada A", "Llegada B", "Fin Servicio"],
    state: ["Estado PS", "Cola A", "Cola B"]
  },
  5: {
    name: "Problema 5: Zona de Seguridad",
    desc: "Distancia entre cola y puesto de servicio (PS).",
    events: ["Llegada", "Llegada a PS", "Fin Servicio"],
    state: ["Estado PS", "Cola", "Zona Seguridad"]
  }
};

const App = () => {
  const [activeProblem, setActiveProblem] = useState(1);
  const [params, setParams] = useState({
    startTime: "08:00:00",
    maxEvents: 30,
    arrivalInterval: "45",
    serviceDuration: "40",
    workDuration: "100",
    restDuration: "50",
    maxWaitTime: "120",
    travelToPSTime: "15"
  });

  const [simulationData, setSimulationData] = useState([]);
  const [isSimulating, setIsSimulating] = useState(false);

  const runSimulation = () => {
    setIsSimulating(true);
    let currentTime = parseTime(params.startTime);
    let state = {
      psOccupied: false,
      queue: [], 
      queueA: [], 
      queueB: [], 
      serverPresent: true,
      securityZoneOccupied: false,
      remainingServiceTime: 0,
    };

    let FEL = []; 

    // Programar primera llegada
    FEL.push({ type: 'LLEGADA', time: currentTime });
    
    if (activeProblem === 2) {
      FEL.push({ type: 'SALIDA_SERVIDOR', time: currentTime + getVal(params.workDuration) });
    }

    const logs = [];
    let iterations = 0;

    while (FEL.length > 0 && iterations < params.maxEvents) {
      FEL.sort((a, b) => a.time - b.time);
      const currentEvent = FEL.shift();
      currentTime = currentEvent.time;

      const logEntry = {
        time: currentTime,
        event: currentEvent.type,
        nextLlegada: FEL.find(e => e.type.startsWith('LLEGADA'))?.time,
        nextFinServicio: FEL.find(e => e.type === 'FIN_SERVICIO' || e.type === 'LLEGADA_PS')?.time,
        state: { ...state, queue: [...state.queue], queueA: [...state.queueA], queueB: [...state.queueB] },
        remaining: state.remainingServiceTime
      };

      switch (currentEvent.type) {
        case 'LLEGADA':
        case 'LLEGADA_A':
        case 'LLEGADA_B':
          const nextType = activeProblem === 4 ? (Math.random() > 0.5 ? 'LLEGADA_A' : 'LLEGADA_B') : 'LLEGADA';
          FEL.push({ type: nextType, time: currentTime + getVal(params.arrivalInterval) });

          if (activeProblem === 4) {
            const isA = currentEvent.type === 'LLEGADA_A';
            if (!state.psOccupied) {
              state.psOccupied = true;
              FEL.push({ type: 'FIN_SERVICIO', time: currentTime + getVal(params.serviceDuration) });
            } else {
              isA ? state.queueA.push(currentTime) : state.queueB.push(currentTime);
            }
          } else if (activeProblem === 5) {
            if (!state.psOccupied && !state.securityZoneOccupied) {
              state.securityZoneOccupied = true;
              FEL.push({ type: 'LLEGADA_PS', time: currentTime + getVal(params.travelToPSTime) });
            } else {
              state.queue.push(currentTime);
            }
          } else if (activeProblem === 3) {
            if (!state.psOccupied) {
              state.psOccupied = true;
              FEL.push({ type: 'FIN_SERVICIO', time: currentTime + getVal(params.serviceDuration) });
            } else {
              const waitLimit = getVal(params.maxWaitTime);
              state.queue.push(currentTime);
              FEL.push({ type: 'ABANDONO', time: currentTime + waitLimit, arrivalTime: currentTime });
            }
          } else if (activeProblem === 2) {
            if (!state.psOccupied && state.serverPresent) {
              state.psOccupied = true;
              FEL.push({ type: 'FIN_SERVICIO', time: currentTime + getVal(params.serviceDuration) });
            } else {
              state.queue.push(currentTime);
            }
          } else {
            if (!state.psOccupied) {
              state.psOccupied = true;
              FEL.push({ type: 'FIN_SERVICIO', time: currentTime + getVal(params.serviceDuration) });
            } else {
              state.queue.push(currentTime);
            }
          }
          break;

        case 'FIN_SERVICIO':
          state.psOccupied = false;
          state.remainingServiceTime = 0;
          
          if (activeProblem === 4) {
            if (state.queueA.length > 0) {
              state.queueA.shift();
              state.psOccupied = true;
              FEL.push({ type: 'FIN_SERVICIO', time: currentTime + getVal(params.serviceDuration) });
            } else if (state.queueB.length > 0) {
              state.queueB.shift();
              state.psOccupied = true;
              FEL.push({ type: 'FIN_SERVICIO', time: currentTime + getVal(params.serviceDuration) });
            }
          } else if (activeProblem === 5) {
            state.securityZoneOccupied = false;
            if (state.queue.length > 0) {
              state.queue.shift();
              state.securityZoneOccupied = true;
              FEL.push({ type: 'LLEGADA_PS', time: currentTime + getVal(params.travelToPSTime) });
            }
          } else {
            if (state.queue.length > 0 && (activeProblem !== 2 || state.serverPresent)) {
              const nextInQueue = state.queue.shift();
              if (activeProblem === 3) {
                const idx = FEL.findIndex(e => e.type === 'ABANDONO' && e.arrivalTime === nextInQueue);
                if (idx > -1) FEL.splice(idx, 1);
              }
              state.psOccupied = true;
              FEL.push({ type: 'FIN_SERVICIO', time: currentTime + getVal(params.serviceDuration) });
            }
          }
          break;

        case 'SALIDA_SERVIDOR':
          state.serverPresent = false;
          if (state.psOccupied) {
            const fsIdx = FEL.findIndex(e => e.type === 'FIN_SERVICIO');
            if (fsIdx > -1) {
              state.remainingServiceTime = FEL[fsIdx].time - currentTime;
              FEL.splice(fsIdx, 1);
            }
          }
          FEL.push({ type: 'LLEGADA_SERVIDOR', time: currentTime + getVal(params.restDuration) });
          break;

        case 'LLEGADA_SERVIDOR':
          state.serverPresent = true;
          FEL.push({ type: 'SALIDA_SERVIDOR', time: currentTime + getVal(params.workDuration) });
          
          if (state.remainingServiceTime > 0) {
            FEL.push({ type: 'FIN_SERVICIO', time: currentTime + state.remainingServiceTime });
          } else if (!state.psOccupied && state.queue.length > 0) {
            state.queue.shift();
            state.psOccupied = true;
            FEL.push({ type: 'FIN_SERVICIO', time: currentTime + getVal(params.serviceDuration) });
          }
          break;

        case 'LLEGADA_PS':
          state.securityZoneOccupied = false;
          state.psOccupied = true;
          FEL.push({ type: 'FIN_SERVICIO', time: currentTime + getVal(params.serviceDuration) });
          break;

        case 'ABANDONO':
          const qIdx = state.queue.indexOf(currentEvent.arrivalTime);
          if (qIdx > -1) state.queue.splice(qIdx, 1);
          break;
      }

      logs.push(logEntry);
      iterations++;
    }

    setSimulationData(logs);
    setIsSimulating(false);
  };

  return (
    <div className="min-h-screen bg-slate-50 text-slate-900 font-sans p-4 md:p-8">
      <header className="max-w-7xl mx-auto mb-8">
        <div className="flex items-center gap-3 mb-2">
          <div className="p-2 bg-indigo-600 rounded-lg text-white">
            <RefreshCw size={24} />
          </div>
          <h1 className="text-2xl font-bold text-slate-800">Simulador de Sistemas de Colas</h1>
        </div>
        <p className="text-slate-500">Configura y simula los 5 problemas clásicos con valores fijos o rangos aleatorios.</p>
      </header>

      <main className="max-w-7xl mx-auto grid grid-cols-1 lg:grid-cols-4 gap-6">
        
        <div className="lg:col-span-1 space-y-6">
          <section className="bg-white p-6 rounded-2xl shadow-sm border border-slate-200">
            <h2 className="text-sm font-semibold uppercase tracking-wider text-slate-400 mb-4 flex items-center gap-2">
              <Settings size={16} /> Configuración
            </h2>
            
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-slate-700 mb-1">Seleccionar Problema</label>
                <select 
                  className="w-full bg-slate-50 border border-slate-200 rounded-lg p-2 text-sm outline-none focus:ring-2 focus:ring-indigo-500"
                  value={activeProblem}
                  onChange={(e) => setActiveProblem(Number(e.target.value))}
                >
                  {Object.keys(PROBLEMS).map(id => (
                    <option key={id} value={id}>Problema {id}</option>
                  ))}
                </select>
                <p className="mt-2 text-[11px] text-slate-400 italic leading-tight">
                  {PROBLEMS[activeProblem].desc}
                </p>
              </div>

              <div className="p-3 bg-amber-50 rounded-xl border border-amber-100 flex items-start gap-2">
                <HelpCircle size={16} className="text-amber-500 shrink-0 mt-0.5" />
                <p className="text-[10px] text-amber-700 leading-tight">
                  Usa números (ej: <b>40</b>) o rangos (ej: <b>10-25</b>) para valores aleatorios en segundos.
                </p>
              </div>

              <div className="grid grid-cols-1 gap-3 pt-2">
                <div>
                  <label className="block text-xs font-medium text-slate-500 mb-1">Llegada (seg)</label>
                  <input type="text" className="w-full bg-slate-50 border border-slate-200 rounded-lg p-2 text-sm"
                    placeholder="ej: 10-30"
                    value={params.arrivalInterval} onChange={e => setParams({...params, arrivalInterval: e.target.value})}/>
                </div>
                <div>
                  <label className="block text-xs font-medium text-slate-500 mb-1">Servicio (seg)</label>
                  <input type="text" className="w-full bg-slate-50 border border-slate-200 rounded-lg p-2 text-sm"
                    placeholder="ej: 40"
                    value={params.serviceDuration} onChange={e => setParams({...params, serviceDuration: e.target.value})}/>
                </div>
              </div>

              {activeProblem === 2 && (
                <div className="space-y-3 p-3 bg-indigo-50/50 rounded-xl border border-indigo-100">
                  <div>
                    <label className="block text-xs font-medium text-indigo-700 mb-1">Trabaja (seg)</label>
                    <input type="text" className="w-full bg-white border border-indigo-200 rounded-lg p-2 text-sm" 
                      value={params.workDuration} onChange={e => setParams({...params, workDuration: e.target.value})}/>
                  </div>
                  <div>
                    <label className="block text-xs font-medium text-indigo-700 mb-1">Descansa (seg)</label>
                    <input type="text" className="w-full bg-white border border-indigo-200 rounded-lg p-2 text-sm" 
                      value={params.restDuration} onChange={e => setParams({...params, restDuration: e.target.value})}/>
                  </div>
                </div>
              )}

              {activeProblem === 3 && (
                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-1">Tiempo Máx. Espera (seg)</label>
                  <input type="text" className="w-full bg-slate-50 border border-slate-200 rounded-lg p-2 text-sm" 
                    value={params.maxWaitTime} onChange={e => setParams({...params, maxWaitTime: e.target.value})}/>
                </div>
              )}

              {activeProblem === 5 && (
                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-1">Traslado a PS (seg)</label>
                  <input type="text" className="w-full bg-slate-50 border border-slate-200 rounded-lg p-2 text-sm" 
                    value={params.travelToPSTime} onChange={e => setParams({...params, travelToPSTime: e.target.value})}/>
                </div>
              )}

              <div>
                <label className="block text-xs font-medium text-slate-500 mb-1">Eventos a simular</label>
                <input type="number" className="w-full bg-slate-50 border border-slate-200 rounded-lg p-2 text-sm" 
                  value={params.maxEvents} onChange={e => setParams({...params, maxEvents: Number(e.target.value)})}/>
              </div>

              <button 
                onClick={runSimulation}
                disabled={isSimulating}
                className="w-full bg-indigo-600 hover:bg-indigo-700 text-white font-bold py-3 rounded-xl transition-all flex items-center justify-center gap-2 shadow-lg shadow-indigo-100 disabled:opacity-50"
              >
                {isSimulating ? <RefreshCw className="animate-spin" size={18} /> : <Play size={18} />}
                Simular Caso
              </button>
            </div>
          </section>
        </div>

        <div className="lg:col-span-3">
          <section className="bg-white rounded-2xl shadow-sm border border-slate-200 overflow-hidden min-h-[600px]">
            <div className="p-6 border-b border-slate-100 flex justify-between items-center">
              <h2 className="text-lg font-bold text-slate-800 flex items-center gap-2">
                <TableIcon size={20} className="text-indigo-600" /> 
                {PROBLEMS[activeProblem].name}
              </h2>
            </div>

            <div className="overflow-x-auto">
              {simulationData.length > 0 ? (
                <table className="w-full text-left border-collapse">
                  <thead>
                    <tr className="bg-slate-50 text-slate-500 text-[10px] uppercase tracking-wider">
                      <th className="px-4 py-3 font-semibold">Hora</th>
                      <th className="px-4 py-3 font-semibold">Evento</th>
                      <th className="px-4 py-3 font-semibold">Próx. Llegada</th>
                      <th className="px-4 py-3 font-semibold">Próx. Fin Serv.</th>
                      
                      {activeProblem === 2 && <th className="px-4 py-3 font-semibold">Remanente</th>}
                      
                      <th className="px-4 py-3 font-semibold text-center">Cola</th>
                      <th className="px-4 py-3 font-semibold text-center">Est. PS</th>
                      
                      {activeProblem === 2 && <th className="px-4 py-3 font-semibold">Servidor</th>}
                      {activeProblem === 5 && <th className="px-4 py-3 font-semibold">Z. Seg.</th>}
                    </tr>
                  </thead>
                  <tbody className="text-sm divide-y divide-slate-50">
                    {simulationData.map((row, idx) => (
                      <tr key={idx} className={`hover:bg-indigo-50/30 transition-colors ${row.state.remainingServiceTime > 0 ? 'bg-amber-50/30' : ''}`}>
                        <td className="px-4 py-3 font-mono text-indigo-600 font-medium">{formatTime(row.time)}</td>
                        <td className="px-4 py-3">
                          <span className={`px-2 py-0.5 rounded text-[11px] font-bold ${
                            row.event.includes('LLEGADA') ? 'bg-green-100 text-green-700' :
                            row.event.includes('FIN') ? 'bg-blue-100 text-blue-700' :
                            row.event.includes('SALIDA') ? 'bg-red-100 text-red-700' :
                            'bg-amber-100 text-amber-700'
                          }`}>
                            {row.event}
                          </span>
                        </td>
                        <td className="px-4 py-3 text-slate-400 font-mono text-xs">{row.nextLlegada ? formatTime(row.nextLlegada) : '--:--:--'}</td>
                        <td className="px-4 py-3 text-slate-400 font-mono text-xs">{row.nextFinServicio ? formatTime(row.nextFinServicio) : '--:--:--'}</td>
                        
                        {activeProblem === 2 && (
                          <td className="px-4 py-3 font-mono text-xs text-amber-600">
                            {row.state.remainingServiceTime > 0 ? `${Math.round(row.state.remainingServiceTime)}s` : '-'}
                          </td>
                        )}

                        <td className="px-4 py-3 text-center font-bold">
                          {activeProblem === 4 ? (
                            <span className="text-[10px]">A:{row.state.queueA.length} B:{row.state.queueB.length}</span>
                          ) : row.state.queue.length}
                        </td>

                        <td className="px-4 py-3 text-center">
                          <div className={`mx-auto w-6 h-6 rounded-full flex items-center justify-center text-[11px] font-bold ${
                            row.state.psOccupied 
                              ? (activeProblem === 2 && !row.state.serverPresent ? 'bg-amber-100 text-amber-600 border border-amber-200' : 'bg-red-100 text-red-600') 
                              : 'bg-slate-100 text-slate-400'
                          }`}>
                            {row.state.psOccupied ? '1' : '0'}
                          </div>
                        </td>

                        {activeProblem === 2 && (
                          <td className="px-4 py-3">
                            {row.state.serverPresent ? 
                              <span className="text-[10px] text-green-600 font-bold uppercase tracking-tight">Presente</span> : 
                              <span className="text-[10px] text-red-400 font-bold uppercase tracking-tight italic">Descanso</span>}
                          </td>
                        )}

                        {activeProblem === 5 && (
                          <td className="px-4 py-3 text-center">
                             <div className={`mx-auto w-5 h-5 rounded flex items-center justify-center text-[10px] ${row.state.securityZoneOccupied ? 'bg-amber-100 text-amber-600' : 'bg-slate-100 text-slate-400'}`}>
                              {row.state.securityZoneOccupied ? '1' : '0'}
                            </div>
                          </td>
                        )}
                      </tr>
                    ))}
                  </tbody>
                </table>
              ) : (
                <div className="flex flex-col items-center justify-center py-20 text-slate-300">
                  <TableIcon size={48} className="mb-4 opacity-20" />
                  <p>Configura los parámetros y presiona "Simular Caso"</p>
                </div>
              )}
            </div>
          </section>
        </div>
      </main>
    </div>
  );
};

export default App;