from Modulos import Lectura
import numpy as np
import pandas as pd
import itertools
from Modulos import Y_bus

# ================================================================================ Lectura de los datos. ================================================================================================================
GS, NR, FD, DC, Convergencia, Max_iter = Lectura.CONFIG ()

ID_Barras, Barra_i, Bus_type, V_pu, V_ang, P_gen, Q_gen, P_demanda, Q_demanda, Z_zip, I_zip, P_zip = Lectura.BUS ()

ID_lineas, Bus_i_lineas, Bus_j_lineas, R_lineas, X_lineas, B_lineas = Lectura.LINES ()

ID_trx, Bus_i_trx, Bus_j_trx, Xcc_trx, Tap_trx = Lectura.TRX ()

ID_SHUNT, Bus_i_shunt, R_Shunt, X_Shunt = Lectura.SHUNT_ELEMENTS ()

# ============================================================================= Comprobación de las barras. =============================================================================================================
Lectura.COMPROBACION (Barra_i, Bus_i_lineas, Bus_j_lineas, Bus_i_trx, Bus_j_trx, Bus_i_shunt)

MatrizA, elementos_a_tierra_arr, Barra_i_conex, Barra_j_conex, Y_linea, TRX_I, TRX_J, Tomas_a_tierra, SeriesTRX = Y_bus.Incidencia_Nodal(Barra_i, Bus_i_lineas, Bus_j_lineas, R_lineas, X_lineas, B_lineas, Bus_i_trx, Bus_j_trx, Xcc_trx, Tap_trx, Bus_i_shunt)


print (MatrizA)
print ()
print (elementos_a_tierra_arr)
print ()
print (Barra_i_conex)
print ()
print (Barra_j_conex)
print ()
print (Y_linea)
print ()
print (TRX_I)
print ()
print (TRX_J)
print ()
print (Tomas_a_tierra)
print ()
print (SeriesTRX)
