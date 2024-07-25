import pandas as pd
import math


# =================================================== Comenzamos la lectura de los datos =================================================================
# Ruta al archivo Excel
ruta_archivo = 'Datos/Data_io.xlsx'

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
    Barras = Barras.sort_values(by='Bus i')

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

    # Bucle para V_pu: Si el valor es None, reemplaza con 1.
    for k in range(len(V_pu)):
        if Modulo_V[k] == None or Modulo_V[k] == 0:
            Modulo_V[k] = 1
            
        else:
            continue
        
    # Aplicamos los casos que apliquen el calculo de la cargas de voltaje variable, del tipo Zip.
    for i , k in enumerate (P_load):
        
        # Calculamos la potencia activa del modelo Zip.
        P = P_load[i]*(Z_zip[i]*(Modulo_V[i]**2) + I_zip[i]*(Modulo_V [i])+ P_zip[i])
        
        # Calculamos la potencia reactiva del modelo Zip.
        Q = Q_load[i]*(Z_zip[i]*(Modulo_V[i]**2) + I_zip[i]*(Modulo_V [i])+ P_zip[i])
        
        # Si P o Q son 0, no se hace nada, pero si son diferentes de 0, realizamos las correspondiente sustitución.
        if P == 0: 
            P_load [i] = P_load[i]
        
        else:
            P_load [i] = P
            
        if Q == 0:
            Q_load [i] = Q_load[i]
        
        else:
            Q_load [i] = Q
            
        # Ahora podemos retornar los valores calculados y extraidos de los datos.
        
    return ID_Barras, Barra_i, Bus_type, Modulo_V, Angulos_grados, P_gen, Q_gen, P_load, Q_load, Z_zip, I_zip, P_zip


            
  
print ()
print (archivo_excel.sheet_names)
print ()

# Seleccionamos la hoja de calculo LINES.
Lineas = archivo_excel.parse('LINES')

# Eliminamos las Lineas que esten apagadas, para simplificar la cuentas.
Lineas = Lineas[Lineas.iloc[:, 0] != 'OFF']

# Ordenamos la columna Bus i, por si hace falta.
Lineas = Lineas.sort_values(by='Bus i')

# Redefinimos los indices para efectos de calculos.
Lineas = Lineas.reset_index(drop=True)


print ()
print (Lineas)          
print ()
print ()
print ()
print ()
print ()
print ()


