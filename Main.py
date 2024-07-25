from Modulos import Lectura

# ============================================================================= Lectura de los datos. ========================================================================================================
GS, NR, FD, DC, Convergencia, Max_iter = Lectura.CONFIG ()

ID_Barras, Barra_i, Bus_type, V_pu, V_ang, P_gen, Q_gen, P_demanda, Q_demanda, Z_zip, I_zip, P_zip = Lectura.BUS ()

ID_lineas, Bus_i_lineas, Bus_j_lineas, R_lineas, X_lineas, B_lineas = Lectura.LINES ()

ID_trx, Bus_i_trx, Bus_j_trx, Xcc_trx, Tap_trx = Lectura.TRX ()

ID_shunt, Bus_i_shunt, Bus_j_shunt, B_shunt = Lectura.SHUNT_ELEMENTS ()

# ============================================================================= Comprobación. ========================================================================================================

