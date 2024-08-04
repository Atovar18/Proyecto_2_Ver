from Modulos import Lectura
import numpy as np
import pandas as pd
import itertools
from Modulos import Y_bus

# ================================================================================ Lectura de los datos. ================================================================================================================
GS, NR, FD, DC, Convergencia, Max_iter = Lectura.CONFIG ()

ID_Barras, Barra_i, Bus_type, V_pu, V_ang, P_gen, Q_gen, P_demanda, Q_demanda, Z_zip, I_zip, P_zip = Lectura.BUS ()

ID_lineas, Bus_i_lineas, Bus_j_lineas, R_lineas, X_lineas, B_lineas = Lectura.LINES ()

ID_trx, Bus_i_trx, Bus_j_trx, Xcc_trx, Tap_trx, Barra_tap = Lectura.TRX ()

ID_SHUNT, Bus_i_shunt, R_Shunt, X_Shunt = Lectura.SHUNT_ELEMENTS ()

# ============================================================================= Comprobación de las barras. ===============================================================================================================================================================================================================================
Lectura.COMPROBACION (Barra_i, Bus_i_lineas, Bus_j_lineas, Bus_i_trx, Bus_j_trx, Bus_i_shunt)

# ============================================================================= Cálculo de la matriz de incidencia nodal. ====================================================================================================================================================================================================================
MatrizA, elementos_a_tierra_arr, Barra_i_conex, Barra_j_conex, Y_linea, TRX_I, TRX_J, Tomas_a_tierra, SeriesTRX = Y_bus.Incidencia_Nodal(Barra_i, Bus_i_lineas, Bus_j_lineas, R_lineas, X_lineas, B_lineas, Bus_i_trx, Bus_j_trx, Xcc_trx, Tap_trx, Bus_i_shunt, R_Shunt, X_Shunt)

# ============================================================================= Cálculo de la matriz de admitancias de rama. ===============================================================================================================================================================================================================
Y_rama, Conex_Tierra, Bus_i_TRX_n, Bus_j_TRX_n = Y_bus.Y_rama(Barra_i_conex, Barra_j_conex, Y_linea, TRX_I, TRX_J, Tomas_a_tierra, R_Shunt, X_Shunt, B_lineas, elementos_a_tierra_arr, Barra_tap, Tap_trx, Bus_i_trx, Bus_j_trx, Bus_i_shunt, Bus_i_lineas, Bus_j_lineas)

# ============================================================================= Creación de la Ybus. =======================================================================================================================================================================================================================================
Y_Bus = Y_bus.Y_BUS (MatrizA, Y_rama)

# ============================================================================= METODOS NUMERICOS. ================================================================================================================================================================================================================================================

if GS == 'Y': 
    
    print ('Método de Gauss-Seidel.')


