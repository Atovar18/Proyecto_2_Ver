from Modulos import Lectura
from Modulos import Y_bus
from Modulos import Gauus
from Modulos import Sflow
from Modulos import Potencia
from Modulos import Newton_Rapson
from Modulos import Salida
from Modulos import Lineal
from Modulos import Desacoplado
import pandas as pd
import time 
import os




# ============================================================================= Inicio de la rutina. =======================================================================================================================================================================================================================================
Comienzo = time.time()

# //////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
#                                                                              Extracción de los datos.                                               
# //////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

GS, NR, FD, DC, Convergencia, Max_iter = Lectura.CONFIG ()

ID_Barras, Barra_i_totales, Bus_type, V_pu, V_ang, P_gen, Q_gen, P_demanda, Q_demanda, Z_zip, I_zip, P_zip, ruta_archivo = Lectura.BUS ()

ID_lineas, Bus_i_lineas, Bus_j_lineas, R_lineas, X_lineas, B_lineas = Lectura.LINES ()

ID_trx, Bus_i_trx, Bus_j_trx, Xcc_trx, Tap_trx, Barra_tap, Barrai_TRX, Barraj_TRX = Lectura.TRX ()

ID_SHUNT, Bus_i_shunt, R_Shunt, X_Shunt = Lectura.SHUNT_ELEMENTS ()

# ============================================================================= Comprobación de las conexiones. ================================================================================================================================================================================================================================
Lectura.COMPROBACION (Barra_i_totales, Bus_i_lineas, Bus_j_lineas, Bus_i_trx, Bus_j_trx, Bus_i_shunt)

# //////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
#                                                                              Ybus.                                                
# //////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

# ============================================================================= Cálculo de la matriz de incidencia nodal. ==================================================================================================================================================================================================================
MatrizA, elementos_a_tierra_arr, Barra_i_conex, Barra_j_conex, Y_linea, TRX_I, TRX_J, Tomas_a_tierra, SeriesTRX, Conex_lineas, ID_conex_totales, Bus_i_trx_tierra, Bus_j_trx_tierra = Y_bus.Incidencia_Nodal(Barra_i_totales, Bus_i_lineas, Bus_j_lineas, R_lineas, X_lineas, B_lineas, Bus_i_trx, Bus_j_trx, Xcc_trx, Tap_trx, Bus_i_shunt, R_Shunt, X_Shunt, ID_lineas, ID_trx, Barra_tap)

# ============================================================================= Cálculo de la matriz de admitancias de rama. ===============================================================================================================================================================================================================
Y_rama, Conex_Tierra, Bus_i_TRX_n, Bus_j_TRX_n = Y_bus.Y_rama(Barra_i_conex, Barra_j_conex, Y_linea, TRX_I, TRX_J, Tomas_a_tierra, R_Shunt, X_Shunt, B_lineas, elementos_a_tierra_arr, Barra_tap, Tap_trx, Bus_i_trx, Bus_j_trx, Bus_i_shunt, Bus_i_lineas, Bus_j_lineas, Bus_i_trx_tierra, Bus_j_trx_tierra, Barra_i_totales)

# ============================================================================= Creación de la Ybus. =======================================================================================================================================================================================================================================
Y_Bus = Y_bus.Y_BUS (MatrizA, Y_rama)

# //////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
#                                                                                METODOS NUMERICOS                                                
# //////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

# ============================================================================= Método de Gauss Saidel. =========================================================================================================================================================================================================================================

if GS == 'Y': 
    # Llamamos a la función de Gauss Saidel.
    Modulos_GS, Angulos_GS, Fasores_GS, Iteracion_GS, Error_GS, P_return_GS, Q_return_GS = Gauus.Gauss_Seidel (Y_Bus, Bus_type, P_gen, Q_gen, P_demanda, Q_demanda, V_pu, V_ang, Convergencia, Max_iter, Z_zip, I_zip, P_zip)
    
    # Calculamos los flujos.
    Salida_i_GS, Salida_j_GS, ID_GS, P_loss_GS, Q_loss_GS, Pij_GS, Qij_GS, Pji_GS, Qji_GS = Sflow.Flujos (Bus_i_lineas, Bus_j_lineas, ID_lineas, B_lineas, Barrai_TRX, Barraj_TRX, ID_trx, Tap_trx, Fasores_GS, Conex_lineas, SeriesTRX)
    
    # Calculamos las potencias de los generadores.   
    P_gen_GS, Q_gen_GS = Potencia.Potencia_entregada (Bus_type, Fasores_GS, Y_Bus)
    
# ============================================================================= Método de Newton Raphson. =========================================================================================================================================================================================================================================    

if NR == 'Y':
    
    # Llamamos a la función de Newton.
    Modulos_NR, Angulos_NR, P_return_NR, Q_return_NR, Iteracion_NR, Error_NR, Fasores_NR = Newton_Rapson.newtonRaphson(Convergencia, Max_iter,Y_Bus,P_gen,P_demanda,Q_gen,Q_demanda,V_pu,Bus_type, Z_zip, I_zip, P_zip)

    # Calculamos los flujos.
    Salida_i_NR, Salida_j_NR, ID_NR, P_loss_NR, Q_loss_NR, Pij_NR, Qij_NR, Pji_NR, Qji_NR = Sflow.Flujos (Bus_i_lineas, Bus_j_lineas, ID_lineas, B_lineas, Barrai_TRX, Barraj_TRX, ID_trx, Tap_trx, Fasores_NR, Conex_lineas, SeriesTRX)
    
    # Calculamos las potencias de los generadores.   
    P_gen_NR, Q_gen_NR = Potencia.Potencia_entregada (Bus_type, Fasores_NR, Y_Bus)

# ============================================================================= Método de Newton Raphson Desacoplado Rápido. =========================================================================================================================================================================================================================================    

if FD == 'Y':
    
    # Llamamos a la función de Desacople.
    Modulos_FD, Angulos_FD, P_salida_FD , Q_salida_FD, Iteracion_FD, Error_FD, Fasores_FD = Desacoplado.Desacople(V_pu, Y_Bus, P_gen, P_demanda, Q_gen, Q_demanda, Bus_type, Max_iter, Convergencia, Z_zip, I_zip, P_zip)
    
    # Calculamos los flujos.
    Salida_i_FD, Salida_j_FD, ID_FD, P_loss_FD, Q_loss_FD, Pij_FD, Qij_FD, Pji_FD, Qji_FD = Sflow.Flujos (Bus_i_lineas, Bus_j_lineas, ID_lineas, B_lineas, Barrai_TRX, Barraj_TRX, ID_trx, Tap_trx, Fasores_FD, Conex_lineas, SeriesTRX)
    
    # Calculamos las potencias de los generadores.   
    P_gen_FD, Q_gen_FD = Potencia.Potencia_entregada (Bus_type, Fasores_FD, Y_Bus)

# ============================================================================= Método de Newton Lineal. =========================================================================================================================================================================================================================================        
    
if DC == 'Y':
    
    # Llamaos a la función de Newton DC.
    Angulos_Lineales = Lineal.Newton_DC (P_gen, P_demanda, X_lineas, Xcc_trx, Bus_i_lineas, Bus_j_lineas, Bus_i_trx, Bus_j_trx, Bus_type)

# //////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
#                                                                                Escritura de resultados.                                              
# //////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

# Condición para la escritura de los resultados.
if GS == 'Y' or NR == 'Y' or DC == 'Y' or FD == 'Y':

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
    Lineas = pd.read_excel(ruta_archivo, sheet_name='LINES')
    Bus = pd.read_excel(ruta_archivo, sheet_name='BUS')
    TRX = pd.read_excel(ruta_archivo, sheet_name='TRX')
    SHUNT_ELEMENTS = pd.read_excel(ruta_archivo, sheet_name='SHUNT_ELEMENTS')
    
    # ----------------------------------------------------------------- Exportamos los datos al archivo Excel. --------------------------------------------------------------------------------------                                                           
    # Llamamos la función de escritura de los datos.
    Salida.Datos(writer, Lineas, Bus, TRX, SHUNT_ELEMENTS)

    # --------------------------------------------------------------- Gauss Saidel ---------------------------------------------------------------------------------
    if GS == 'Y':
        # Creamos la hoja de resultados.
        GS_S = pd.DataFrame().to_excel(writer, sheet_name='RESULTS GS', index=False)
        
        # Extraemos la hoja de flujos.
        SF_GS = pd.read_excel(ruta_archivo, sheet_name='POWER FLOW GS')
        
        # ----------------------------------------------------------------- Exportamos los datos al archivo Excel. --------------------------------------------------------------------------------------                                                           
        # Escribimos resultados.
        Salida.Gauss(writer, ID_Barras, Modulos_GS, Angulos_GS, P_gen_GS, Q_gen_GS, P_return_GS, Q_return_GS, Iteracion_GS, Error_GS)
        
        # Escribimos los flujos.
        Salida.Sflow_GS(writer, Pij_GS, Qij_GS, Pji_GS, Qji_GS, P_loss_GS, Q_loss_GS, ID_GS, Salida_i_GS, Salida_j_GS, SF_GS)
    
    # --------------------------------------------------------------- Newton Raphson ---------------------------------------------------------------------------------   
    if NR == 'Y':
        # Creamos la hoja de resultados.
        NR_S = pd.DataFrame().to_excel(writer, sheet_name='RESULTS NR', index=False)
        
        # Extraemos la hoja de flujos.
        SF_NR = pd.read_excel(ruta_archivo, sheet_name='POWER FLOW NR')
        
        # ----------------------------------------------------------------- Exportamos los datos al archivo Excel. --------------------------------------------------------------------------------------                                                           
        # Escribimos resultados.
        Salida.NR(writer, ID_Barras, Modulos_NR, Angulos_NR, P_gen_NR, Q_gen_NR, P_return_NR, Q_return_NR, Iteracion_NR, Error_NR)
        
        # Escribimos los flujos.
        Salida.Sflow_NR(writer, Pij_NR, Qij_NR, Pji_NR, Qji_NR, P_loss_NR, Q_loss_NR, ID_NR, Salida_i_NR, Salida_j_NR, SF_NR)  
        
    if DC == 'Y':
        # Creamos la hoja de resultados.
        DC_S = 'Y'
        
        # ----------------------------------------------------------------- Exportamos los datos al archivo Excel. --------------------------------------------------------------------------------------                                                                   
        # Escribimos resultados.
        Salida.Lineal(writer, DC_S, Angulos_Lineales, Barra_i_totales) 
        
    if FD == 'Y':
        # Creamos la hoja de resultados.
        FD_S = pd.DataFrame().to_excel(writer, sheet_name='RESULTS FD', index=False)  
        
        # Extraemos la hoja de flujos.
        SF_FD = pd.read_excel(ruta_archivo, sheet_name='POWER FLOW FD') 
        
                # ----------------------------------------------------------------- Exportamos los datos al archivo Excel. --------------------------------------------------------------------------------------                                                           
        # Escribimos resultados.
        Salida.FD(writer, ID_Barras, Modulos_FD, Angulos_FD, P_gen_FD, Q_gen_FD, P_salida_FD, Q_salida_FD, Iteracion_FD, Error_FD)
        
        # Escribimos los flujos.
        Salida.Sflow_FD(writer, Pij_FD, Qij_FD, Pji_FD, Qji_FD, P_loss_FD, Q_loss_FD, ID_FD, Salida_i_FD, Salida_j_FD, SF_FD)      



    # Cerramos la escritura.
    writer.close()
    print ()
    print ('Calculos guardados en la carpeta "Salida", archivo:', filename)
    print ()

if GS == 'N' and NR == 'N' and DC == 'N' and FD == 'N':
    print ('No se ha seleccionado ningún método de cálculo.')

# ============================================================================= Fin de la rutina. ==========================================================================================================================================================================================================================================
Final = time.time()
print ()
print ('El tiempo de ejecución es de: ', Final - Comienzo, 'segundos.')
print ()



