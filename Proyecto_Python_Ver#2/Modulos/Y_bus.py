import numpy as np
import pandas as pd
import itertools

def Incidencia_Nodal(Bus_i_lineas, Bus_j_lineas, Bus_i_trx, Bus_j_trx, R_lineas, X_lineas, B_lineas, R_Shunt, X_Shunt, Tap_trx, Xcc_trx, Bus_i_SHUNT, Barrai_TRX, Barraj_TRX, Barra_i):
    # Copiamos las variables a trabajar.
    Barras_i = Barra_i.copy()
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


    # =========================================================================== Fin de la copia de las variables ==========================================================================================

    # Formamos las impedancias de las lineas, shunt y transformadores.
    Impedancia_lineas = np.array([complex(Resis_lineas[i], Reac_lineas[i]) for i in range(len(Resis_lineas))])
    Impedancia_shunt = np.array([complex(Resis_Shunt[i], Reac_Shunt[i]) for i in range(len(Resis_Shunt))])
    Impedancia_transformadores = np.array([complex(0, Reac_trx[i]) for i in range(len(Reac_trx))])

    # Convertimos las impedancias a admitancias.
    Admitancia_lineas = np.reciprocal(Impedancia_lineas)
    Admitancia_shunt = np.reciprocal(Impedancia_shunt)
    Admitancia_transformadores = Tap * np.reciprocal(Impedancia_transformadores) # Admitancias de los transformadores serie, entre barras.

    # ============================ Calculamos los posibles efectos a tierra de las lineas y transformadores. ==========================================================================================================
    # -------------------------------------------------------------- Efecto de las lineas ----------------------------------------------------
    Efecto = Suscep_lineas/2    # Efecto de las lineas.
    Efecto = np.array([complex(0, Efecto[i]) for i in range(len(Efecto))])  # Convertimos a complejo.
    Efecto_lineas_Barrai = Efecto.copy()  # Efecto de las barras de salida de las lineas.
    Efecto_lineas_Barraj = Efecto.copy()  # Efecto de las barras de llegada de las lineas.

    # Sumamos en paralelo las admitancias de las lineas y los efectos de las barras.
    # Crear un DataFrame con los datos
    df_lineas = pd.DataFrame({'Linea_Salida': Lineas_Salida, 'Linea_Llegada': Lineas_Llegadas, 'Admitancia': Admitancia_lineas, 'Efecto_Barrai': Efecto_lineas_Barrai, 'Efecto_Barraj': Efecto_lineas_Barraj})
    # Bucle para comparar y sumar
    i = 0
    while i < len(df_lineas) - 1:
        if df_lineas.loc[i, 'Linea_Salida'] == df_lineas.loc[i + 1, 'Linea_Salida'] and df_lineas.loc[i, 'Linea_Llegada'] == df_lineas.loc[i + 1, 'Linea_Llegada']:
            df_lineas.loc[i, 'Admitancia'] += df_lineas.loc[i + 1, 'Admitancia']
            df_lineas.loc[i, 'Efecto_Barrai'] += df_lineas.loc[i + 1, 'Efecto_Barrai']
            df_lineas.loc[i, 'Efecto_Barraj'] += df_lineas.loc[i + 1, 'Efecto_Barraj']
            df_lineas = df_lineas.drop(i + 1).reset_index(drop=True)
        else:
            i += 1   
    # Extraer los datos actualizados
    Lineas_Salida = df_lineas['Linea_Salida']
    Lineas_Llegadas = df_lineas['Linea_Llegada']
    Admitancia_lineas = df_lineas['Admitancia']
    Efecto_lineas_Barrai = df_lineas['Efecto_Barrai']
    Efecto_lineas_Barraj = df_lineas['Efecto_Barraj']

    # -------------------------------------------------------------- Efecto de los transformadores -----------------------------------------------------------------------------------------------
    Efecto_trx_barrai = (1-Tap) * Admitancia_transformadores  # Efecto de las barras de salida de los transformadores.
    Efecto_trx_barraj = ((Tap**2)-Tap) * Admitancia_transformadores # Efecto de las barras de llegada de los transformadores.
    # Creamos un DataFrame para los transformadores.
    df_transformadores = pd.DataFrame({'Transformador_Salida': Transformadores_Salida, 'Transformador_Llegada': Transformadores_Llegadas, 'Admitancia': Admitancia_transformadores, 'Efecto_Barrai': Efecto_trx_barrai, 'Efecto_Barraj': Efecto_trx_barraj, 'Indice i': Barrai_TRX, 'Indice j': Barraj_TRX})
    # Sumamos en paralelo las admitancias de las lineas y los efectos de las barras.
    # Bucle para comparar y sumar
    i = 0
    while i < len(df_transformadores) - 1:
        if df_transformadores.loc[i, 'Transformador_Salida'] == df_transformadores.loc[i + 1, 'Transformador_Salida'] and df_transformadores.loc[i, 'Transformador_Llegada'] == df_transformadores.loc[i + 1, 'Transformador_Llegada']:
            df_transformadores.loc[i, 'Admitancia'] += df_transformadores.loc[i + 1, 'Admitancia']
            df_transformadores.loc[i, 'Efecto_Barrai'] += df_transformadores.loc[i + 1, 'Efecto_Barrai']
            df_transformadores.loc[i, 'Efecto_Barraj'] += df_transformadores.loc[i + 1, 'Efecto_Barraj']
            df_transformadores = df_transformadores.drop(i + 1).reset_index(drop=True)
        else:
            i += 1

    # Extraer los datos actualizados
    Transformadores_Salida = df_transformadores['Transformador_Salida']
    Transformadores_Llegadas = df_transformadores['Transformador_Llegada']
    Admitancia_transformadores = df_transformadores['Admitancia']
    Efecto_trx_barrai = df_transformadores['Efecto_Barrai']
    Efecto_trx_barraj = df_transformadores['Efecto_Barraj']
    Indice_i_trx = df_transformadores['Indice i']
    Indice_j_trx = df_transformadores['Indice j']

    # ============================================================================================================================================================================================================================
    #                                                  Calculaomos la incidencia nodal de barras y elementos conectados a tierra.
    # ============================================================================================================================================================================================================================

    # Buscamos el total de los elementos conectados a tierra.
    Elementos_a_tierra = []
    Elementos_a_tierra.extend(Efecto_lineas_Barrai)
    Elementos_a_tierra.extend(Efecto_trx_barrai)
    Elementos_a_tierra.extend(Admitancia_shunt)
    # Eliminamos los elementos que son 0
    Elementos_a_tierra = [elemento for elemento in Elementos_a_tierra if elemento != 0]
    Elementos_a_tierra = list(set(Elementos_a_tierra))
    Elementos_a_tierra = len(Elementos_a_tierra)        # Número de elementos a tierra.

    # Definimos las dimensiones.
    Num_columnas = len(Barras_i)
    Num_filas = len(Lineas_Salida) + Elementos_a_tierra

    # Creamos la matriz de incidencia.
    MatrizA = np.zeros((Num_filas, Num_columnas))

    # Establecemos las conexiones entre las barras.
    Salidas = []
    Salidas.extend(Lineas_Salida)
    Salidas.extend(Transformadores_Salida)
    Llegadas = []
    Llegadas.extend(Lineas_Llegadas)
    Llegadas.extend(Transformadores_Llegadas)


    #Tenemos que limpiar las listas de salidas y llegadas los elementos repetidos.
    df_Barras = pd.DataFrame({'Salida': Salidas, 'Llegada': Llegadas})

    # Ordenamos la columna Bus i, por si hace falta.
    df_Barras = df_Barras.sort_values(by=['Salida', 'Llegada'])
    df_Barras = df_Barras.reset_index(drop=True)

    # Eliminamos filas duplicadas basándonos en las columnas 'Salida' y 'Llegada'
    i = 0
    while i < len(df_Barras) - 1:
        if df_Barras.loc[i, 'Salida'] == df_Barras.loc[i + 1, 'Salida'] and df_Barras.loc[i, 'Llegada'] == df_Barras.loc[i + 1, 'Llegada']:
            df_Barras = df_Barras.drop(i + 1).reset_index(drop=True)  # Elimina el elemento i+1 y reinicia los índices
        else:
            i += 1

    # Extraemos las columnas Salida y Llegada.
    Salidas = df_Barras['Salida']
    Llegadas = df_Barras['Llegada']

    # Creamos la matriz de incidencias sobre las barras.
    for idx, (valor_i, valor_j) in enumerate(itertools.zip_longest(Salidas, Llegadas, fillvalue=None)):
        if valor_i is not None and valor_j is not None:
            
            # Realiza las operaciones necesarias con los valores
            Barra_i = int(valor_i)
            Barra_j = int(valor_j)
            MatrizA[idx, Barra_i - 1] = (1)
            MatrizA[idx, Barra_j - 1] = (-1)
            
    # Ahora agregamos las conexiones a tierra de las lineas, transformadores y shunt.
    contador = Elementos_a_tierra
    indice_tierra = []
    indice_tierra.extend(Lineas_Salida)
    indice_tierra.extend(Indice_i_trx)
    indice_tierra.extend(Shunt_i)
    # Eliminamos los elementos duplicados en indice_tierra
    indice_tierra = list(set(indice_tierra))

    # Iteramos sobre los índices y valores de Elementos_a_tierras
    #elementos_a_tierra_arr = np.array(list(Elementos_a_tierras))
    for idx, elemento in enumerate(indice_tierra):
        elemento = int(elemento)
        MatrizA[contador, elemento - 1] = 1  # Usamos el valor del elemento para la columna
        contador += 1  # Movemos el contador para la siguiente fila.

    
    return MatrizA, indice_tierra, Admitancia_lineas, Admitancia_transformadores, Admitancia_shunt, Efecto_lineas_Barrai, Efecto_lineas_Barraj, Efecto_trx_barrai, Efecto_trx_barraj