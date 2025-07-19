import numpy as np
import pandas as pd
import itertools

def Incidencia_Nodal(Bus_i_lineas, Bus_j_lineas, R_lineas, X_lineas, B_lineas, R_Shunt, X_Shunt, Tap_trx, Xcc_trx, Bus_i_SHUNT, Indices_tap_i, Indices_tap_j, Barra_i,Bus_i_trx, Bus_j_trx, Indices_line_i, Indices_line_j):

    Bus_i = Barra_i.copy()
    Lineas_Salida = Bus_i_lineas.copy()
    Lineas_Llegadas = Bus_j_lineas.copy()
    Transformadores_Salida = Bus_i_trx.copy()
    Transformadores_Llegadas = Bus_j_trx.copy()
    Shunt_i = Bus_i_SHUNT.copy()
    Resis_lineas = R_lineas.copy()
    Reac_lineas = X_lineas.copy()
    Reac_Shunt = X_Shunt.copy()
    Resis_Shunt = R_Shunt.copy()
    Suscep_lineas = B_lineas.copy()        # Susceptancia de las lineas con unidades de Most (admitancias).
    Tap = Tap_trx.copy()
    Reac_trx = Xcc_trx.copy()

    # ======================================================================================================================================================================================================
    #                                 Formamos impedancias y luego admitancias.
    # ======================================================================================================================================================================================================
    Impedancia_lineas = np.array([complex(Resis_lineas[i], Reac_lineas[i]) for i in range(len(Resis_lineas))])
    Impedancia_shunt = np.array([complex(Resis_Shunt[i], Reac_Shunt[i]) for i in range(len(Resis_Shunt))])
    Impedancia_transformadores = np.array([complex(0, Reac_trx[i]) for i in range(len(Reac_trx))])

    # Convertimos las impedancias a admitancias.
    Admitancia_lineas = np.reciprocal(Impedancia_lineas)
    Admitancia_shunt = np.reciprocal(Impedancia_shunt)
    Admitancia_transformadores = Tap * np.reciprocal(Impedancia_transformadores) # Admitancias de los transformadores serie, entre barras.

    # ======================================================================================================================================================================================================    
    #                                    Calculamos los posibles efectos a tierra de los elementos.      
    # ======================================================================================================================================================================================================
    
    # Definimos listas de igual longitud para facilitar calculos.
    # Encuentra la longitud máxima entre las listas
    longitud_maxima = max(len(Suscep_lineas), len(Bus_i_SHUNT), len(Tap))
    
    Efecto_L_Barra_i = []
    Efecto_L_Barra_j = []
    Efecto_trx_Barra_i = []
    Efecto_trx_Barra_j = []
    
    # Rellena las listas más cortas con ceros
    Efecto_L_Barra_i = Efecto_L_Barra_i + [0] * (longitud_maxima - len(Efecto_L_Barra_i))
    Efecto_L_Barra_i = Efecto_L_Barra_i + [0] * (longitud_maxima - len(Efecto_L_Barra_i))
    Efecto_L_Barra_j = Efecto_L_Barra_j + [0] * (longitud_maxima - len(Efecto_L_Barra_j))
    Efecto_trx_Barra_i = Efecto_trx_Barra_i + [0] * (longitud_maxima - len(Efecto_trx_Barra_i))
    Efecto_trx_Barra_j = Efecto_trx_Barra_j + [0] * (longitud_maxima - len(Efecto_trx_Barra_j))
    
    

    # ------------------------------------------------------------- Lineas ---------------------------------------------------------------------------------------------------------------------------------
    Efecto_line = Suscep_lineas/2
    Efecto_line = np.array([complex(0, Efecto_line[i]) for i in range(len(Efecto_line))])  # Convertimos a complejo.
    Efecto_L_Barra_i = Efecto_line.copy()
    Efecto_L_Barra_j = Efecto_line.copy()

    # ------------------------------------------------------------- Transformadores --------------------------------------------------------------------------------------------------------------------------
    Efecto_trx_Barra_i = (1-Tap)*Admitancia_transformadores
    Efecto_trx_Barra_j = ((Tap**2)-Tap)*Admitancia_transformadores

    # ------------------------------------------------------------- Bshunt -----------------------------------------------------------------------------------------------------------------------------------
    Admitancia_shunt = Admitancia_shunt

    # ********************************************************************************************************************************************************************************************************
    #                                                              Definimos dimensiones de la matriz
    # ********************************************************************************************************************************************************************************************************# Elementos a tierra: combinamos todas las listas y eliminamos duplicados

    # Combinamos todas las listas y eliminamos duplicados.
    indices_a_tierra = list(set(itertools.chain(Indices_line_i, Indices_line_j, Indices_tap_i, Indices_tap_j, Shunt_i)))

    # Creamos la matriz base.
    Filas = len(Bus_i) + len(indices_a_tierra)  # Numero de filas: numero de barras + numero de elementos a tierra.
    Columnas = len(Bus_i)  # Numero de columnas: numero de barras.
    MatrizA = np.zeros((Filas, Columnas))

    # ======================================================================================================================================================================================================    
    #                                    Calculamos la matriz de incidencia para las barras.      
    # ======================================================================================================================================================================================================

    # ----------------------------------- Salidas ----------------------------------
    Indice_Barras_Salida = []
    Indice_Barras_Salida.extend(Lineas_Salida)
    Indice_Barras_Salida.extend(Transformadores_Salida)
    # ----------------------------------- Llegadas ---------------------------------
    Indice_Barras_Llegadas = []
    Indice_Barras_Llegadas.extend(Lineas_Llegadas)
    Indice_Barras_Llegadas.extend(Transformadores_Llegadas)
    # ----------------------------------- Ordenamos --------------------------------
    Orden = pd.DataFrame({'Salida': Indice_Barras_Salida, 'Llegada': Indice_Barras_Llegadas})
    Orden = Orden.sort_values(by=['Salida', 'Llegada'])
    Orden = Orden.reset_index(drop=True)

    # Eliminamos filas duplicadas basándonos en las columnas 'Salida' y 'Llegada'
    i = 0
    while i < len(Orden) - 1:
        if Orden.loc[i, 'Salida'] == Orden.loc[i + 1, 'Salida'] and Orden.loc[i, 'Llegada'] == Orden.loc[i + 1, 'Llegada']:
            Orden = Orden.drop(i + 1).reset_index(drop=True)  # Elimina el elemento i+1 y reinicia los índices
        else:
            i += 1
            
    # Extraemos las columnas Salida y Llegada.
    Salidas = Orden['Salida']
    Llegadas = Orden['Llegada']

    # Creamos la matriz de incidencias sobre las barras.
    for idx, (valor_i, valor_j) in enumerate(itertools.zip_longest(Salidas, Llegadas, fillvalue=None)):
        if valor_i is not None and valor_j is not None:
            
            # Realiza las operaciones necesarias con los valores
            Barras_i = int(valor_i)
            Barras_j = int(valor_j)
            MatrizA[idx, Barras_i - 1] = (1)
            MatrizA[idx, Barras_j - 1] = (-1)

    # ======================================================================================================================================================================================================    
    #                                    Calculamos la matriz de incidencia para los elementos a Tierra.      
    # ======================================================================================================================================================================================================

    # Definimos un contador auxiliar.
    Contador = len(Bus_i)  # Comenzamos desde el final de las filas de las barras.
    for idx, valor in enumerate(indices_a_tierra):
        if valor_i is not None and valor_j is not None:
            MatrizA [Contador, valor - 1] = (1)
            Contador += 1  # Incrementamos el contador para la siguiente fila de elementos a tierra.

    return Admitancia_lineas, Admitancia_transformadores, Efecto_L_Barra_i, Efecto_L_Barra_j, Efecto_trx_Barra_i, Efecto_trx_Barra_j, indices_a_tierra, MatrizA, Admitancia_shunt

def Y_rama (Barra_i, Bus_i_lineas, Bus_j_lineas, Admitancia_lineas, Bus_i_trx, Bus_j_trx, Admitancia_transformadores, Admitancia_shunt, Bus_i_SHUNT, indices_a_tierra, Efecto_L_Barra_i, Efecto_L_Barra_j, Efecto_trx_Barra_i, Efecto_trx_Barra_j, B_lineas):
    import numpy as np
    import pandas as pd
    import itertools

    # =========================================================================================================================================================================================================================
    #                               Copiamos las variables que usaremos.
    # =========================================================================================================================================================================================================================

    Bus_i = Barra_i.copy()
    i_lineas = Bus_i_lineas.copy()
    j_lineas = Bus_j_lineas.copy()
    i_trx = Bus_i_trx.copy()
    j_trx = Bus_j_trx.copy()
    i_shunt = Bus_i_SHUNT.copy()
    Sucep_lineas = B_lineas.copy()  # Susceptancia de las lineas con unidades de Most (admitancias).

    # ************************************************************************************************************************************************************************************************************************
    #                                                   Comenzamos definiendo las dimensiones.
    # *************************************************************************************************************************************************************************************************************************

    Filas = len(Bus_i) + len(indices_a_tierra)  # Numero de filas: numero de barras + numero de elementos a tierra.
    Columnas = len(Bus_i) + len(indices_a_tierra)  # Numero de columnas: numero de barras.
    Y_rama = np.zeros((Filas, Columnas), dtype=complex)  # Matriz de admitancias de ramas.

    # =======================================================================================================================================================================================================
    #                        Seguimos llenando las posiciones correspondientes a los elementos entre barras.
    # =======================================================================================================================================================================================================

    # ---------------------- Salidas (Bus i) ----------------------
    Salidas_rama = []
    Salidas_rama.extend(Bus_i_lineas)
    Salidas_rama.extend(Bus_i_trx)
    # ---------------------- Llegadas (Bus j) ----------------------
    Llegadas_rama = []
    Llegadas_rama.extend(Bus_j_lineas)
    Llegadas_rama.extend(Bus_j_trx)
    # ---------------------- Admitancias ---------------------------
    Admitancias_rama = []
    Admitancias_rama.extend(Admitancia_lineas)
    Admitancias_rama.extend(Admitancia_transformadores)
    # ---------------------- Ordenamos -----------------------------
    Orden_2 = pd.DataFrame ({'Salida': Salidas_rama, 'Llegada': Llegadas_rama, 'Admitancia': Admitancias_rama})
    Orden_2 = Orden_2.sort_values(by=['Salida', 'Llegada'])
    Orden_2 = Orden_2.reset_index(drop=True)

    # ---------------------- Sumamos en paralelo -------------------
    i = 0
    while i < len(Orden_2) - 1:
        if Orden_2.loc[i, 'Salida'] == Orden_2.loc[i + 1, 'Salida'] and Orden_2.loc[i, 'Llegada'] == Orden_2.loc[i + 1, 'Llegada']:
            Orden_2.loc[i, 'Admitancia'] += Orden_2.loc[i + 1, 'Admitancia']
            Orden_2 = Orden_2.drop(i + 1).reset_index(drop=True)  # Elimina el elemento i+1 y reinicia los índices
        else:
            i += 1
            
    # Extraemos las columnas Salida y Llegada.
    Salidas = Orden_2['Salida']
    Llegadas = Orden_2['Llegada']
    Admitancias = Orden_2['Admitancia']

    # Creamos la matriz de incidencias sobre las barras.
    for idx, (valor_i, valor_j) in enumerate(itertools.zip_longest(Salidas, Llegadas, fillvalue=None)):
        if valor_i is not None and valor_j is not None:
            
            # Realiza las operaciones necesarias con los valores
            Y_rama[idx, idx] = Admitancias[idx]  # Asignamos la admitancia a la diagonal de la matriz.
            
    # =======================================================================================================================================================================================================
    #                        Seguimos llenando las posiciones correspondientes a los elementos a Tierra.
    # =======================================================================================================================================================================================================

    # Definimos un contador para acceder a las filas de tierra.
    Contador = len(Bus_i)  # Comenzamos a contar desde el final de las barras.

    # --------------------------- Sumamos sobre las barras i -----------------------------------------------
    for idx_lineas, valor_i in enumerate(i_lineas):
        for idx_shunt, valor_j in enumerate(i_shunt):
            if valor_i == valor_j:  # Si coinciden los valores
                print (f'Sumando admitancia de tierra {valor_j} a la barra {valor_i}')
                Efecto_L_Barra_i[idx_lineas-1] += Admitancia_shunt[idx_shunt]  # Sumar la admitancia correspondiente
                break  # Salimos del bucle interno si encontramos una coincidencia

    for idx_lineas, valor_j in enumerate(i_lineas):
        for idx_trx, valor_i in enumerate(i_trx):
            if valor_i == valor_j:  # Si coinciden los valores
                Efecto_L_Barra_i[idx_lineas-1] += Efecto_trx_Barra_i[idx_trx]  # Sumar la admitancia correspondiente
                break  # Salimos del bucle interno si encontramos una coincidencia

    # --------------------------- Sumamos sobre las barras j -------------------------------------------------
    for idx_lineas, valor_j in enumerate(j_lineas):
        for idx_trx, valor_i in enumerate(j_trx):
            if valor_i == valor_j:  # Si coinciden los valores
                Efecto_L_Barra_j[idx_lineas-1] += Efecto_trx_Barra_j[idx_trx]  # Sumar la admitancia correspondiente
                break  # Salimos del bucle interno si encontramos una coincidencia

    # ------------------- Creamos la matriz de incidencias sobre las conex a tierra. ------------------------
    # Sobre Bus i.
    for idx, valor in enumerate(indices_a_tierra):
        if valor is not None:
            Y_rama[Contador, Contador] += Efecto_L_Barra_i [idx]  # Asignamos la admitancia a la diagonal de la matriz.
            Contador += 1  # Incrementamos el contador para la siguiente fila de elementos a tierra. 
            
    Contador = len(Bus_i)  # Retomamos la cuenta desde el final de las barras.   

    # Sobre Bus j.
    for idx, valor in enumerate(indices_a_tierra):
        if valor is not None:
            Y_rama[Contador, Contador] += Efecto_L_Barra_j [idx]  # Asignamos la admitancia a la diagonal de la matriz.
            Contador += 1  # Incrementamos el contador para la siguiente fila de elementos a tierra. 
            
    return Y_rama

def Y_bus(MatrizA, Y_rama):
    
    MatrizAI =  np.transpose(MatrizA)  # Invertimos la matriz de incidencia para obtener la matriz de admitancias.
    Y_Bus = MatrizAI @ Y_rama @ MatrizA # Calculamos la matriz de admitancias del sistema.
    
    return Y_Bus