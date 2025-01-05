import numpy as np
import itertools

def Newton_DC (P_gen, P_demanda, X_lineas, Xcc_trx, Bus_i_lineas, Bus_j_lineas, Bus_i_trx, Bus_j_trx, Bus_type):
    
    # Armamos la lista de potencias activas.
    P_esp = P_gen - P_demanda

    # Convertimos a listas las variables que nos interesan.
    X_lineas = list(X_lineas)
    Xcc_trx = list(Xcc_trx)
    Bus_i_lineas = list(Bus_i_lineas)
    Bus_j_lineas = list(Bus_j_lineas)
    Bus_i_trx = list(Bus_i_trx)
    Bus_j_trx = list(Bus_j_trx)

    # Unimos las listas
    X_lineas.extend(Xcc_trx)
    Bus_i_lineas.extend(Bus_i_trx)
    Bus_j_lineas.extend(Bus_j_trx)

    # Ordenamos los valores. 
        # Paso 1: Crear lista de tuplas
    Lista_combinada = list(zip(Bus_i_lineas, Bus_j_lineas, X_lineas))

    # Paso 2: Ordenar la lista de tuplas por el primer elemento de cada tupla (que corresponde a Barra_i)
    lista_combinada_ordenada = sorted(Lista_combinada, key=lambda x: x[0]) 

    # Paso 3: Desempaquetar en las listas originales
    Barra_i, Barra_j, X = map(list,zip(*lista_combinada_ordenada))

    # Creamos la matriz del tamaño total de pontencias del sistema.
    Matriz = np.zeros((len(P_esp), len(P_esp)))

    # Debemos armar la matriz con las suceptantcias entre las barras.
    for idx, (valor_i, valor_j) in enumerate(itertools.zip_longest(Barra_i, Barra_j, fillvalue=None)):
        if valor_i is not None and valor_j is not None:
            indice_ij = int(valor_i) - 1
            indice_ji = int(valor_j) - 1

            # Colocar los valores de X fuera de la diagonal principal
            Matriz[indice_ij, indice_ji] = -1/X[idx]
            Matriz[indice_ji, indice_ij] = -1/X[idx]  # Asegurar simetría en la 
            
    # Creamos una matriz diagonal donde sumamos todas las conexiones fuera de la diagonal.        
    aux = np.diagflat(np.sum(Matriz,axis=1))

    # Agregamos la matriz auxiliar a la matriz que esta fuera de la diagonal.
    Matriz = Matriz - aux

    # Encontrar las posiciones donde Bus_type tiene el valor "SL"
    indices_sl = np.where(Bus_type == "SL")[0]

    # Eliminar las filas y columnas correspondientes
    Matriz = np.delete(Matriz, indices_sl, axis=0)
    Matriz = np.delete(Matriz, indices_sl, axis=1)
    P_esp = np.delete(P_esp, indices_sl, axis=0)

    # Transponer la matriz fila para obtener la matriz columna.
    P_esp = np.matrix(P_esp)
    P_esp = np.transpose(P_esp)

    # Resolvemos el sistema de ecuaciones.
    Matriz = np.linalg.inv(Matriz)
    Matriz_angulos = Matriz@P_esp

    # Aproximamos los resultados.
    Matriz_angulos = np.round (Matriz_angulos, 4)

    # Encontrar las posiciones donde Bus_type tiene el valor "SL"
    Aux = np.where(Bus_type == "SL") 

    # Agregar los valores de los ángulos en las posiciones correspondientes.
    Angulo_grados = np.insert((Matriz_angulos), Aux [0], 0,axis= 0)
                
    Angulo_grados = np.round(Angulo_grados, 4)
    Angulo_grados = np.degrees(Angulo_grados)
    
    return Angulo_grados