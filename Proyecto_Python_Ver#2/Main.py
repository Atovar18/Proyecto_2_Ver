from Modulos import Lectura
from Modulos import Y_bus
import pandas as pd
import math

# ============================================================================== Comenzamos la lectura de los datos ==========================================================================================
# Ruta al archivo Excel
ruta_archivo = 'Datos_O/data_io3.xlsx'

# Cargar el archivo Excel
archivo_excel = pd.ExcelFile(ruta_archivo)

# =========================================================================== Lectura de datos ==========================================================================================

GS, NR, FD, DC, Convergencia, Max_iter = Lectura.CONFIG()  # Extraemos los datos para la configuracion.

ID_Barras, Barra_i, Bus_type, Modulo_V, Angulos_grados, P_gen, Q_gen, P_demanda, Q_demanda, Z_zip, I_zip, P_zip, ruta_archivo = Lectura.BUS()  # Extraemos los datos de las Barras.

ID_lineas, Bus_i_lineas, Bus_j_lineas, R_lineas, X_lineas, B_lineas = Lectura.LINES()  # Extraemos los datos de las lineas.

ID_trx, Bus_i_trx, Bus_j_trx, Xcc_trx, Tap_trx, Barra_tap, Barrai_TRX, Barraj_TRX = Lectura.TRX()  # Extraemos los datos de los transformadores.

ID_SHUNT, Bus_i_SHUNT, R_Shunt, X_Shunt = Lectura.SHUNT_ELEMENTS()  # Extraemos los datos de los elementos conectados a tierra.

# =========================================================================== Fin de la lectura de datos =================================================================================================================

# Ahora comprobamos que hay suficientes datos para realizar el calculo.
Lectura.COMPROBACION(Barra_i, Bus_i_lineas, Bus_j_lineas, Bus_i_trx, Bus_j_trx, Bus_i_SHUNT)

# =========================================================================== Fin de la comprobacion de datos ============================================================================================================
# ************************************************************************************************************************************************************************************************************************
# ************************************************************************************************************************************************************************************************************************
# =========================================================================== Comenzamos el calculo de la matriz de admitancias ==========================================================================================

MatrizA, indice_tierra, Admitancia_lineas, Admitancia_transformadores, Admitancia_shunt, Efecto_lineas_Barrai, Efecto_lineas_Barraj, Efecto_trx_barrai, Efecto_trx_barraj = Y_bus.Incidencia_Nodal(Bus_i_lineas, 
Bus_j_lineas, Bus_i_trx, Bus_j_trx, R_lineas, X_lineas, B_lineas, R_Shunt, X_Shunt, Tap_trx, Xcc_trx, Bus_i_SHUNT, Barrai_TRX, Barraj_TRX,Barra_i)

    
print ("Matriz de admitancias (MatrizA):")
print(MatrizA)














