from Modulos import Carga_Zip
import time 
import numpy as np
import pandas as pd
import sympy as sp


def Desacople (V_pu, Y_Bus, P_gen, P_demanda, Q_gen, Q_demanda, Bus_type, Max_iter, Convergencia, Z_zip, I_zip, P_zip):
    # Toma de tiempo del método.
    inicio = time.time()
    
    # Definimos las variables iniciales que deseamos.    
    error = 0
    Delta_P = np.zeros((len(Y_Bus)),dtype=object)
    Delta_Q = np.zeros((len(Y_Bus)),dtype=object)
    values = {}
    indice_borrar_SL = []
    indice_borrar_PV = []
    Voltaje = np.array (V_pu, dtype= complex)
    Voltaje = pd.Series (Voltaje) 
    indice = 0

    # Calculamos las potencias especificas.
    P_esp = P_gen - P_demanda; P_salida = P_esp
    Q_esp = Q_gen - Q_demanda; Q_salida = Q_esp

    # ------------- Armamos las matrices B, que nacen de la matriz Y_BUS. ---------------------------------
    # Modulo del numero complejo.
    ybus_modulos = abs (Y_Bus)
    # Angulo en rad del numero complejo.
    ybus_angulos = np.angle(Y_Bus)
    # Componente imaginaria.
    Imag_ybus = np.imag (Y_Bus)

    #Voltajes
    Voltaje_modulo = sp.Matrix(abs(Voltaje))
    Voltaje_angulo = sp.Matrix(np.arctan2(np.imag(Voltaje),np.real(Voltaje)))

    # --------------------- Creamos las incognitas symbolicas del proceso iterativo. ----------------------------------
    # Voltajes.
    # Voltajes --> 'V1, V2, V3'
    voltajes_var = [sp.symbols(f'V{i+1}') for i in range(len(Voltaje))]

    # Angulos.
    # Angulos ---> 'alpha1, alpha2, alpha3'
    angulos_var = [sp.symbols(f'alpha{i+1}') for i in range(len(Voltaje))]
        
    # ------------------------- Ecuaciones de simbolicas. --------------------------------------------------------
    # Ecuaciones de ▲P y ▲Q
    for i in range(len(Bus_type)):
        if Bus_type[i] == "SL":
            indice_borrar_SL.append(i)
            
        elif Bus_type[i] == "PQ":
            for j in range(len(Bus_type)):
                Delta_P[i] += voltajes_var[i]*ybus_modulos[i,j]*voltajes_var[j]*sp.cos(ybus_angulos[i,j] - angulos_var[i] + angulos_var[j])
                Delta_Q[i] -= voltajes_var[i]*ybus_modulos[i,j]*voltajes_var[j]*sp.sin(ybus_angulos[i,j] - angulos_var[i] + angulos_var[j])
                
        elif Bus_type[i] == "PV":
            for j in range(len(Bus_type)):
                Delta_P[i] += voltajes_var[i]*ybus_modulos[i,j]*voltajes_var[j]*sp.cos(ybus_angulos[i,j] - angulos_var[i] + angulos_var[j])
            indice_borrar_PV.append(i)
            
    # Valores a no eliminar
    no_borrar_SL = set([i for i, _ in enumerate(Voltaje_modulo) if i not in indice_borrar_SL])
    no_borrar_PV = set([i for i, _ in enumerate(Voltaje_modulo) if i not in indice_borrar_PV])

    #Añadiendo la potencia especifica a cada ecuacion de potencia
    Delta_P2 = Delta_P.copy ()
    Delta_Q2 = Delta_Q.copy ()
    Delta_P = sp.Matrix(P_esp) - sp.Matrix(Delta_P)
    Delta_Q = sp.Matrix(Q_esp) - sp.Matrix(Delta_Q)

    # Borramos los datos extras de las variables que no necesitamos.
    Delta_Q = np.delete(Delta_Q,indice_borrar_SL + indice_borrar_PV)
    v_mod = sp.Matrix(np.delete(Voltaje_modulo,indice_borrar_PV + indice_borrar_SL))
    v_ang = sp.Matrix(np.delete(Voltaje_angulo,indice_borrar_SL))
    P_esp = np.delete(P_esp,indice_borrar_SL)
    Q_esp = np.delete(Q_esp,indice_borrar_SL + indice_borrar_PV)
    voltajes_var = np.delete(voltajes_var,indice_borrar_PV + indice_borrar_SL)
    angulos_var = np.delete(angulos_var, indice_borrar_SL)

    # -------------------------- Construccion de las matrices de susceptancias. -------------------------------------------
    # Respecto al angúlo.
    b_angle = sp.Matrix(np.delete(Imag_ybus,list(indice_borrar_SL),axis=1))
    b_angle = sp.Matrix(np.delete(b_angle,list(indice_borrar_SL),axis=0))
    b_angle = b_angle.inv()

    # Respecto al modulo.
    b_mod = sp.Matrix(np.delete(Imag_ybus, list(indice_borrar_PV +indice_borrar_SL),axis=1))
    b_mod = sp.Matrix(np.delete(b_mod, list(indice_borrar_PV +indice_borrar_SL),axis=0))
    b_mod = b_mod.inv()



    #Vectores de ecuaciones delta
    deltaQV = sp.Matrix([Delta_Q[i]/abs(v_mod[i]) for i in range(len(v_mod))])
    deltaPV = sp.Matrix([Delta_P[i]/abs(Voltaje[i]) for i in range(len(Voltaje)) if i not in indice_borrar_SL])

    # ---------------------------------------------------------------- Bucle iterativo. -----------------------------------------------------------------------------------

    for w in range(Max_iter):
        for i in range(len(Voltaje_modulo)):
            values[f'V{i+1}'] = Voltaje_modulo[i]
            values[f'alpha{i+1}'] = Voltaje_angulo[i]
        
            
        # Sustituimos valores.
        f_eval_angle = deltaPV.subs(values)
        f_eval_mod = deltaQV.subs(values)
        indice += 1
        
        # Ecuaciones.
        values_next_angle = v_ang - b_angle*f_eval_angle
        values_next_mod = v_mod - b_mod*f_eval_mod
        
        # Comprobobamos los resultados.
        error_mod = max(abs(values_next_mod - v_mod))
        error_ang = max(abs(values_next_angle - v_ang))
        error = max(error_mod,error_ang)
        
        # Convierte la variable sympy.Float a un float de Python
        error_float = float(error)

        # Coloca una condición para romper el bucle si el valor es muy grande
        if error_float >= 1e+10:
            print("Valor muy alto encontrado, rompiendo el bucle.")
            break
            # Rompe el bucle o realiza alguna acción 
        
        # Condición de ruptura.
        if error < Convergencia:
            break
        
        # Sustitución de los resultados viejos por los nuevos.
        else:
                k=0
                for i in list(no_borrar_SL.intersection(no_borrar_PV)):
                    Voltaje_modulo[i] = values_next_mod[k]
                    k += 1
        
                k=0 #iterador auxiliar
                for i in list(no_borrar_SL):
                    Voltaje_angulo[i] = values_next_angle[k]
                    k += 1

                v_ang = values_next_angle.copy()
                v_mod = values_next_mod.copy()
                
                # Convertimos en una variable float64, para efectos de calculos
                Voltajes_modulos =  np.array(Voltaje_modulo).astype(np.float64)
                
                # Aplanar la lista si es necesario (en caso de que sea una matriz 2D).
                flat_list = [item for sublist in Voltajes_modulos for item in sublist]

                # Crear una Series de pandas a partir de la lista.
                Voltajes_modulos = pd.Series(flat_list)
                
                # Asegurarse de que P_carga y Q_carga sean del tipo correcto.
                P_carga = P_demanda.astype(np.float64)
                Q_carga = Q_demanda.astype(np.float64)
                
                # Determinamos las nuevas P y Q de carga según el modelo ZIP.
                p_especificada, q_especifica, P_carga, Q_carga = Carga_Zip.Cargas_Variables(P_carga, Q_carga, P_gen, Q_gen, Voltajes_modulos, Z_zip, I_zip, P_zip)
                P_salida = P_carga
                Q_salida = Q_carga
                p_especificada = np.array (p_especificada)
                q_especifica = np.array (q_especifica)    

                # Añadiendo la potencia especifica a cada ecuacion de potencia
                Delta_P = sp.Matrix(p_especificada) - sp.Matrix(Delta_P2)
                Delta_Q = sp.Matrix(q_especifica) - sp.Matrix(Delta_Q2) 
                
                # Borramos los datos extras de las variables que no necesitamos.
                Delta_Q = np.delete(Delta_Q,indice_borrar_SL + indice_borrar_PV)
                
                #Vectores de ecuaciones delta
                deltaQV = sp.Matrix([Delta_Q[i]/abs(v_mod[i]) for i in range(len(v_mod))])
                deltaPV = sp.Matrix([Delta_P[i]/abs(Voltaje[i]) for i in range(len(Voltaje)) if i not in indice_borrar_SL])
                
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
    print (f"El tiempo de ejecucion en FD fue de {Tiempo:.3f} segundos.")
    print ()  
    
    return modulo_series, angulo_grados_series, P_salida , Q_salida, indice, error, Fasor