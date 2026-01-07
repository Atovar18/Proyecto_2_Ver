import numpy as np
import math as ma
import sympy as sp
import pandas as pd
import Modulos.Carga_Zip as Carga_Zip
import time

def Newton_Raphson(P_gen, Q_gen, P_demanda, Q_demanda, Angulos_grados, Modulo_V, Y_Bus, Bus_type, Convergencia, Max_iter, Z_zip, I_zip, P_zip):

    # Tomamos el tiempo del método.
    Inicio = time.time()

    # -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    #                                       Copiamos los datos, para evitar errores.
    # -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    P_gen_NR = P_gen.copy()
    Q_gen_NR = Q_gen.copy()
    P_demanda_NR = P_demanda.copy()
    Q_demanda_NR = Q_demanda.copy()
    Angulos_rad_NR = Angulos_grados.copy()
    Modulo_V_NR = Modulo_V.copy()
    Y_Bus_NR = Y_Bus.copy()
    Bus_type_NR = Bus_type.copy()
    Convergencia_NR = Convergencia
    Max_iter_NR = Max_iter
    Z_zip_NR = Z_zip.copy()
    I_zip_NR = I_zip.copy()
    P_zip_NR = P_zip.copy()

    # -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    #                                           Convertimos los angulos a radianes.
    # -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    for i in range(len(Angulos_rad_NR)):
        Angulos_rad_NR[i] = (Angulos_rad_NR[i])*(np.pi/180)

    # -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    #                                           Calculamos las potencias especificas.   
    # -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    P_espec_NR = P_gen_NR - P_demanda_NR
    Q_espec_NR = Q_gen_NR - Q_demanda_NR

    # -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    #                                           Separamos la matriz Ybus en modulo y angulo.
    # -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    Ybus_modulo = abs(Y_Bus_NR)
    Ybus_angulo = np.angle(Y_Bus_NR)

    # -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    #                                                          Voltajes iniciales.
    # -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    Voltajes_NR = np.zeros((len(Bus_type_NR)), dtype=complex)

    # Calculamos los voltajes complejos iniciales.
    for i in range(len(Bus_type_NR)):
        Voltajes_NR[i] = Modulo_V_NR[i]*(np.cos(Angulos_rad_NR[i]) + 1j*np.sin(Angulos_rad_NR[i]))
        
    # Separamos modulos y angulos de los voltajes iniciales.
    V_mod_NR = sp.Matrix(abs(Voltajes_NR))
    V_ang_NR = sp.Matrix(np.angle(Voltajes_NR))             
    """Usando el comando sp, para trabajar con matrices simbólicas."""
    Valores = V_ang_NR.col_join(V_mod_NR)  # Unimos los valores en una sola matriz.


    # -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    #                                                   Definimos las variables simbólicas.   
    # -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    # Voltajes.
    Voltaje_variable = [sp.symbols(f'V{i+1}') for i in range(len(Bus_type_NR))]

    # Angulos.
    Angulo_variable = [sp.symbols(f'Alpha{i+1}') for i in range(len(Bus_type_NR))]

    # --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    #                                                      # Ecuaciones de ▲P y ▲Q.
    # --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    # Variables auxiliares.
    indicePV_NR = []
    indiceSL_NR = []
    Delta_P_NR = np.zeros(len(Bus_type_NR), object)  # Inicializamos la lista de delta P.
    Delta_Q_NR = np.zeros(len(Bus_type_NR), object)  # Inicializamos la lista de delta Q.

    # Bucle para identificar los tipos de barra y formar las ecuaciones.
    for i in range (len(Bus_type_NR)):
        if Bus_type_NR[i] == 'SL':  # Barra SL.
            indiceSL_NR.append(i)
            
        elif Bus_type_NR[i] == 'PQ':  # Barra PQ.
            for j in range(len(Bus_type_NR)):
                Delta_P_NR[i] += Voltaje_variable[i]*Ybus_modulo[i,j]*Voltaje_variable[j]*sp.cos(-Ybus_angulo[i,j] + Angulo_variable[i] - Angulo_variable[j])
                Delta_Q_NR[i] += Voltaje_variable[i]*Ybus_modulo[i,j]*Voltaje_variable[j]*sp.sin(-Ybus_angulo[i,j] + Angulo_variable[i] - Angulo_variable[j])
                    
                
        elif Bus_type_NR[i] == 'PV':  # Barra PV.
            for j in range(len(Bus_type_NR)):
                Delta_P_NR[i] += Voltaje_variable[i]*Voltaje_variable[j]*Ybus_modulo[i,j]*sp.cos(Ybus_angulo[i,j] - Angulo_variable[i] + Angulo_variable[j]) 
            indicePV_NR.append(i)
                    
    # --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    #                                            Restamos las potencias especificas.
    # --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    # Valores a no eliminar, para saber cuales posiciones vamos a sustituir.
    no_borrar_SL = set([i for i, _ in enumerate(V_mod_NR) if i not in indiceSL_NR])
    no_borrar_PV = set([i for i, _ in enumerate(V_mod_NR) if i not in indicePV_NR])

    # -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    #                                       Borramos los datos extras de las Barras SL y PV.
    # -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    # Delta P y Delta Q.
    Delta_P_NR = sp.Matrix(np.delete(Delta_P_NR, indiceSL_NR))
    Delta_Q_NR = sp.Matrix(np.delete(Delta_Q_NR, indicePV_NR + indiceSL_NR))

    # Voltajes y Angulos.
    V_mod = sp.Matrix(np.delete(V_mod_NR,indicePV_NR + indiceSL_NR))
    V_ang = sp.Matrix(np.delete(V_ang_NR,indiceSL_NR))

    # Potencias especificas.
    P_espec = sp.Matrix(np.delete(P_espec_NR, indiceSL_NR))
    Q_espec = sp.Matrix(np.delete(Q_espec_NR, indicePV_NR + indiceSL_NR))

    # Ecuaciones simbolicas.
    Voltaje_variable = sp.Matrix(np.delete(Voltaje_variable, indicePV_NR + indiceSL_NR))
    Angulo_variable = sp.Matrix(np.delete(Angulo_variable, indiceSL_NR))

    # -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    #                                          Formamos las ecuaciones finales.
    # -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    DeltaP = sp.Matrix(P_espec) - sp.Matrix(Delta_P_NR)
    DeltaQ = sp.Matrix(Q_espec) - sp.Matrix(Delta_Q_NR)

    # ********************************************************************************************************************************************************************************************************************************
    #                                                    Matriz Jacobiana.
    # ********************************************************************************************************************************************************************************************************************************

    # Variables Auxiliares.
    valores = {}

    # -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    #                                           Matriz Derivadas de P.   
    # -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    # Creamos una submatriz que sean las derivadas de P con respecto a los angulos.
    J_P_Angulo = DeltaP.jacobian([valores for valores in Angulo_variable])

    # Creamos una submatriz que sean las derivadas de P con respecto a los voltajes.
    J_P_Volt = DeltaP.jacobian([valores for valores in Voltaje_variable]) 

    # Juntamos las dos submatrices en una sola.
    jacobian_p = J_P_Angulo.row_join(J_P_Volt)

    # -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    #                                          Matriz Derivadas de Q.
    # -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    # Creamos una submatriz que sean las derivadas de Q con respecto a los angulos.
    J_Q_Angulo = DeltaQ.jacobian([valores for valores in Angulo_variable])

    # Creamos una submatriz que sean las derivadas de Q con respecto a los voltajes.
    J_Q_Volt = DeltaQ.jacobian([valores for valores in Voltaje_variable])

    # Juntamos las dos submatrices en una sola.
    jacobian_q = J_Q_Angulo.row_join(J_Q_Volt)

    # -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    #                                          Matriz Jacobiana Completa.
    # -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    Jacobiana = jacobian_p.col_join(jacobian_q)

    # -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    #                                          Valores iniciales de angulos y voltajes.
    # -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    ValoresAnteriores = Angulo_variable.col_join(Voltaje_variable)  # Valores anteriores de angulos y voltajes.

    # -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    #                                           Matriz de Delta P y Delta Q.
    # -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    DeltasPQ = DeltaP.col_join(DeltaQ)

    # Variables auxiliares para el bucle.
    iteracion = 0
    ValoresNuevos = sp.zeros(ValoresAnteriores.rows,ValoresAnteriores.cols)  # Inicializamos los valores nuevos.


    # *****************************************************************************************************************************************************************
    #                                           Bucle de iteraciones.
    # *****************************************************************************************************************************************************************

    for k in range (Max_iter_NR):
        
        # Contamos las iteraciones.
        iteracion += 1
        
        # -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
        #                                       Asignamos los valores de las variables.
        # -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
        for i in range(len(V_mod_NR)):
            valores[f'V{i+1}'] = V_mod_NR[i]
            valores[f'Alpha{i+1}'] = V_ang_NR[i]
        
        # -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------    
        #                   Sustituimos los valores en la matriz Jacobiana y en la de Deltas.
        # -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
        
        Jacobiana = Jacobiana.subs(valores)
        DeltasPQ = DeltasPQ.subs(valores)
        ValoresAnteriores = ValoresAnteriores.subs(valores)
        Jacobiana_inv = Jacobiana.inv()  # Invertimos la matriz Jacobiana.

        # --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
        #                                       Expresión para NR
        # --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
        ValoresNuevos = ValoresAnteriores - Jacobiana_inv*DeltasPQ  # Nueva expresión para NR.
        
        # ================================================================================================================
        #                                       Calculamos el Error.
        # =================================================================================================================
        error = float(max(abs(ValoresNuevos - ValoresAnteriores)))
        # Cambiamos el type de error para poder compararlo.
        error = np.array(error, dtype=float)
        
        # ================================================================================================================
        #                               Condiciones de rompimiento del bucle.
        # ================================================================================================================
        if error < Convergencia_NR:
            print ()
            print ('El método de Newton Raphson ha convergido en', iteracion, 'iteraciones.')
            print ()
            break
        
        if iteracion == Max_iter_NR:
            print ()
            print ('El método de Newton Raphson no ha convergido en el número máximo de iteraciones.')
            print ()
            break
        
        # Verificar si algún valor en la matriz alcanza 1e+170 
        if (error >= 1e+170).any(): 
            print("Valor muy alto encontrado, rompiendo el bucle.") 
            break
        
        # -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
        #                                       Actualizamos los valores para la siguiente iteración.
        # -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
        
        # Voltaje
        h = 0
        for i in list (no_borrar_SL.intersection(no_borrar_PV)):
            V_mod_NR[i] = ValoresNuevos[(len(V_ang_NR)-1) + h]
            h += 1
            
        # Angulo
        h = 0
        for i in list (no_borrar_SL):
            V_ang_NR[i] = ValoresNuevos[h]
            h += 1
            
        # Valores anteriores
        ValoresAnteriores = ValoresNuevos.copy()
        
        # ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
        #                                               Pasamos por el Modelo Zip.
        # ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
        P_espec_NR, Q_espec_NR, P_demanda, Q_demanda = Carga_Zip.Cargas_Variables(P_demanda_NR, Q_demanda_NR, P_gen_NR, Q_gen_NR, Modulo_V_NR, Z_zip_NR, I_zip_NR, P_zip_NR, Bus_type_NR)
        
        # -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
        #                       Eliminamos los datos de las barras SL y PV para la siguiente iteración.
        # -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
        P_espec = sp.Matrix(np.delete(P_espec_NR, indiceSL_NR))
        Q_espec = sp.Matrix(np.delete(Q_espec_NR, indicePV_NR + indiceSL_NR))
        
        # -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
        #                           Creamos la nueva matriz de Deltas P y Deltas Q.
        # -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
        DeltaP = sp.Matrix(P_espec) - sp.Matrix(Delta_P_NR)
        DeltaQ = sp.Matrix(Q_espec) - sp.Matrix(Delta_Q_NR)
        
        # -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
        #                          Creamos la nueva matriz de Deltas P y Deltas Q.
        # -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
        DeltasPQ = DeltaP.col_join(DeltaQ)

    # -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    #                                   Preparamos los datos de salida.
    # -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
        
    # Convertimos las variables de salida.
    Modulos = V_mod_NR.copy()
    Angulos = V_ang_NR.copy()
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

    # Lista auxiliar
    Fasor = []

    # --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    #                   Construimos los Fasores a partir de los modulos y angulos.
    # --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    for i in range(len(angulo_radianes_series)):
        parte_real = modulo_series[i] * np.cos(angulo_radianes_series[i])
        parte_imaginaria = modulo_series[i] * np.sin(angulo_radianes_series[i])
        Fasor.append(complex(parte_real, parte_imaginaria))
        
    # ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    #                       Convertimos los angulos a grados para la salida.
    # ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    Angulos = np.degrees(angulo_radianes_series)

    # ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    #                       Asignamos las variables de salida.
    # ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    Angulos = V_ang_NR
    Modulos = V_mod_NR
    Iteraciones = iteracion
    Error = error
    Fasor = pd.Series(Fasor)
    
    
    final = time.time()
    print ()
    print("Tiempo de ejecución del método de Newton Raphson: ", final - Inicio, "segundos.")
    print ()



    return Modulos, Angulos, Fasor, Iteraciones, Error, P_demanda, Q_demanda
