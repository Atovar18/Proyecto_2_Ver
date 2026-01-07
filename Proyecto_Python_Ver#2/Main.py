from Modulos import Lectura
from Modulos import Y_bus
from Modulos import Gauss_Saidel
from Modulos import Sflow
from Modulos import Potencia
from Modulos import Salida
from Modulos import Newton_Rapson
from Modulos import Carga_Zip

import pandas as pd
import os
import time
import sympy as sp
import numpy as np

# ============================================================================= Inicio de la rutina. =======================================================================================================================================================================================================================================
Comienzo = time.time()

# //////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
#                                                                              Extracción de los datos.                                               
# //////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

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

# =========================================================================== Fin del calculo de la matriz de admitancias ===================================================================================================================================================
# ***************************************************************************************************************************************************************************************************************************************************************************
# ***************************************************************************************************************************************************************************************************************************************************************************
# =========================================================================== Comenzamos el calculo del sistema =============================================================================================================================================================


if GS == 'Y':
    # --------------------------------------------------------------------------- Método Gauss Saidel ---------------------------------------------------------------------------
    # Calculos.
    Modulos_GS, Angulos_GS, Fasores_GS, Iteraciones_GS, Error_GS, P_demanda_GS, Q_demanda_GS= Gauss_Saidel.Gauss_Seidel(P_gen, Q_gen, P_demanda, Q_demanda, Angulos_grados, Modulo_V, Y_Bus, Bus_type, Convergencia, Max_iter, Z_zip, I_zip, P_zip)

    # Flujos.
    Salidas_GS, Llegadas_GS, ID_GS, P_perdidas_GS, Q_perdidas_GS, P_ij_GS, P_ji_GS, Q_ij_GS, Q_ji_GS = Sflow.calculo_flujos(Modulos_GS, Fasores_GS, Admitancia_lineas, Admitancia_transformadores, Bus_i_lineas, Bus_j_lineas, Bus_i_trx, Bus_j_trx, Tap_trx, Efecto_L_Barra_i, Efecto_L_Barra_j, ID_lineas, ID_trx)

    # Generación.
    P_gen_GS, Q_gen_GS, Pi_GS, Qi_GS = Potencia.Potencia_Barras(Modulos_GS, Fasores_GS, Y_Bus, Bus_type, P_gen, Q_gen, P_demanda_GS, Q_demanda_GS)

if NR == 'Y':
    # --------------------------------------------------------------------------- Método Newton Raphson ---------------------------------------------------------------------------
    # Calculos.
    Modulos_NR, Angulos_NR, Fasores_NR, Iteraciones_NR, Error_NR, P_demanda_NR, Q_demanda_NR = Newton_Rapson.Newton_Raphson(P_gen, Q_gen, P_demanda, Q_demanda, Angulos_grados, Modulo_V, Y_Bus, Bus_type, Convergencia, Max_iter, Z_zip, I_zip, P_zip)
    
    # Flujos.
    Salidas_NR, Llegadas_NR, ID_NR, P_perdidas_NR, Q_perdidas_NR, P_ij_NR, P_ji_NR, Q_ij_NR, Q_ji_NR = Sflow.calculo_flujos(Modulos_NR, Fasores_NR, Admitancia_lineas, Admitancia_transformadores, Bus_i_lineas, Bus_j_lineas, Bus_i_trx, Bus_j_trx, Tap_trx, Efecto_L_Barra_i, Efecto_L_Barra_j, ID_lineas, ID_trx)
    
    # Generación.
    P_gen_NR, Q_gen_NR, Pi_NR, Qi_NR = Potencia.Potencia_Barras(Modulos_NR, Fasores_NR, Y_Bus, Bus_type, P_gen, Q_gen, P_demanda_NR, Q_demanda_NR)
    
    


# //////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
#                                                                                Escritura de resultados.                                              
# //////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

# Condición para la escritura de los resultados.
if GS == 'Y' or DC == 'Y' or FD == 'Y':

    # Crear la carpeta 'Salida' si no existe
    output_dir = 'Salida'
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Generar un nombre de archivo único
    base_filename = 'Resultado'
    extension = '.xlsx'
    filename = base_filename + extension
    counter = 1

    # Asegurarse de que el nombre de archivo sea único
    while os.path.exists(os.path.join(output_dir, filename)):
        filename = f"{base_filename}{counter}{extension}"
        counter += 1
        
    # Crear el archivo de salida en la carpeta 'Salida'
    output_path = os.path.join(output_dir, filename)
    writer = pd.ExcelWriter(output_path, engine='xlsxwriter')

    # Leemos los datos de nuestro master.
    # ----------------------------------------------------------------- Datos --------------------------------------------------------------------------------------
    Bus = pd.read_excel(ruta_archivo, sheet_name='BUS')
    Lineas = pd.read_excel(ruta_archivo, sheet_name='LINES')
    TRX = pd.read_excel(ruta_archivo, sheet_name='TRX')
    SHUNT_ELEMENTS = pd.read_excel(ruta_archivo, sheet_name='SHUNT_ELEMENTS')

    # ----------------------------------------------------------------- Exportamos los datos al archivo Excel. --------------------------------------------------------------------------------------                                                           
    # Llamamos la función de escritura de los datos.
    Salida.Datos(writer, Lineas, Bus, TRX, SHUNT_ELEMENTS)

    if GS == 'Y':
        # Creamos la hoja de resultados.
        GS_S = pd.DataFrame().to_excel(writer, sheet_name='RESULTS GS', index=False)
        
        # Extraemos la hoja de flujos.
        SF_GS = pd.DataFrame().to_excel(writer, sheet_name='POWER FLOW GS', index=False)
        
        # Exportamos los datos de las barras.
        Salida.Salida_GS(writer, Modulos_GS, Angulos_GS, P_gen_GS, Q_gen_GS, P_demanda_GS, Q_demanda_GS, Error_GS, Iteraciones_GS, ID_Barras, 
                        Pi_GS, Qi_GS)

        # Exportamos los datos de los flujos.
        Salida.Sflow_GS(writer, P_perdidas_GS, Q_perdidas_GS, P_ij_GS, P_ji_GS, Salidas_GS, Llegadas_GS, ID_GS, Q_ij_GS, Q_ji_GS)
        # ----------------------------------------------------------------- Exportamos los datos al archivo Excel. --------------------------------------------------------------------------------------


    # Cerramos la escritura.
    writer.close()
    print ()
    print ('Calculos guardados en la carpeta "Salida", archivo:', filename)
    print ()

if GS == 'N' and NR == 'N' and DC == 'N' and FD == 'N':
    print ('No se ha seleccionado ningún método de cálculo.')
    print ()

# ============================================================================= Fin de la rutina. ==========================================================================================================================================================================================================================================
Final = time.time()
print ()
print ('El tiempo de ejecución es de: ', Final - Comienzo, 'segundos.')
print ()

