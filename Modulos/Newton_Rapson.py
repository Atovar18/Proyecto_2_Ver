import numpy as np
import sympy as sp
import pdb
import time
import pandas as pd
import math
from Modulos import Carga_Zip
  
def newtonRaphson(Convergencia, max_iter,y_bus,p_gen,p_load,q_gen,q_load,v_bar,bar_type, Z_zip, I_zip, P_zip):

    # Toma de tiempo del método.
    inicio = time.time()
    
    # Copia de las variables originales para no afectar los valores originales.
    p_gen2 = p_gen.copy()
    p_gen = np.array(p_gen2)
    p_load2 = p_load.copy()
    P_carga = p_load2.copy()
    p_load = np.array(p_load2)
    q_gen2 = q_gen.copy()
    q_gen = np.array(q_gen2)
    q_load2 = q_load.copy()
    q_load = np.array(q_load2)
    Q_carga = q_load2.copy ()
    y_bus2 = y_bus.copy()
    y_bus = np.matrix(y_bus2)
    Voltaje = np.zeros ((len(v_bar)),dtype=complex)
    for i in range(len(v_bar)):
        Voltaje[i] = v_bar[i] + 0*1j
    voltajes_barras = Voltaje.copy()
    
    
    # Variables auxiliares.
    error = 0
    Delta_P = np.zeros((len(y_bus)),dtype=object)
    Delta_Q = np.zeros((len(y_bus)),dtype=object)
    valores = {}
    indice_borrar_SL = []
    indice_borrar_PV = []
    
    # Potencias especificas.
    p_especificada = p_gen - p_load; p_return = p_especificada
    q_especifica = q_gen - q_load; q_return = q_especifica

    # Separamos la Matriz Y_bus en modulos y angulos de los fasores.
    ybus_modulos = abs(y_bus)
    ybus_angulos = np.angle(y_bus)
    
    #Voltajes
    Voltaje_modulo = sp.Matrix(abs(voltajes_barras))
    Voltaje_angulo = sp.Matrix(np.arctan2(np.imag(voltajes_barras),np.real(voltajes_barras)))
    values_bf = Voltaje_angulo.col_join(Voltaje_modulo)

    # Creamos las variables simbolicas a sustituir.
    # Voltajes --> 'V1, V2, V3'
    vol_var = [sp.symbols(f'V{i+1}') for i in range(len(voltajes_barras))]
    
    # Angulos ---> 'alpha1, alpha2, alpha3'
    ang_var = [sp.symbols(f'alpha{i+1}') for i in range(len(voltajes_barras))]

    # Ecuaciones de simbolicas.
    # Ecuaciones de ▲P y ▲Q
    for i in range(len(bar_type)):
        if bar_type[i] == "SL":
            indice_borrar_SL.append(i)
        elif bar_type[i] == "PQ":
            for j in range(len(bar_type)):
                Delta_P[i] += vol_var[i]*ybus_modulos[i,j]*vol_var[j]*sp.cos(ybus_angulos[i,j] - ang_var[i] + ang_var[j])
                Delta_Q[i] -= vol_var[i]*ybus_modulos[i,j]*vol_var[j]*sp.sin(ybus_angulos[i,j] - ang_var[i] + ang_var[j])
                
        elif bar_type[i] == "PV":
            for j in range(len(bar_type)):
                Delta_P[i] += vol_var[i]*ybus_modulos[i,j]*vol_var[j]*sp.cos(ybus_angulos[i,j] - ang_var[i] + ang_var[j])
            indice_borrar_PV.append(i)

    # Valores a no eliminar
    no_borrar_SL = set([i for i, _ in enumerate(Voltaje_modulo) if i not in indice_borrar_SL])
    no_borrar_PV = set([i for i, _ in enumerate(Voltaje_modulo) if i not in indice_borrar_PV])

    # Borramos los datos extras de las variables que no necesitamos.
    Delta_P = np.delete(Delta_P,indice_borrar_SL)
    Delta_P2 = Delta_P.copy ()
    Delta_Q = np.delete(Delta_Q,indice_borrar_SL + indice_borrar_PV)
    Delta_Q2 = Delta_Q.copy()
    v_mod = sp.Matrix(np.delete(Voltaje_modulo,indice_borrar_PV + indice_borrar_SL))
    v_ang = sp.Matrix(np.delete(Voltaje_angulo,indice_borrar_SL))
    p_especificada = np.delete(p_especificada,indice_borrar_SL)
    q_especifica = np.delete(q_especifica,indice_borrar_SL + indice_borrar_PV)
    vol_var = np.delete(vol_var,indice_borrar_PV + indice_borrar_SL)
    ang_var = np.delete(ang_var, indice_borrar_SL)

    #Añadiendo la potencia especifica a cada ecuacion de potencia
    Delta_P = sp.Matrix(p_especificada) - sp.Matrix(Delta_P)
    Delta_Q = sp.Matrix(q_especifica) - sp.Matrix(Delta_Q)

    # ------------------------------------------- Matriz Jacobiana -------------------------------------------------------------------------------------------
    #jacobianos de potencia activa
    JdeltaPalpha = Delta_P.jacobian([valores for valores in ang_var])
    JdeltaPvolt = Delta_P.jacobian([valores for valores in vol_var]) 
    jacobian_p = JdeltaPalpha.row_join(JdeltaPvolt)
    #Jacobiano de potencia reactiva
    JdeltaQalpha = Delta_Q.jacobian([valores for valores in ang_var])
    JdeltaQvolt = Delta_Q.jacobian([valores for valores in vol_var])
    jacobian_q = JdeltaQalpha.row_join(JdeltaQvolt)

    #Uniendo valores
    values_bf = v_ang.col_join(v_mod)
    Jacobian = jacobian_p.col_join(jacobian_q)
    f_powers = Delta_P.col_join(Delta_Q)
    values_next = sp.zeros(values_bf.rows,values_bf.cols)
    indice = 0

    # ---------------------------------------------------------------- Bucle iterativo -----------------------------------------------------------------------------------
    for k in range(max_iter):
        for i in range(len(Voltaje_modulo)):
            valores[f'V{i+1}'] = Voltaje_modulo[i]
            valores[f'alpha{i+1}'] = Voltaje_angulo[i]
        indice += 1
        # Sustituimos valores
        Jacobian = Jacobian.subs(valores)
        Jacobian_eval = Jacobian.inv()
        f_eval = f_powers.subs(valores)

        # Expresion de NR
        values_next = values_bf - Jacobian_eval*f_eval
        error = max(abs(values_next - values_bf))

        # Actualizacion de variables
        #modulos de voltajes
        k=1 #iterador auxiliar
        for i in list(no_borrar_SL.intersection(no_borrar_PV)):
            Voltaje_modulo[i] = values_next[(len(v_ang)-1)+k]
            k += 1
            
        k=0 #iterador auxiliar
        for i in list(no_borrar_SL):
            Voltaje_angulo[i] = values_next[k]
            k += 1
        values_bf = values_next.copy()
        
        # Convertimos en una variable float64, para efectos de calculos
        Voltajes_modulos =  np.array(Voltaje_modulo).astype(np.float64)
        
        # Aplanar la lista si es necesario (en caso de que sea una matriz 2D).
        flat_list = [item for sublist in Voltajes_modulos for item in sublist]

        # Crear una Series de pandas a partir de la lista.
        Voltajes_modulos = pd.Series(flat_list)
        
        # Asegurarse de que P_carga y Q_carga sean del tipo correcto.
        P_carga = P_carga.astype(np.float64)
        Q_carga = Q_carga.astype(np.float64)
        
        # Determinamos las nuevas P y Q de carga según el modelo ZIP.
        p_especificada, q_especifica, P_carga, Q_carga = Carga_Zip.Cargas_Variables(P_carga, Q_carga, p_gen2, q_gen2, Voltajes_modulos, Z_zip, I_zip, P_zip)
        p_return = p_especificada
        q_return = q_especifica
        p_especificada = np.array (p_especificada)
        q_especifica = np.array (q_especifica) 
        
        # Eliminamos los valores correspondiente a las barras SL y PV en las nuevas potencias activas y reactivas.
        p_especificada = np.delete(p_especificada,indice_borrar_SL)
        q_especifica = np.delete(q_especifica,indice_borrar_SL + indice_borrar_PV)      

        # Añadiendo la potencia especifica a cada ecuacion de potencia
        Delta_P = sp.Matrix(p_especificada) - sp.Matrix(Delta_P2)
        Delta_Q = sp.Matrix(q_especifica) - sp.Matrix(Delta_Q2)
        
        # Juntamos las nuevas ecuaciones delta, para sustituir los nuevos valores del proceso iterativo.
        f_powers = Delta_P.col_join(Delta_Q)
        
        if error < Convergencia:
            break
    
    # Convertimos las variables de salida.
    Modulos = Voltaje_modulo.copy()
    Angulos = Voltaje_angulo.copy ()
    angulo_radianes_series = np.array(Angulos)
    modulo_series = np.array(Modulos)
    
    # Aplanar la lista si es necesario (en caso de que sea una matriz 2D).
    Lista_modulos = [item for sublist in modulo_series for item in sublist]
    Lista_angulos = [item for sublist in angulo_radianes_series for item in sublist]
    
    # Asegurarse de que Lista_modulos y Lista_angulos sean listas de float
    Lista_modulos = [float(x) for x in Lista_modulos]
    Lista_angulos = [float(x) for x in Lista_angulos]

    # Convertir las listas a Series de pandas con el tipo de dato float
    angulo_radianes_series = pd.Series(Lista_angulos, dtype=float)
    modulo_series = pd.Series(Lista_modulos, dtype=float)

    Fasor = []
    for i in range(len(angulo_radianes_series)):
        parte_real = modulo_series[i] * np.cos(angulo_radianes_series[i])
        parte_imaginaria = modulo_series[i] * np.sin(angulo_radianes_series[i])
        Fasor.append(complex(parte_real, parte_imaginaria))

    Fasor = pd.Series(Fasor)

    # Convertir los ángulos de radianes a grados
    angulo_grados_series = np.degrees(angulo_radianes_series)

    # Finalizamos la rutina.
    Final = time.time()
    
    # Tiempo de ejecucion.
    Tiempo = Final - inicio
    print (f"El tiempo de ejecucion en NR fue de {Tiempo:.3f} segundos.")
    print ()
    
    return modulo_series, angulo_grados_series, p_return, q_return, indice, error, Fasor