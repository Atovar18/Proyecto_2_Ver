import numpy as np
import pandas as pd


def Flujos (Bus_i_lineas, Bus_j_lineas, ID_lineas, B_lineas, Barrai_TRX, Barraj_TRX, ID_trx, Tap_trx, Fasores_GS, Conex_lineas, SeriesTRX):

    # Creamos arrays vacios para almacenar los potencias según el tipo de elementos que tennemos.
    Potencia_Sij = np.array([]); Potencia_Sji = np.array([]); Potencia_Sij2 = np.array([]); Potencia_Sji2 = np.array([])
    
    # Creamos una lista con los indices i y j de las conexiones de las lineas y los transformadores.
    Indice_Line = list (zip (Bus_i_lineas, Bus_j_lineas))
    Indice_TRX = list (zip (Barrai_TRX, Barraj_TRX))

    # Convertimos las listas en arrays.
    Bus_i_linea = list (Bus_i_lineas)
    Bus_j_linea = list (Bus_j_lineas)
    Bus_i_TRX = list (Barrai_TRX)
    Bus_j_TRX = list (Barraj_TRX)
    ID_linea = list (ID_lineas)
    ID_trxS = list (ID_trx)
    
    # Picamos las subceptancias de las lineas la mitad para i y j.
    for posicion, nexos in enumerate (Indice_Line):
        
        i = nexos [0] - 1
        j = nexos [1] - 1

        if posicion <= len (B_lineas)-1:
            X_linea_tierra = B_lineas [posicion] / 2
            
            if X_linea_tierra == 0:
                Y_linea_tierra = 0
                
            else: 
                Y_linea_tierra = X_linea_tierra
        else: 
            Y_linea_tierra = 0 
            
        
        # Crear la matriz Matriz_Linea 
        Matriz_Linea = pd.DataFrame({ 'Bus_i_lineas': Bus_i_linea, 'Bus_j_lineas': Bus_j_linea, 'Conex_lineas': Conex_lineas, 'Y_linea_tierra':Y_linea_tierra})
        Matriz_Trx = pd.DataFrame({ 'Bus_i_TRX': Bus_i_TRX, 'Bus_j_TRX': Bus_j_TRX, 'SeriesTRX': SeriesTRX})
        Zp_linea = None
        Zx_trx = None
        
        
        """El bucle for se encarga de leer el bus i y bus j, para calcular el flujo de potencia, pero para elementos en 
        paralelo, compara el la columna de Bus_i y lo compara con el indice i donde se encuentra el elemento conectado, 
        igual con la bus j, una vez ubicados los elementos iguales, se extrae la impedancia asociada al elemento para 
        calcular el flujo de potencia."""
        # Comparar i con la primera columna y j con la segunda columna 
        for index, row in Matriz_Linea.iterrows():           
            if int(row['Bus_i_lineas'].real - 1) == i and int(row['Bus_j_lineas'].real-1) == j: 
                Zp_linea = row['Conex_lineas']
                break
        
        # ******************************************************************************************************************************************************************************************************************************************************************************************************************************************************
        #                                                                              Flujo de potencia i -> j.
        # ******************************************************************************************************************************************************************************************************************************************************************************************************************************************************
        
        # Calculamos los terminos.
        Termino_tierra = (abs (Fasores_GS [i]) ** 2) * np.conjugate(Y_linea_tierra)
        Termino_conex_linea = Fasores_GS [i]*(np.conjugate((Fasores_GS[i] - Fasores_GS[j]) * Zp_linea))

        # Flujo i -> j.
        ij = Termino_tierra + Termino_conex_linea
        
        # Aproximamos los resultados.
        ij = np.round (ij, 4)
        
        # Guardamos los valores.
        Potencia_Sij = np.append (Potencia_Sij, ij)
        
        # ******************************************************************************************************************************************************************************************************************************************************************************************************************************************************
        #                                                                              Flujo de potencia j -> i.
        # ******************************************************************************************************************************************************************************************************************************************************************************************************************************************************
        
        # Calculamos los terminos.
        Termino_tierra_2 = (abs (Fasores_GS [j]) ** 2) * np.conjugate(Y_linea_tierra)
        Termino_conex_linea_2 = Fasores_GS [j]*(np.conjugate((Fasores_GS[j] - Fasores_GS[i]) * Zp_linea))

        # Flujo j -> i.
        ji = Termino_tierra_2 + Termino_conex_linea_2
        
        # Aproximamos los resultados.
        ji = np.round (ji, 4)
        
        # Guardamos los valores.
        Potencia_Sji = np.append (Potencia_Sji, ji)
        
    # ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    #                                                                               Sección de transformadores.
    # ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    for posicion, nexos in enumerate (Indice_TRX):
        
        i = nexos [0] - 1
        j = nexos [1] - 1
        
        # ******************************************************************************************************************************************************************************************************************************************************************************************************************************************************
        #                                                                              Flujo de potencia i -> j.
        # ******************************************************************************************************************************************************************************************************************************************************************************************************************************************************
        
        # Comparar i con la primera columna y j con la segunda columna        
        for index, row in Matriz_Trx.iterrows():           
            if int(row['Bus_i_TRX'].real - 1) == i and int(row['Bus_j_TRX'].real-1) == j: 
                Zx_trx = row['SeriesTRX']
                break
    
            
        # Calculamos los terminos.
        Termino1 = (abs (Fasores_GS [i]) ** 2)*np.conjugate(Zx_trx)
        Termino2 = np.conjugate (Tap_trx[posicion])*(Fasores_GS [i])*(np.conjugate(Fasores_GS [j]))*np.conjugate(Zx_trx)
        
        # Flujo i -> j.
        ij = Termino1 - Termino2
        
        # Aproximamos los resultados.
        ij = np.round (ij, 4)
        
        # Guardamos los valores.
        Potencia_Sij2 = np.append (Potencia_Sij2, ij)
        
        # ******************************************************************************************************************************************************************************************************************************************************************************************************************************************************
        #                                                                              Flujo de potencia j -> i.
        # ******************************************************************************************************************************************************************************************************************************************************************************************************************************************************
        
        # Calculamos los terminos.
        Termino1 = (Tap_trx[posicion]**2)*(abs (Fasores_GS [j]) ** 2)*np.conjugate(SeriesTRX [posicion])
        Termino2 = Tap_trx[posicion]*(Fasores_GS [j])*(np.conjugate(Fasores_GS [i]))*np.conjugate(SeriesTRX [posicion])
        
        # Flujo j -> i.
        ji = Termino1 - Termino2
        
        # Aproximamos los resultados.
        ji = np.round (ji, 4)
        
        # Guardamos los valores.
        Potencia_Sji2 = np.append (Potencia_Sji2, ji)
        
    # Separación de los valores de las potencias.

    # i -> j.
    Pij_linea = np.real(Potencia_Sij)
    Qij_linea = np.imag(Potencia_Sij)
    Pij_trx = np.real(Potencia_Sij2)
    Qij_trx = np.imag(Potencia_Sij2)

    # j -> i.
    Pji_linea = np.real(Potencia_Sji)
    Qji_linea = np.imag(Potencia_Sji)
    Pji_trx = np.real(Potencia_Sji2)
    Qji_trx = np.imag(Potencia_Sji2)

    # ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    #                                                                               Perdidas.
    # ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    # Lineas.
    Perdidas_line = Potencia_Sij + Potencia_Sji
    P_loss_lineas = np.real(Perdidas_line)
    Q_loss_lineas = np.imag(Perdidas_line)

    # Convertimos los arreglos en listas.
    P_loss_lineas = list (P_loss_lineas)
    Q_loss_lineas = list (Q_loss_lineas)
    Pij_linea = list (Pij_linea)
    Qij_linea = list (Qij_linea)
    Pji_linea = list (Pji_linea)
    Qji_linea = list (Qji_linea)

    # Transformadores.
    Perdidas_trx = Potencia_Sij2 + Potencia_Sji2
    P_loss_trx = np.real(Perdidas_trx)
    Q_loss_trx = np.imag(Perdidas_trx)

    # ******************************************************************************************************************************************************************************************************************************************************************************************************************************************************
    #                                                                              Salidas.
    # ******************************************************************************************************************************************************************************************************************************************************************************************************************************************************

    # Juntamos todos los valores en una sola variable.
    Bus_i_linea.extend (Bus_i_TRX)
    Bus_j_linea.extend (Bus_j_TRX)
    ID_linea.extend (ID_trxS)
    P_loss_lineas.extend (P_loss_trx)
    Q_loss_lineas.extend (Q_loss_trx)
    Pij_linea.extend (Pij_trx)
    Qij_linea.extend (Qij_trx)
    Pji_linea.extend (Pji_trx)
    Qji_linea.extend (Qji_trx)

    # Reescritura de las variables.
    Salida_i = list (Bus_i_linea)
    Salida_j = list (Bus_j_linea)
    ID = list (ID_linea)
    P_loss = list (P_loss_lineas)
    Q_loss = list (Q_loss_lineas)
    Pij = list (Pij_linea)
    Qij = list (Qij_linea)
    Pji = list (Pji_linea)
    Qji = list (Qji_linea)

    # Ordenamos en función de las barras. 
    # Paso 1: Crear lista de tuplas
    lista_combinada = list(zip(Salida_i, Salida_j, P_loss, Q_loss, Pij, Qij, Pji, Qji, ID))

    # Paso 2: Ordenar la lista de tuplas por el primer elemento de cada tupla (que corresponde a Barra_i)
    lista_combinada_ordenada = sorted(lista_combinada, key=lambda x: x[0]) 

    # Paso 3: Desempaquetar en las listas originales
    Salida_i, Salida_j, P_loss, Q_loss, Pij, Qij, Pji, Qji, ID  = map(list,zip(*lista_combinada_ordenada))

    # Paso 4: Regresamos las listas a su estado inical.
    Salida_i =  list(Salida_i)
    Salida_j =  list(Salida_j)
    ID = list(ID)
    P_loss = list(P_loss)
    Q_loss = list(Q_loss)
    Pij = list(Pij)
    Qij = list(Qij)
    Pji = list(Pji)
    Qji = list(Qji)
    
    return Salida_i, Salida_j, ID, P_loss, Q_loss, Pij, Qij, Pji, Qji