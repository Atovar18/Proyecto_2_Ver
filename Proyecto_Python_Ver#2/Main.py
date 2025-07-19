from Modulos import Lectura
from Modulos import Y_bus
import pandas as pd
import math
import numpy as np

# =========================================================================== Lectura de datos ==========================================================================================

GS, NR, FD, DC, Convergencia, Max_iter = Lectura.CONFIG()  # Extraemos los datos para la configuracion.

ID_Barras, Barra_i, Bus_type, Modulo_V, Angulos_grados, P_gen, Q_gen, P_demanda, Q_demanda, Z_zip, I_zip, P_zip, ruta_archivo = Lectura.BUS()  # Extraemos los datos de las Barras.

ID_lineas, Bus_i_lineas, Bus_j_lineas, R_lineas, X_lineas, B_lineas,Indices_line_i, Indices_line_j = Lectura.LINES()  # Extraemos los datos de las lineas.

ID_trx, Bus_i_trx, Bus_j_trx, Xcc_trx, Tap_trx, Barra_tap, Indices_tap_i, Indices_tap_j,Barrai_TRX, Barraj_TRX = Lectura.TRX()  # Extraemos los datos de los transformadores.

ID_SHUNT, Bus_i_SHUNT, R_Shunt, X_Shunt = Lectura.SHUNT_ELEMENTS()  # Extraemos los datos de los elementos conectados a tierra.

# =========================================================================== Fin de la lectura de datos =================================================================================================================

# Ahora comprobamos que hay suficientes datos para realizar el calculo.
Lectura.COMPROBACION(Barra_i, Bus_i_lineas, Bus_j_lineas, Barrai_TRX, Barraj_TRX, Bus_i_SHUNT)

# =========================================================================== Fin de la comprobacion de datos ============================================================================================================
# ************************************************************************************************************************************************************************************************************************
# ************************************************************************************************************************************************************************************************************************
# =========================================================================== Comenzamos el calculo de la matriz de admitancias ==========================================================================================

Admitancia_lineas, Admitancia_transformadores, Efecto_L_Barra_i, Efecto_L_Barra_j, Efecto_trx_Barra_i, Efecto_trx_Barra_j, indices_a_tierra, MatrizA, Admitancia_shunt=Y_bus.Incidencia_Nodal(Bus_i_lineas, Bus_j_lineas, R_lineas, X_lineas, B_lineas, R_Shunt, X_Shunt, Tap_trx, Xcc_trx, Bus_i_SHUNT, Indices_tap_i, Indices_tap_j, Barra_i,Bus_i_trx, Bus_j_trx, Indices_line_i, Indices_line_j)

Y_rama = Y_bus.Y_rama(Barra_i, Bus_i_lineas, Bus_j_lineas, Admitancia_lineas, Bus_i_trx, Bus_j_trx, Admitancia_transformadores, Admitancia_shunt, Bus_i_SHUNT, indices_a_tierra, Efecto_L_Barra_i, Efecto_L_Barra_j, Efecto_trx_Barra_i, Efecto_trx_Barra_j, B_lineas)

Y_Bus = Y_bus.Y_bus(MatrizA, Y_rama)  # Calculamos la matriz de admitancias del sistema.

# =========================================================================== Fin del calculo de la matriz de admitancias ============================================================================================================
# ************************************************************************************************************************************************************************************************************************
# ************************************************************************************************************************************************************************************************************************














