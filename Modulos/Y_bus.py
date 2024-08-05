import numpy as np
import pandas as pd
import itertools
# ============================================================================= Creación de las matrices Y_rama. ========================================================================================================

def Incidencia_Nodal (Barra_i, Bus_i_lineas, Bus_j_lineas, R_lineas, X_lineas, B_lineas, Bus_i_trx, Bus_j_trx, Xcc_trx, Tap_trx, Bus_i_shunt, R_Shunt, X_Shunt): 
    # Seleccionamos las variables a trabajar. 
    Barras = Barra_i
    Barra_i = Bus_i_lineas
    Barra_j = Bus_j_lineas
    Shunt_i = Bus_i_shunt
    trx_i = Bus_i_trx
    trx_j = Bus_j_trx
    Z_shunt = R_Shunt + 1j*X_Shunt
    Y_shunt = np.reciprocal(Z_shunt)

    # Armamos la impedancia de las lineas.
    Z_lineas = R_lineas + 1j*X_lineas

    # Redefinimos los indices para efectos de calculos.
    Barra_i = Barra_i.reset_index(drop=True)
    Barra_j = Barra_j.reset_index(drop=True)
    Shunt_i = Shunt_i.reset_index(drop=True)
    trx_i = trx_i.reset_index(drop=True)
    trx_j = trx_j.reset_index(drop=True)

    # Listas temporales para almacenar los valores que no serán eliminados  
    temp_i_lineas = []
    temp_j_lineas = []

    # Iterar sobre Bshunt_lineas con índice
    for i, valor in enumerate(B_lineas):
        # Verificar si el valor es diferente de 0
        if valor != 0:
            # Agregar los valores correspondientes a las listas temporales
            temp_i_lineas.append(Bus_i_lineas[i])
            temp_j_lineas.append(Bus_j_lineas[i])

    # Reasignar las listas temporales a Barra_i_lineas y Barra_j_lineas
    Barra_i_lineas = temp_i_lineas          # Estas son las conexiones a tierra en la barra i.
    Barra_j_lineas = temp_j_lineas          # Estas son las conexiones a tierra en la barra j.

    # ============================================================================ SECCION TRX ==========================================================================================================

    # Comenzamos directos con las admitanicas.
    Y_trx = np.reciprocal (Xcc_trx*1j)
    Y_trx = Y_trx
    
    # Definimos listas a TRX.
    SeriesTRX = []
    TRX_I =[]
    TRX_J = []

    # Bucle para sumar las series de los TRX sin importar el tap.
    for i in range (len(Y_trx)): 
        
        Serie = Tap_trx [i]*Y_trx[i]
        SeriesTRX.append (Serie)
        
    # Tomamos los valores no repetidos de las barras i y j para conocer su posición.
    Bus_i_TRX_T = list(set(Bus_i_trx))
    Bus_j_TRX_T = list(set(Bus_j_trx)) 
        
    # Crea una nueva lista sin los elementos donde Tap_trx tiene un valor de 1
    Bus_i_TRX_p = [elemento for elemento, tap in zip(Bus_i_trx, Tap_trx) if tap != 1.00000000] 
    Bus_j_TRX_p = [elemento for elemento, tap in zip(Bus_j_trx, Tap_trx) if tap != 1.00000000]       

    # Bucle para agregar las conexiones de TRX a Barra_i y Barra_j, si aplica.    
    for i in range (len(Y_trx)): 
        Bara_i = (1 - Tap_trx [i])*Y_trx[i]
        TRX_I.append (Bara_i)
        
    for i in range (len(Y_trx)): 
        
        Bara_j = (Tap_trx[i]*(Tap_trx [i] - 1))*Y_trx[i]
        TRX_J.append (Bara_j)

    # ============================================================================== Conexiones a Tierra ================================================================================

    # Convertimos todas los arreglos de pandas, a listas.
    TRX_I = TRX_I.tolist() if isinstance(TRX_I, pd.Series) else TRX_I
    TRX_J = TRX_J.tolist() if isinstance(TRX_J, pd.Series) else TRX_J
    B_lineas= B_lineas.tolist() if isinstance(B_lineas, pd.Series) else B_lineas
    Y_shunt= Y_shunt.tolist() if isinstance(Y_shunt, pd.Series) else Y_shunt
    
    Shunt_i = Bus_i_shunt.tolist() if isinstance(Bus_i_shunt, pd.Series) else Bus_i_shunt
    Bus_i_lineas = Bus_i_lineas.tolist() if isinstance(Bus_i_lineas, pd.Series) else Bus_i_lineas
    Bus_j_lineas = Bus_j_lineas.tolist() if isinstance(Bus_j_lineas, pd.Series) else Bus_j_lineas

    # Buscamos el numero de conexiones a tierra que no se deben ser más que el númeto total de barras.
    Bus_i_lineas.extend(Barra_j_lineas)
    Bus_i_lineas.extend(Bus_i_trx)
    Bus_i_lineas.extend(Bus_j_trx)
    Bus_i_lineas.extend(Bus_i_shunt)
    
    # Agregamos las conexiones a tierra de las lineas.
    B_lineas.extend(B_lineas)
    B_lineas.extend(TRX_I)
    B_lineas.extend(TRX_J)
    B_lineas.extend(Y_shunt)
    
    B2_lineas = np.array(B_lineas)
    B2_lineas = B2_lineas[B2_lineas != 0]
    
    if B2_lineas.size == 0:
        Conex = int(0)
        lineas = int(0)
        
    else: 
        # Paso 1: Combinar las listas
        combined_list = list(zip(Bus_i_lineas, B_lineas))

        # Paso 2: Ordenar las listas combinadas según los elementos de Bus_i_lineas
        combined_list.sort(key=lambda x: x[0])

        # Paso 3: Eliminar las posiciones donde los elementos de B_lineas sean 0
        combined_list = [pair for pair in combined_list if pair[1] != 0]

        # Paso 4: Eliminar las posiciones donde los elementos de Bus_i_lineas sean repetidos
        seen = set()
        unique_combined_list = []
        for pair in combined_list:
            if pair[0] not in seen:
                unique_combined_list.append(pair)
                seen.add(pair[0])


        # Separar las listas combinadas de nuevo en Bus_i_lineas y B_lineas
        lineas, Conex = zip(*unique_combined_list)
    
    
    # Escogemos el numero total de conexiones a tierra.
    if Conex == 0:
        Conexiones_a_Tierra = 0
        Tomas_a_tierra = Conexiones_a_Tierra
        elementos_a_tierra = 0
        
    else:
        Conexiones_a_Tierra = len(Conex) 
        Tomas_a_tierra = Conexiones_a_Tierra
        elementos_a_tierra = lineas
            
    # Calculamos las admitancias de las lineas.
    Y_linea = np.reciprocal (Z_lineas)
    Conex_lineas = Y_linea

    # ========================================================================= Mezclamos todas las listas. ==========================================================================================================

    # Definimos las listas correspondientes. 
    Barra_i = list(Barra_i)
    Barra_j = list(Barra_j)
    Y_linea = list(Y_linea)

    # Agregamos los valores a las listas.
    Barra_i.extend (Bus_i_trx)
    Barra_j.extend (Bus_j_trx)
    Y_linea.extend (SeriesTRX)

    # Convertimos todos los valores a enteros.
    for i in range (len(Barra_i)):
            tupa = int(Barra_i[i])
            Barra_i[i] = tupa
            
    for i in range (len(Barra_j)):  
        tupa = int(Barra_j[i])
        Barra_j[i] = tupa
        
    # Ordenamos los valores. 
    # Paso 1: Crear lista de tuplas
    lista_combinada = list(zip(Barra_i, Barra_j, Y_linea ))

    # Paso 2: Ordenar la lista de tuplas por el primer elemento de cada tupla (que corresponde a Barra_i)
    lista_combinada_ordenada = sorted(lista_combinada, key=lambda x: x[0]) 

    # Paso 3: Desempaquetar en las listas originales
    Barra_i, Barra_j, Y_linea  = map(list,zip(*lista_combinada_ordenada))

    # Paso 4: Regresamos las listas a su estado inical.
    Barra_i_conex = pd.Series(Barra_i)
    Barra_j_conex = pd.Series(Barra_j)
    Y_linea = pd.Series (Y_linea)

    # Convertimos los valores finales a listas.
    Barra_i_conex = list(Barra_i_conex)
    Barra_j_conex = list(Barra_j_conex)

    # Buscamos eliminar los valores repetidos.
    def eliminar_pares_duplicados_consecutivos(i, j):
            # Asegurarse de que las listas tienen la misma longitud
            if len(i) != len(j):
                return i, j 

            indice = 0
            # Usar un bucle while porque la longitud de las listas cambiará durante la iteración
            while indice < len(i) - 1:
                # Verificar si hay elementos consecutivos iguales en i
                if i[indice] == i[indice + 1]:
                    # Verificar si los elementos correspondientes en j también son iguales
                    if j[indice] == j[indice + 1]:
                        # Eliminar uno de los elementos duplicados de ambas listas
                        del i[indice + 1]
                        del j[indice + 1]
                        # No incrementar el índice para revisar nuevamente desde la misma posición
                        continue
                indice += 1
            return i, j

    # Obtenemos los nuevos indices sin valores repetidos.
    Barra_i_conex_n, Barra_j_conex_n = eliminar_pares_duplicados_consecutivos(Barra_i_conex, Barra_j_conex)

    # ======================================== Llenamos la matriz según las conexiones. ========================================== 
    # Encuentra el valor máximo entre ambas listas.

    max_value_c = int(max((Barras)))
    max_value_f = max(len(Barra_i_conex_n), len(Barra_j_conex_n))

    # Filas Totales con las conexiones a tierra.
    Filas_totales = int(max_value_f + Conexiones_a_Tierra)

    # Crea una matriz de ceros con el tamaño máximo.
    MatrizA = np.zeros((Filas_totales, max_value_c))

    # Comenzamos a agregar los valores de tierra después de la última barra.
    contador_trx = max_value_f

    # Combinar las listas con zip_longest
    for idx, (valor_i, valor_j) in enumerate(itertools.zip_longest(Barra_i_conex_n, Barra_j_conex_n, fillvalue=None)):
        if valor_i is not None and valor_j is not None:
            
            # Realiza las operaciones necesarias con los valores
            Barra_i = int(valor_i)
            Barra_j = int(valor_j)
            MatrizA[idx, Barra_i - 1] = (1)
            MatrizA[idx, Barra_j - 1] = (-1)

    # Manejo de conexiones a tierra (si es necesario)
    
    if elementos_a_tierra == 0: 
        elementos_a_tierra_arr = []
    else:
        elementos_a_tierra_arr = np.array(list(elementos_a_tierra))

    # Agrega el valor 1 en la matriz según los elementos únicos
    for elemento in elementos_a_tierra_arr:
        elemento = int(elemento)
        MatrizA[contador_trx, elemento - 1] = 1
        contador_trx+=1

    return MatrizA, elementos_a_tierra_arr, Barra_i_conex, Barra_j_conex, Y_linea, TRX_I, TRX_J, Tomas_a_tierra, SeriesTRX, Conex_lineas

def Y_rama (Barra_i_conex, Barra_j_conex, Y_linea, TRX_I, TRX_J, Tomas_a_tierra, R_Shunt, X_Shunt, B_lineas, elementos_a_tierra_arr, Barra_tap, Tap_trx, Bus_i_trx, Bus_j_trx, Bus_i_shunt, Bus_i_lineas, Bus_j_lineas):
    
  # Encontramos el número de filas totales con las conexiones entre barras.
    Filas_totales = len(Y_linea)

    # Agregamos las filas que poseen las conexiones a tierra.
    Filas_totales = Filas_totales + len (elementos_a_tierra_arr)

    # Creamos una matriz de ceros para la matriz de admitancias de rama.
    Matriz = np.zeros ((Filas_totales, Filas_totales), dtype = complex)

    # Seleccionamos los parametros para trabajarlos.
    Lineas = Y_linea
    Z_shunt = R_Shunt + 1j*X_Shunt
    TRX_PI = TRX_I
    TRX_JI = TRX_J
    L_Shunt = B_lineas
    Elementos_a_tierra_arr = np.array(elementos_a_tierra_arr)

    # Eliminamos los TRX que no tengan conexiones a tierra.
    Bus_i_TRX = [elemento for elemento, tap in zip(Bus_i_trx, Tap_trx) if tap != 1] 
    Bus_j_TRX = [elemento for elemento, tap in zip(Bus_j_trx, Tap_trx) if tap != 1] 

    # Creamos las listas de las conexiones a tierra, primero verificamos si misma esta vacia.
    if Elementos_a_tierra_arr.size == 0:
        Conex_totales = Lineas
        Conex_tierra = []
        pass

    else:
        Conex_Tierra = np.zeros(int(Tomas_a_tierra), dtype = complex)
        Conex_Tierra_1 = np.zeros(int(Tomas_a_tierra), dtype = complex)
        Conex_Tierra_2 = np.zeros(int(Tomas_a_tierra), dtype = complex)
        Conex_Tierra_3 = np.zeros(int(Tomas_a_tierra), dtype = complex)
        Conex_Tierra_4 = np.zeros(int(Tomas_a_tierra), dtype = complex)
        Conex_Tierra_5 = np.zeros(int(Tomas_a_tierra), dtype = complex)
        
    # =========================================== Conexiones a Tierra de TRX ==========================================================================================================

    # Bucle para sustituir los valores en i según la posición de la barra tap.
    Bus_i_p = np.copy(Bus_i_TRX)
    Bus_j_p = np.copy(Bus_j_TRX)
    
    if Bus_i_p.size == 0:
        pass
    
    else:
        for i, tap in enumerate(Barra_tap):
            valor_original = Bus_i_trx [i]
            Bus_i_p[i] = tap  # Sustituir en Bus_i_p
            if valor_original != tap:  # Solo si el valor es diferente
                Bus_j_p[i] = valor_original  # Agregar el valor original a Bus_j_TRX en la misma posición.
            
    # Iterar sobre Bus_i_TRX y TRX_I simultáneamente
    for i, bus_i in enumerate(Bus_i_p):
        bus_i = int(bus_i)
        # Insertar el valor de TRX_I en la posición indicada por Bus_i_TRX en la lista respectiva.
        Conex_Tierra_1[bus_i-1] += TRX_I[i]
        

    # Iterar sobre Bus_j_TRX y TRX_j simultáneamente
    for i, bus_i in enumerate(Bus_j_p):
        bus_i = int(bus_i)
        # Insertar el valor de TRX_I en la posición indicada por Bus_i_TRX en la lista respectiva.
        Conex_Tierra_2[bus_i-1] += TRX_J[i]

    # ============================== Cargas a tierra de Shunt_Element ==========================================================================================================
    Y_cargas = np.reciprocal(Z_shunt)

    # Iterar sobre BUS_I y Y_cargas simultáneamente
    for i, bus_i in enumerate(Bus_i_shunt):
        bus_i = int(bus_i)
        # Insertar el valor de TRX_I en la posición indicada por Bus_i_TRX en la lista respectiva.
        Conex_Tierra_3[bus_i-1] += Y_cargas[i]

    # ========================================= Cargas a tierra de Lineas =======================================================================================================
    
    if Elementos_a_tierra_arr.size == 0:
        pass
    
    else :                
        Y_Bshunt_l = [x / 2 for x in L_Shunt*1j]

        # Iterar sobre Barra_i_lineas y Y_Bshunt_l agregamos los efectos capacitivos de las líneas en la barra i.
        for i, bus_i in enumerate(Bus_i_lineas):
            bus_i = int(bus_i)
            # Insertar el valor de Y_Bshunt_l en la posición indicada por Bus_i_lineas en la lista respectiva.
            Conex_Tierra_4[bus_i-1] += Y_Bshunt_l[i]
            
        # Iterar sobre Barra_j_lineas y Y_Bshunt_l agregamos los efectos capacitivos de las líneas en la barra j.
        for i, bus_i in enumerate(Bus_j_lineas):
            bus_i = int(bus_i)
            # Insertar el valor de Y_Bshunt_l en la posición indicada por Bus_j_lineas en la lista respectiva.
            Conex_Tierra_5[bus_i-1] += Y_Bshunt_l[i]  
        
    # =============================================== Conexiones a tierra totales ======================================================================================================================================================
    
    if Elementos_a_tierra_arr.size == 0:
        Conex_totales = Lineas
        Conex_Tierra = int (0)
        pass
    
    else:              
    # Iteramos sobre el tamaño de la lista de conexiones a tierra y agregamos los valores de las otras listas.
        for i in range (len(Conex_Tierra)):
            
            Conex_Tierra [i] = Conex_Tierra_1 [i] + Conex_Tierra_2 [i] + Conex_Tierra_3 [i] + Conex_Tierra_4 [i] + Conex_Tierra_5 [i]  

        def filtrar_ceros_complejos(lista_numeros):
            # Filtrar la lista para excluir los números complejos que son 0 + 0j
            lista_filtrada = [num for num in lista_numeros if num != 0 + 0j]
            return lista_filtrada

        Conex_Tierra = filtrar_ceros_complejos(Conex_Tierra)

        # Crear la nueva lista combinando Z_lineas y Z_cargas
        Conex_totales = list(Lineas) + list(Conex_Tierra)

    # Actualizar la diagonal principal de MatrizZ_RAMA con los valores de nueva_lista
    for i in range(Filas_totales):
        Matriz[i, i] = Conex_totales[i]  
        

    return Matriz, Conex_Tierra, Bus_i_p, Bus_j_p
    

def Y_BUS (Matriz_A, Y_rama):

    A_T = np.transpose(Matriz_A)
    
    y_bus = A_T@Y_rama@Matriz_A    

    return y_bus
    
    
    