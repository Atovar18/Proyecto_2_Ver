import math as mt
import numpy as np

def Potencia_activa (Bus_type, Modulo, Y_modulos_matriz, Y_angulos_matriz, angulo_radianes, i, P_especificada):
    Valor_2 = 0
    
    # Calculamos los valores fijos.
    #print (Y_modulos_matriz[i,i])
    print ('Angulos en Y:',Y_angulos_matriz[i,i])
    Valor_1 = (Modulo[i]**2)*(Y_modulos_matriz[i,i])*np.cos(Y_angulos_matriz[i,i])
    
    for j in range (len(Bus_type)):
        if i != j:
            #print (f'El valor de i es: {i+1} y el valor de j es: {j+1}')
            # Calculamos los valores variables.
            Valor_2 += Modulo[i]*Modulo[j]*Y_modulos_matriz[i,j]*np.cos(angulo_radianes[i] - angulo_radianes[j] - Y_angulos_matriz[i,j])
    print ()         
    cosa = Valor_1 + Valor_2
    toma = P_especificada [i]
    Resultado = toma - cosa
    
    return Resultado

def Potencia_reactiva (Modulo, Y_modulos_matriz, Y_angulos_matriz, k, Q_especificada, angulo_radianes):
    
    # Calculamos los valores fijos.    
    Valor_3 = - (Modulo[k]**2)*(Y_modulos_matriz[k,k])*mt.sin(Y_angulos_matriz[k,k])
    
    for h in range (len(Modulo)):
        if h != k:
            # Calculamos los valores variables.
            Valor_4 = Modulo[k]*Modulo[h]*Y_modulos_matriz[k,h]*np.sin(angulo_radianes[k] - angulo_radianes[h] - Y_angulos_matriz[k,h])

            # Juntamos todos los terminos.
            Valor_3 += Valor_4
            
    Resultado = Q_especificada [k] - Valor_3
    
    return Resultado

def Potencias_NR (Bus_type, Modulo, Y_modulos_matriz, Y_angulos_matriz, angulo_radianes, P_especificada, Q_especificada):
    # Inicializa las listas para almacenar las potencias activas y reactivas
    P_activa = []
    Q_reactiva = []

    # Comenzamos calculando los valores de las potencias activas y reactivas iniciales.
    for k in range (len(P_especificada)):
        if Bus_type[k] == "SL":
            P_activa.append(0)
            Q_reactiva.append(0)
            
        if Bus_type[k] == "PV":
            Resultado = Potencia_activa (Bus_type, Modulo, Y_modulos_matriz, Y_angulos_matriz, angulo_radianes, k, P_especificada)
            P_activa.append(Resultado)
            Q_reactiva.append(0)
            
        if Bus_type[k] == "PQ":
            Resultado = Potencia_activa (Bus_type, Modulo, Y_modulos_matriz, Y_angulos_matriz, angulo_radianes, k, P_especificada)
            P_activa.append(Resultado)
            Resultado = Potencia_reactiva (Modulo, Y_modulos_matriz, Y_angulos_matriz, k, Q_especificada, angulo_radianes)
            Q_reactiva.append(Resultado)
            
        # ---------------------------------------------------------- Matrices de Potencia. --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    # Juntamos todas las potencias.
    P_activas = P_activa.copy()
    P_activas += (Q_reactiva)

    # Eliminar todos los elementos que sean 0
    Matriz_Potencias = [elemento for elemento in P_activas if elemento != 0]
    Matriz_Potencias = np.matrix (Matriz_Potencias)
    Matriz_Potencias = np.transpose(Matriz_Potencias)
            
    return P_activa, Q_reactiva, Matriz_Potencias

def Jacobiana_Potencias (Bus_type, Modulo, Y_modulos_matriz, Y_angulos_matriz, angulo_radianes):

    # Armamos la matriz Jacobiana de potencias activas respecto a los angulos.
    n = len(Bus_type)
    Dan = 0

    # Listas para la Jacobiana.
    Daigonal_P = np.matrix(np.zeros((n,n)))
    F_Daigonal_P = np.matrix(np.zeros((n,n)))

    # Bucle para la diagonal princial.
    for i in range(n):
        
        if Bus_type [i] == 'SL':
                continue
            
        for j in range (n):
            
            if i != j:
                Peras = Modulo [i]*Modulo [j]*Y_modulos_matriz [i,j]*np.sin(angulo_radianes [i] - angulo_radianes [j] - Y_angulos_matriz [i,j])
                Dan += Peras
        Daigonal_P[i,i] = Dan
        Dan = 0

    # Bucle para la matriz fuera de la diagonal.
    for i in range (n):
        
        if Bus_type [i] == 'SL':
            continue
        
        for j in range (n):
            
            if i != j:

                Toma = -Modulo [j]*Modulo [i]*Y_modulos_matriz [i,j]*np.sin(angulo_radianes [j] - angulo_radianes [i] - Y_angulos_matriz [j,i])             
                F_Daigonal_P [i,j] = Toma
    # Juntamos Matrices. 
    Jacoviana_P = Daigonal_P + F_Daigonal_P

    # Eliminar filas y columnas donde Bus_type == "SL"
    indices_a_eliminar = [i for i, tipo in enumerate(Bus_type) if tipo == "SL"]
    Jacoviana_P = np.delete(Jacoviana_P, indices_a_eliminar, axis=0)  # Eliminar filas
    Jacoviana_P = np.delete(Jacoviana_P, indices_a_eliminar, axis=1)  # Eliminar columnas

    # ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    # Armamos la matriz Jacobiana de Potencias Activas respecto al voltaje.
    P_V_Diagonal = np.matrix(np.zeros((n,n)))
    P_V_F_Diagonal = np.matrix(np.zeros((n,n)))
    Valor_2 = 0

    # Bucle para la diagonal principal.
    for i in range (n):
        
        if Bus_type [i] == 'SL':
            continue
        
        Valor_1 = -2*Modulo [i]*Y_modulos_matriz [i,i]*mt.cos(Y_angulos_matriz [i,i])
        for j in range (n):
                
            if i != j:
                Valor_2 += Modulo [j] * Y_modulos_matriz [i,j] * mt.cos(angulo_radianes [i] - angulo_radianes [j] - Y_angulos_matriz [i,j])
                
        Valor = Valor_1 - Valor_2 
        P_V_Diagonal [i,i] = Valor
        Valor_2 = 0
            
    # Bucle para la matriz fuera de la diagonal. 
    for i in range (n):
            
            if Bus_type [i] == 'SL':
                continue
            
            for j in range (n):
                
                if i != j:
                    P_V_F_Diagonal [j,i] = - Modulo [j]* Y_modulos_matriz [j,i] * mt.cos(angulo_radianes [j] - angulo_radianes [i] - Y_angulos_matriz [j,i])

    # Juntamos las matrices.
    Jacoviana_P_Voltaje = P_V_Diagonal + P_V_F_Diagonal

    # Eliminar filas y columnas donde Bus_type == "SL"
    indices_a_eliminar = [i for i, tipo in enumerate(Bus_type) if tipo == "SL"]
    Jacoviana_P_Voltaje = np.delete(Jacoviana_P_Voltaje, indices_a_eliminar, axis=0)  # Eliminar filas
    Jacoviana_P_Voltaje = np.delete(Jacoviana_P_Voltaje, indices_a_eliminar, axis=1)  # Eliminar columnas

    # Eliminar Filas donde Bus_type == "PQ"
    indices_a_eliminar = [i-1 for i, tipo in enumerate(Bus_type) if tipo == "PV"]
    Jacoviana_P_Voltaje = np.delete(Jacoviana_P_Voltaje, indices_a_eliminar, axis=1)  # Eliminar filas

    # ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    # Armamos la matriz Jacobiana de Potencias Reactivas respecto a los angulos.
    Diagonal_Q = np.matrix(np.zeros((n,n)))
    F_Diagonal_Q = np.matrix(np.zeros((n,n)))

    # Bucle para la diagonal principal.
    for i in range(n):
        
        if Bus_type [i] == 'SL':
                continue
            
        for j in range (n):
            
            if i != j:
                Dan += - (Modulo [i]*Modulo [j]*Y_modulos_matriz [i,j]*mt.cos(angulo_radianes [i] - angulo_radianes [j] - Y_angulos_matriz [i,j]))
        Diagonal_Q[i,i] = Dan

    # Bucle para la matriz fuera de la diagonal.
    for i in range (n):
        
        if Bus_type [i] == 'SL':
            continue
        
        for j in range (n):
            
            if i != j:
                F_Diagonal_Q [i,j] = Modulo [i]*Modulo [j]*Y_modulos_matriz [i,j]*mt.cos(angulo_radianes [i] - angulo_radianes [j] - Y_angulos_matriz [i,j])
                
    # Juntamos Matrices.
    Jacoviana_Q = Diagonal_Q + F_Diagonal_Q

    # Eliminar filas y columnas donde Bus_type == "SL"
    indices_a_eliminar = [i for i, tipo in enumerate(Bus_type) if tipo == "SL"]
    Jacoviana_Q = np.delete(Jacoviana_Q, indices_a_eliminar, axis=0)  # Eliminar filas
    Jacoviana_Q = np.delete(Jacoviana_Q, indices_a_eliminar, axis=1)  # Eliminar columnas

    # Eliminar filas y columnas donde Bus_type == "SL"
    indices_a_eliminar = [i-1 for i, tipo in enumerate(Bus_type) if tipo == "PV"]
    Jacoviana_Q = np.delete(Jacoviana_Q, indices_a_eliminar, axis=0)  # Eliminar filas


    # ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    # Armamos la matriz Jacobiana de Potencias Reactivas respecto al voltaje.
    Q_V_Diagonal = np.matrix(np.zeros((n,n)))
    Q_V_F_Diagonal = np.matrix(np.zeros((n,n)))
    Valor_6 = 0

    # Bucle para la diagonal principal.
    for i in range (n):
        
        if Bus_type [i] == 'SL':
            continue    
        
        Valor_m = 2*Modulo [i]*Y_modulos_matriz [i,i]*np.sin(Y_angulos_matriz [i,i])
        for j in range (n):
                
            if i != j:
                Caja = Modulo [j]*Y_modulos_matriz [i,j]*mt.sin(angulo_radianes [i] - angulo_radianes [j] - Y_angulos_matriz [i,j])
                Valor_6 += Caja
    
        Julio = Valor_m - Valor_6 
        Q_V_Diagonal [i,i] = Julio
        Valor_6 = 0
    
    # Eliminar filas y columnas donde Bus_type == "SL"
    indices_a_eliminar = [i for i, tipo in enumerate(Bus_type) if tipo == "SL"]
    Q_V_Diagonal = np.delete(Q_V_Diagonal, indices_a_eliminar, axis=0)  # Eliminar filas
    Q_V_Diagonal = np.delete(Q_V_Diagonal, indices_a_eliminar, axis=1)  # Eliminar columnas

    # Eliminar Filas donde Bus_type == "PQ"
    indices_a_eliminar = [i-1 for i, tipo in enumerate(Bus_type) if tipo == "PV"]  
    Jacoviana_Q_Voltaje = np.delete(Q_V_Diagonal, indices_a_eliminar, axis=0)  # Eliminar filas
    Jacoviana_Q_Voltaje = np.delete(Q_V_Diagonal, indices_a_eliminar, axis=1)  # Eliminar columnas
    
    # Eliminar filas que contienen solo ceros
    Jacoviana_Q_Voltaje = Jacoviana_Q_Voltaje[~np.all(Jacoviana_Q_Voltaje == 0, axis=1)]

    # ******************************************************************************************************************************************************************************************************************************************************************
    #                                                       Armado la matriz Jacobiana final.
    # ******************************************************************************************************************************************************************************************************************************************************************

    # Juntamos la matrices Jacobianas correspondientes a los angulos.
    matriz1 = Jacoviana_P
    matriz2 = Jacoviana_Q

    # Ajustar dimensiones para combinar verticalmente
    if matriz1.shape[1] != matriz2.shape[1]:
        # Añadir columnas de ceros a la matriz más pequeña
        if matriz1.shape[1] < matriz2.shape[1]:
            matriz1 = np.hstack((matriz1, np.zeros((matriz1.shape[0], matriz2.shape[1] - matriz1.shape[1]))))
        else:
            matriz2 = np.hstack((matriz2, np.zeros((matriz2.shape[0], matriz1.shape[1] - matriz2.shape[1]))))

    # Combinar verticalmente
    matriz_combinada_angulos = np.vstack((matriz1, matriz2))

    # ----------------------------------------------- Jacovianas respecto al voltaje. -----------------------------------------------------------------------------------------------------------------------------------------------------------
    # Bases para juntar.
    Base = [Jacoviana_P_Voltaje, Jacoviana_Q_Voltaje]

    # Determinamos las dimensiones de la nueva matriz.
    max_filas = Jacoviana_P_Voltaje.shape[0] + Jacoviana_Q_Voltaje.shape[0]
    max_columnas = max(matriz.shape[1] for matriz in Base)

    # Ajustar dimensiones de cada matriz
    matrices_ajustadas = []
    for matriz in Base:
        filas, columnas = matriz.shape
        matriz_ajustada = np.zeros((max_filas, max_columnas))
        matriz_ajustada[:filas, :columnas] = matriz
        matrices_ajustadas.append(matriz_ajustada)

    # Combinar todas las matrices ajustadas en una sola matriz
    matriz_combinada = np.vstack(matrices_ajustadas)

    # Eliminar filas que contienen solo ceros
    matriz_combinada = matriz_combinada[~np.all(matriz_combinada == 0, axis=1)]

    # Eliminar columnas que contienen solo ceros
    matriz_combinada_voltaje = matriz_combinada[:, ~np.all(matriz_combinada == 0, axis=0)]

    # ------------------------------------------------------------------------------ Armamos la jacoviana final. ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    # Combinar las matrices horizontalmente
    Jacoviana = np.hstack((matriz_combinada_angulos, matriz_combinada_voltaje))
    return Jacoviana

import sympy as sp

def Jacobiana (Expresion_P, angulos_var, voltaje_var, Expresion_Q, v_ang, v_mod):
    
    #Jacobianos
    #jacobianos de potencia activa
    JdeltaPalpha = Expresion_P.jacobian([valores for valores in angulos_var])
    JdeltaPvolt = Expresion_P.jacobian([valores for valores in voltaje_var]) 
    jacobian_p = JdeltaPalpha.row_join(JdeltaPvolt)
    #Jacobiano de potencia reactiva
    JdeltaQalpha = Expresion_Q.jacobian([valores for valores in angulos_var])
    JdeltaQvolt = Expresion_Q.jacobian([valores for valores in voltaje_var])
    jacobian_q = JdeltaQalpha.row_join(JdeltaQvolt)

    #Uniendo valores
    values_bf = v_ang.col_join(v_mod)
    Jacobian = jacobian_p.col_join(jacobian_q)
    f_powers = Expresion_P.col_join(Expresion_Q)
    values_next = sp.zeros(values_bf.rows,values_bf.cols)
    
    
    
    return