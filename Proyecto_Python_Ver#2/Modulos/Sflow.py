import pandas as pd
import numpy as np


def calculo_flujos(Modulos, Fasores, Admitancia_lineas, Admitancia_transformadores, Bus_i_lineas, Bus_j_lineas, Bus_i_trx, Bus_j_trx, Tap_trx, Efecto_L_Barra_i, Efecto_L_Barra_j, ID_lineas, ID_transformadores):
    
    # Creamos copias de las variables.
    Salida_i_lineas = np.copy(Bus_i_lineas)  # Copia de las barras de salida de las lineas.
    Llegada_i_lineas = np.copy(Bus_j_lineas)  # Copia de las barras de llegada de las lineas.
    Salida_i_transformadores = np.copy(Bus_i_trx)  # Copia de las barras de salida de los transformadores.
    Llegada_i_transformadores = np.copy(Bus_j_trx)  # Copia de las barras de llegada de los transformadores.
    Modulo = np.copy(Modulos)  # Copia de los modulos de las tensiones.
    Fasor = np.copy(Fasores)
    L_Barra_i = np.copy(Efecto_L_Barra_i)
    L_Barra_j = np.copy(Efecto_L_Barra_j)
    ID_linea = np.copy(ID_lineas)  # Copia de los IDs de las lineas.
    ID_transformador = np.copy(ID_transformadores)  # Copia de los IDs de los transformadores.

    # Creamos las para poder ordenar los datos de las lineas.
    S_ij_lineas = np.array([])  # Lista para almacenar los flujos de potencia i -> j.
    S_ji_lineas = np.array([])  # Lista para almacenar los flujos de potencia j -> i.
    S_ij_transformadores = np.array([])  # Lista para almacenar los flujos de potencia i -> j en los transformadores.
    S_ji_transformadores = np.array([])  # Lista para almacenar los flujos de potencia j -> i en los transformadores.

    for posicion, (salida, llegada) in enumerate(zip(Bus_i_lineas, Bus_j_lineas)): 

        # Obtenemos los indices de las barras de salida y llegada.
        indice_i = salida - 1
        indice_j = llegada - 1
        
        # =================================================================================================================================================================================================================================================================================================================================================
        #                                  Cálculo de los flujos de potencia sobre las líneas.
        # =================================================================================================================================================================================================================================================================================================================================================
        
        # ******************************************************************************************************************************************************************************************************************************************************************************************************************************************************
        #                                            Flujo de potencia i -> j.
        # ******************************************************************************************************************************************************************************************************************************************************************************************************************************************************
        
        # Obtenemos los flujos de potencia en la linea.
        Tierra_ij = (Modulo[indice_i]**2)*(np.conjugate(L_Barra_i[indice_i]))
        Linea_ij = Fasor[indice_i]*(np.conjugate((Fasor[indice_i] - Fasor[indice_j])*(Admitancia_lineas[posicion]))) 

        # Flujo total i -> j.
        ij = Tierra_ij + Linea_ij
        
        # Añadimos el flujo de potencia i -> j a la lista.
        S_ij_lineas = np.append(S_ij_lineas, ij)

        # ******************************************************************************************************************************************************************************************************************************************************************************************************************************************************
        #                                            Flujo de potencia j -> i.
        # ******************************************************************************************************************************************************************************************************************************************************************************************************************************************************

        # Obtenemos los flujos de potencia en la linea.
        Tierra_ji = (Modulo[indice_j]**2)*(np.conjugate(L_Barra_j[indice_j]))
        Linea_ji = Fasor[indice_j]*(np.conjugate((Fasor[indice_j] - Fasor[indice_i]) *(Admitancia_lineas[posicion])))

        # Flujo total j -> i.
        ji = Tierra_ji + Linea_ji

        # Añadimos el flujo de potencia j -> i a la lista.
        S_ji_lineas = np.append(S_ji_lineas, ji)

    for posicion, (salida, llegada) in enumerate(zip(Bus_i_trx, Bus_j_trx)):
        # =================================================================================================================================================================================================================================================================================================================================================
        #                                  Cálculo de los flujos de potencia sobre los transformadores.
        # =================================================================================================================================================================================================================================================================================================================================================
        
        # ******************************************************************************************************************************************************************************************************************************************************************************************************************************************************
        #                                            Flujo de potencia i -> j.
        # ******************************************************************************************************************************************************************************************************************************************************************************************************************************************************
        
        # Obtenemos los flujos de potencia en el transformador.
        termino_1 = (Modulo[indice_i]**2)*(np.conjugate(Admitancia_transformadores[indice_i]))
        termino_2 = Tap_trx [indice_i] * Fasor[indice_i] * np.conjugate(Fasor[indice_i])*np.conjugate(Admitancia_transformadores[indice_i])
        
        # Flujo total i -> j en el transformador.
        ij_transformador = termino_1 - termino_2
        
        # Añadimos el flujo de potencia i -> j en el transformador a la lista.
        S_ij_transformadores = np.append(S_ij_transformadores, ij_transformador)
        
        # ******************************************************************************************************************************************************************************************************************************************************************************************************************************************************
        #                                            Flujo de potencia j -> i.
        # ******************************************************************************************************************************************************************************************************************************************************************************************************************************************************

        termino_3 = (Tap_trx[indice_j]**2)*(Modulo[indice_j]**2)*(np.conjugate(Admitancia_transformadores[indice_j]))
        termino_4 = Tap_trx[indice_j] * Fasor[indice_j] * np.conjugate(Fasor[indice_j]) * np.conjugate(Admitancia_transformadores[indice_j])
        
        # Flujo total j -> i en el transformador.
        ji_transformador = termino_3 - termino_4  
        
        # Añadimos el flujo de potencia j -> i en el transformador a la lista.
        S_ji_transformadores = np.append(S_ji_transformadores, ji_transformador)
        

    # Sumamos los flujos de las lineas y transformadores.
    S_perdidas_lineas = S_ij_lineas + S_ji_lineas 
    S_perdidas_transformadores = S_ij_transformadores + S_ji_transformadores  # Flujos de potencia perdidas en los transformadores.

    S_perdidas_lineas = np.round(S_perdidas_lineas, 4)  # Redondeamos los flujos de potencia perdidas en las lineas a cuatro decimales.
    S_perdidas_transformadores = np.round(S_perdidas_transformadores, 4)  # Redondeamos los flujos de potencia perdidas en los transformadores a cuatro decimales.

    # Separamos las perdidas activas y reactivas.
    P_perdidas_lineas = np.real(S_perdidas_lineas)
    Q_perdidas_lineas = np.imag(S_perdidas_lineas)
    P_perdidas_transformadores = np.real(S_perdidas_transformadores)
    Q_perdidas_transformadores = np.imag(S_perdidas_transformadores)

    # Extendemos las listas para reducir las variables.
    P_perdidas = np.append(P_perdidas_lineas, P_perdidas_transformadores)
    Q_perdidas = np.append(Q_perdidas_lineas, Q_perdidas_transformadores)
    Salidas = np.append(Salida_i_lineas, Salida_i_transformadores)
    Llegadas = np.append(Llegada_i_lineas, Llegada_i_transformadores)
    ID = np.append(ID_linea, ID_transformador)
    Pij = np.real(np.append(S_ij_lineas, S_ij_transformadores))
    Qij = np.imag(np.append(S_ij_lineas, S_ij_transformadores))
    Pji = np.real(np.append(S_ji_lineas, S_ji_transformadores))
    Qji = np.imag(np.append(S_ji_lineas, S_ji_transformadores))

    # Creamos un DataFrame con los datos para ordenarlos según su salida y llegada.
    Nuevo_orden = pd.DataFrame({'Salidas': Salidas, 'Llegadas': Llegadas, 'ID': ID, 'P_perdidas': P_perdidas, 'Q_perdidas': Q_perdidas, 'P_ij': Pij, 'P_ji': Pji, 'Q_ij': Qij, 'Q_ji': Qji})

    # Ordenamos la columna Salidas y Llegadas, por si hace falta.
    Nuevo_orden = Nuevo_orden.sort_values(by=['Salidas', 'Llegadas'])

    # Redefinimos los indices para efectos de calculos.
    Nuevo_orden = Nuevo_orden.reset_index(drop=True)

    # Extraemos los datos ordenados.
    Salidas = Nuevo_orden['Salidas'].values
    Llegadas = Nuevo_orden['Llegadas'].values
    ID = Nuevo_orden['ID'].values
    P_perdidas = Nuevo_orden['P_perdidas'].values
    Q_perdidas = Nuevo_orden['Q_perdidas'].values
    P_ij = Nuevo_orden['P_ij'].values
    P_ji = Nuevo_orden['P_ji'].values
    Q_ij = Nuevo_orden['Q_ij'].values
    Q_ji = Nuevo_orden['Q_ji'].values

    return Salidas, Llegadas, ID, P_perdidas, Q_perdidas, P_ij, P_ji, Q_ij, Q_ji