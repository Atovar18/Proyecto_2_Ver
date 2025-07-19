import pandas as pd
import math


# ============================================================================== Comenzamos la lectura de los datos ==========================================================================================
# Ruta al archivo Excel
ruta_archivo = 'Datos_O/EjemploP6.xlsx'

# Cargar el archivo Excel
archivo_excel = pd.ExcelFile(ruta_archivo)

def CONFIG ():  
    
    # Seleccionamos la hoja de calculo CONFIG.
    Configuracion = archivo_excel.parse('CONFIG')
    
    # Extraemos los valores de las variables de configuracion.
    GS = Configuracion.iloc[0,1]
    NR = Configuracion.iloc[1,1]
    FD = Configuracion.iloc[2,1]
    DC = Configuracion.iloc[3,1]
    Convergencia = Configuracion.iloc[5,1]
    Max_iter = Configuracion.iloc[6,1]
    
    return GS, NR, FD, DC, Convergencia, Max_iter

def BUS ():

    # Seleccionamos la hoja de calculo BUS.
    Barras = archivo_excel.parse('BUS')

    # Eliminamos las barras que esten apagadas, para simplificar la cuentas.
    Barras = Barras[Barras.iloc[:, 0] != 'OFF']

    # Ordenamos la columna Bus i, por si hace falta.
    Barras = Barras.sort_values(by=['Bus i'])

    # Redefinimos los indices para efectos de calculos.
    Barras = Barras.reset_index(drop=True)

    # Extraemos los valores de las variables de BUS.
    ID_Barras = Barras.iloc[:, 1]
    Barra_i = Barras.iloc[:, 2]
    Bus_type = Barras.iloc[:, 3]
    V_pu = Barras.iloc[:, 4]
    V_ang = Barras.iloc[:, 5]           # No estoy sustiyendo los valores de none por 0 aun.
    P_gen = Barras.iloc[:, 6]
    Q_gen = Barras.iloc[:, 7]
    P_load = Barras.iloc[:, 8]
    Q_load = Barras.iloc[:, 9]
    Z_zip = Barras.iloc[:, 10]
    I_zip = Barras.iloc[:, 11]
    P_zip = Barras.iloc[:, 12]
    
    # Creación de matriz para los generadores en paralelo. 
    # Crear un DataFrame con los datos
    df = pd.DataFrame({'ID_Barras': ID_Barras, 'Barra_i': Barra_i, 'Bus_type': Bus_type, 'V_pu': V_pu, 'V_ang': V_ang, 'P_gen': P_gen, 'Q_gen': Q_gen, 'P_load': P_load, 'Q_load': Q_load, 'Z_zip': Z_zip, 'I_zip': I_zip, 'P_zip': P_zip})

    # Bucle para comparar y sumar
    i = 0
    while i < len(df) - 1:
        if df.loc[i, 'Barra_i'] == df.loc[i + 1, 'Barra_i']:
            df.loc[i, 'P_gen'] += df.loc[i + 1, 'P_gen']
            df.loc[i, 'Q_gen'] += df.loc[i + 1, 'Q_gen']            
            df = df.drop(i + 1).reset_index(drop=True)
        else:
            i += 1
            
    # Separar los datos en variables individuales 
    ID_Barras = df['ID_Barras']
    Barra_i = df['Barra_i']
    Bus_type = df['Bus_type']
    V_pu = df['V_pu']
    V_ang = df['V_ang']
    P_gen = df['P_gen']
    Q_gen = df['Q_gen']
    P_load = df['P_load']
    Q_load = df['Q_load']
    Z_zip = df['Z_zip']
    I_zip = df['I_zip']
    P_zip = df['P_zip']
    
    # Copia de las variables originiales para no afectar los valores originales.
    Angulos_grados = V_ang.copy()

    # Bucle para Angulo_grados: Si el valor es None, reemplaza con 0    
    for i in range(len(Angulos_grados)):
        if math.isnan(Angulos_grados[i]):
            Angulos_grados[i] = 0
            
        else: 
            continue

    # Copia de las variables originiales para no afectar los valores originales.   
    Modulo_V = V_pu.copy()
    P_demanda = P_load.copy()
    Q_demanda = Q_load.copy()

    # Bucle para V_pu: Si el valor es None, reemplaza con 1.
    for k in range(len(V_pu)):
        if Modulo_V[k] == None or Modulo_V[k] == 0:
            Modulo_V[k] = 1
            
        else:
            continue
        
    # Aplicamos los casos que apliquen el calculo de la cargas de voltaje variable, del tipo Zip.
    for i , k in enumerate (P_load):
        
        # Calculamos la potencia activa del modelo Zip.
        P = P_demanda[i]*(Z_zip[i]*(Modulo_V[i]**2) + I_zip[i]*(Modulo_V [i])+ P_zip[i])
        
        # Calculamos la potencia reactiva del modelo Zip.
        Q = Q_demanda[i]*(Z_zip[i]*(Modulo_V[i]**2) + I_zip[i]*(Modulo_V [i])+ P_zip[i])
        
        # Si P o Q son 0, no se hace nada, pero si son diferentes de 0, realizamos las correspondiente sustitución.
        if P == 0: 
            P_demanda [i] = P_demanda[i]
        
        else:
            P_demanda [i] = P
            
        if Q == 0:
            Q_demanda [i] = Q_demanda[i]
        
        else:
            Q_demanda [i] = Q
            
        # Ahora podemos retornar los valores calculados y extraidos de los datos.
        
    return ID_Barras, Barra_i, Bus_type, Modulo_V, Angulos_grados, P_gen, Q_gen, P_demanda, Q_demanda, Z_zip, I_zip, P_zip, ruta_archivo

def LINES ():

    # Seleccionamos la hoja de calculo LINES.
    Lineas = archivo_excel.parse('LINES')

    # Eliminamos las Lineas que esten apagadas, para simplificar la cuentas.
    Lineas = Lineas[Lineas.iloc[:, 0] != 'OFF']

    # Ordenamos la columna Bus i, por si hace falta.
    Lineas = Lineas.sort_values(by=['Bus i', 'Bus j'])

    # Redefinimos los indices para efectos de calculos.
    Lineas = Lineas.reset_index(drop=True)

    # Extraemos los valores importantes de las listas Lineas.
    ID_lineas = Lineas.iloc[:, 1]
    Bus_i_lineas = Lineas.iloc[:, 2]
    Bus_j_lineas = Lineas.iloc[:, 3]
    R_lineas = Lineas.iloc[:, 4]
    X_lineas = Lineas.iloc[:, 5]
    B_lineas = Lineas.iloc[:, 6]
    
    # Creamos una nueva variable para almacenar los índices donde Tap_trx es distinto de 1
    Indices_line_i = Lineas.loc[Lineas['Bshunt (p.u.)'] != 0, 'Bus i'].tolist()
    Indices_line_j = Lineas.loc[Lineas['Bshunt (p.u.)'] != 0, 'Bus j'].tolist()
    
    return ID_lineas, Bus_i_lineas, Bus_j_lineas, R_lineas, X_lineas, B_lineas, Indices_line_i, Indices_line_j
    
def TRX ():

    # Seleccionamos la hoja TRX para extraer los datos de los Transformadores.
    Transformadores = archivo_excel.parse('TRX')

    # Eliminamos los Transformadores que esten apagadas, para simplificar la cuentas.
    Transformadores = Transformadores[Transformadores.iloc[:, 0] != 'OFF']

    # Ordenamos la columna Bus i, por si hace falta.
    Transformadores = Transformadores.sort_values(by=['Bus i', 'Bus j'])

    # Redefinimos los indices para efectos de calculos.
    Transformadores = Transformadores.reset_index(drop=True)

    # Extraemos los valores importantes de las listas Transformadores.
    ID_trx = Transformadores.iloc[:, 1]
    Bus_i_trx = Transformadores.iloc[:, 2]
    Bus_j_trx = Transformadores.iloc[:, 3]
    Xcc_trx = Transformadores.iloc[:, 4]
    Tap_trx = Transformadores.iloc[:, 5]
    Barra_tap = Transformadores.iloc[:, 6]
    
    # Creamos una copia para efectos de los valores originales para control de los flujos.
    Barrai_TRX = Bus_i_trx.copy()
    Barraj_TRX = Bus_j_trx.copy()

    
    for i, tap in enumerate(Barra_tap):
        valor_original = Bus_i_trx [i]
        Barrai_TRX[i] = tap  # Sustituir en Bus_i_p
        if valor_original != tap:  # Solo si el valor es diferente
            Barraj_TRX[i] = valor_original  # Agregar el valor original a Bus_j_TRX en la misma posición.
            
    # Creamos una nueva variable para almacenar los índices donde Tap_trx es distinto de 1
    Indices_tap_i = Transformadores.loc[Transformadores['TAP'] != 1, 'Bus i'].tolist()
    Indices_tap_j = Transformadores.loc[Transformadores['TAP'] != 1, 'Bus j'].tolist()
    
    # Actualizamos las variables Bus_i_trx y Bus_j_trx con las nuevas listas.
    
    return ID_trx, Bus_i_trx, Bus_j_trx, Xcc_trx, Tap_trx, Barra_tap, Indices_tap_i, Indices_tap_j,Barrai_TRX, Barraj_TRX

def SHUNT_ELEMENTS ():

    # Seleccionamos la hoja de SHUNT ELEMENTS.
    Elementos_a_tierra = archivo_excel.parse('SHUNT_ELEMENTS')

    # Eliminamos los Elementos_a_tierra que esten apagadas, para simplificar la cuentas.
    Elementos_a_tierra = Elementos_a_tierra[Elementos_a_tierra.iloc[:, 0] != 'OFF']

    # Ordenamos la columna Bus i, por si hace falta.
    Elementos_a_tierra = Elementos_a_tierra.sort_values(by='Bus i')

    # Redefinimos los indices para efectos de calculos.
    Elementos_a_tierra = Elementos_a_tierra.reset_index(drop=True)

    # Extraemos los valores importantes de las listas Elementos_a_tierra.
    ID_SHUNT = Elementos_a_tierra.iloc[:, 1]
    Bus_i_SHUNT = Elementos_a_tierra.iloc[:, 2]
    R_Shunt = Elementos_a_tierra.iloc[:, 3]
    X_Shunt = Elementos_a_tierra.iloc[:, 4]
    
    return ID_SHUNT, Bus_i_SHUNT, R_Shunt, X_Shunt

# ==================================================================================== Comprobación de las Barras =========================================================================================================================================

def COMPROBACION (Barra_i, Bus_i_lineas, Bus_j_lineas, Bus_i_trx, Bus_j_trx, Bus_i_shunt):
    
    # Buscamos los valores totales de las barras.
    Max_Barra = max (Barra_i)
    
    # Definimos una lista con todos los valores de las conexiones.
    Valores_maximos = []
    Valores_maximos.append(list(Bus_i_trx))
    Valores_maximos.append(list(Bus_j_trx))
    Valores_maximos.append(list(Bus_i_lineas))
    Valores_maximos.append(list(Bus_j_lineas))
    Valores_maximos.append(list(Bus_i_shunt))   
    
    # Aplanar la lista de listas en una sola lista
    Valores_aplanados = [item for sublist in Valores_maximos for item in sublist]

    # Encontrar el valor máximo
    Valor_maximo = max(Valores_aplanados)
    
    # Realizamos la comparación entre los valores.
    if Max_Barra == Valor_maximo:
        print ()
        print ('Las conexiones coinciden.')
        print ()
    
    else:
        print ()
        print ('Las conexiones no coinciden.')
        print ('Barras:',Max_Barra)
        print ('Elementos interconectados:',Valor_maximo) 
        print ()
        exit ()
    
    return