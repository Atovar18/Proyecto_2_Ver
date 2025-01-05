import pandas as pd
import numpy as np

def Datos (writer, Lineas, Bus, TRX, SHUNT_ELEMENTS):
    
    # Eliminamos los datos que estan apagados, para simplificar la cuentas.
    Lineas = Lineas[Lineas.iloc[:, 0] != 'OFF']
    Bus = Bus[Bus.iloc[:, 0] != 'OFF']
    TRX = TRX[TRX.iloc[:, 0] != 'OFF']
    SHUNT_ELEMENTS = SHUNT_ELEMENTS[SHUNT_ELEMENTS.iloc[:, 0] != 'OFF']
    
    # Exportamos los datos al archivo Excel.
    Lineas.to_excel(writer, sheet_name='LINES', index=False)
    Bus.to_excel(writer, sheet_name='BUS', index=False)
    TRX.to_excel(writer, sheet_name='TRX', index=False)
    SHUNT_ELEMENTS.to_excel(writer, sheet_name='SHUNT ELEMENTS', index=False)
    
    return

def Gauss (writer, ID_Barras, Fasores_GS, Angulos_GS, P_gen_GS, Q_gen_GS, P_demanda, Q_demanda, Iteracion_GS, Error_GS):
    
    # =============================================== Transformamos los datos para Gauss Saidel ===========================================================
    # Convertimos los resultados en un dataframe de pandas.
    Resultados_GS = pd.DataFrame (Fasores_GS)
    angulos_grados_GS = pd.DataFrame (Angulos_GS)
    P_generada = pd.DataFrame (P_gen_GS)
    Q_generada = pd.DataFrame (Q_gen_GS)
    P_i = [] # Lista para almacenar la potencia generada menos la demanda
    Q_i = [] # Lista para almacenar la potencia generada menos la demanda

    # Agregamos los valores a las listas.
    for i in range(len(P_generada)): 
        P_i.append (P_generada.values[i] - P_demanda.values[i])
        Q_i.append (Q_generada.values[i] - Q_demanda.values[i])

    # Aproximamos nuestros resultados.
    P_i = np.round (P_i, 4)
    Q_i = np.round (Q_i, 4)
    Q_demanda = np.round (Q_demanda,4)
    P_demanda = np.round (P_demanda,4)

    # Convertimos las vairables a un dataframe de pandas.
    P_i = pd.DataFrame (P_i)
    Q_i = pd.DataFrame (Q_i)
    Q_demanda = pd.DataFrame (Q_demanda)
    P_demanda = pd.DataFrame (P_demanda)
    ID_Barras = pd.DataFrame (ID_Barras)

    # Enviamos a Exel los resultados.
    ID_Barras.to_excel(writer, sheet_name='RESULTS GS', header= ['Bus i'], index=False, startrow=1, startcol=0)
    Resultados_GS.to_excel(writer, sheet_name='RESULTS GS', header= ['|V| (pu)'], index=False, startrow=1, startcol=1)
    angulos_grados_GS.to_excel(writer, sheet_name='RESULTS GS', header= ['<V (degree)>'], index=False, startrow=1, startcol=2)
    P_generada.to_excel(writer, sheet_name='RESULTS GS', header= ['Pgen (pu)'], index=False, startrow=1, startcol=5)
    Q_generada.to_excel(writer, sheet_name='RESULTS GS', header= ['Qgen (pu)'], index=False, startrow=1, startcol=6)
    P_demanda.to_excel(writer, sheet_name='RESULTS GS', header= ['Pload (pu)'], index=False, startrow=1, startcol=7)
    Q_demanda.to_excel(writer, sheet_name='RESULTS GS', header= ['Qload (pu)'], index=False, startrow=1, startcol=8)
    P_i.to_excel(writer, sheet_name='RESULTS GS', header= ['Pi (pu)'], index=False, startrow=1, startcol=3)
    Q_i.to_excel(writer, sheet_name='RESULTS GS', header= ['Qi (pu)'], index=False, startrow=1, startcol=4)
    
    # Escribimos los datos en la hoja 'RESULTS GS' en posiciones especificas.
    worksheet = writer.sheets['RESULTS GS']
    worksheet.write(0, 0, 'Iteraciones')
    worksheet.write(0, 1, Iteracion_GS)
    worksheet.write(0, 2, 'Error')
    worksheet.write(0, 3, Error_GS)


    return


def Sflow_GS (writer, Pij_GS, Qij_GS, Pji_GS, Qji_GS, P_loss_GS, Q_loss_GS, ID_lineas, Bus_i_lineas, Bus_j_lineas, SF_GS):
    
    # Extrayendo la parte real de cada elemento en la lista
    P_ij_GS = Pij_GS
    Q_ij_GS = Qij_GS
    P_ji_GS = Pji_GS
    Q_ji_GS = Qji_GS
    
    # Aproximamos los resultados.
    P_ij_GS = np.round (P_ij_GS, 4)
    Q_ji_GS = np.round (Q_ji_GS, 4)
    P_ji_GS = np.round (P_ji_GS, 4)
    Q_ij_GS = np.round (Q_ij_GS, 4)
    Perdidas_P_GS = np.round (P_loss_GS, 4)
    Perdidas_Q_GS = np.round (Q_loss_GS, 4)

    # =============================================== Transformamos los datos ===========================================================
    ID_Lineas = pd.DataFrame (ID_lineas, columns=['Ident.'])
    Barra_i = pd.DataFrame (Bus_i_lineas, columns=['Bus i'])
    Barra_j = pd.DataFrame (Bus_j_lineas, columns=['Bus j '])
    P_ij_GS = pd.DataFrame (P_ij_GS, columns=['P_ij (pu)'])
    Q_ij_GS = pd.DataFrame (Q_ij_GS, columns=['Q_ij (pu)'])
    P_ji_GS = pd.DataFrame (P_ji_GS, columns=['P_ji (pu)'])
    Q_ji_GS = pd.DataFrame (Q_ji_GS, columns=['Q_ji (pu)'])
    Perdidas_P_GS = pd.DataFrame (Perdidas_P_GS, columns=['Ploss (pu)'])
    Perdidas_Q_GS = pd.DataFrame (Perdidas_Q_GS, columns=['Qloss (pu)'])

    # =============================================== Escribimos los resultados del flujo de potencia ===================================================
    ID_Lineas.to_excel(writer, sheet_name='POWER FLOW GS', header= 'Ident.', index=False, startrow=0, startcol=0)
    Barra_i.to_excel(writer, sheet_name='POWER FLOW GS', header= 'Bus i', index=False, startrow=0, startcol=1)
    Barra_j.to_excel(writer, sheet_name='POWER FLOW GS', header= 'Bus j', index=False, startrow=0, startcol=2)
    P_ij_GS.to_excel(writer, sheet_name='POWER FLOW GS', header= 'P_ij', index=False, startrow=0, startcol=3)
    Q_ij_GS.to_excel(writer, sheet_name='POWER FLOW GS', header= 'Q_ij', index=False, startrow=0, startcol=4)
    P_ji_GS.to_excel(writer, sheet_name='POWER FLOW GS', header= 'P_ji', index=False, startrow=0, startcol=5)
    Q_ji_GS.to_excel(writer, sheet_name='POWER FLOW GS', header= 'Q_ji', index=False, startrow=0, startcol=6)
    Perdidas_P_GS.to_excel(writer, sheet_name='POWER FLOW GS', header= 'Ploss', index=False, startrow=0, startcol=7)
    Perdidas_Q_GS.to_excel(writer, sheet_name='POWER FLOW GS', header= 'Qloss', index=False, startrow=0, startcol=8)

    SF_GS.to_excel(writer, sheet_name='POWER FLOW GS', index=False)

    return

def NR (writer, ID_Barras, Fasores_NR, Angulos_NR, P_gen_NR, Q_gen_NR, P_demanda, Q_demanda, Iteracion_NR, Error_NR):
    
    # =============================================== Transformamos los datos para Gauss Saidel ===========================================================
    # Convertimos los resultados en un dataframe de pandas.
    Resultados_NR = pd.DataFrame (Fasores_NR)
    Resultados_NR = np.round (Resultados_NR, 4)
    angulos_grados_NR = pd.DataFrame (Angulos_NR)
    angulos_grados_NR = np.round (angulos_grados_NR, 4)
    P_generada = pd.DataFrame (P_gen_NR)
    Q_generada = pd.DataFrame (Q_gen_NR)
    P_i = [] # Lista para almacenar la potencia generada menos la demanda
    Q_i = [] # Lista para almacenar la potencia generada menos la demanda

    # Agregamos los valores a las listas.
    for i in range(len(P_generada)): 
        P_i.append (P_generada.values[i] - P_demanda.values[i])
        Q_i.append (Q_generada.values[i] - Q_demanda.values[i])

    # Aproximamos nuestros resultados.
    P_i = np.round (P_i, 4)
    Q_i = np.round (Q_i, 4)
    Q_demanda = np.round (Q_demanda,4)
    P_demanda = np.round (P_demanda, 4)

    # Convertimos las vairables a un dataframe de pandas.
    P_i = pd.DataFrame (P_i)
    Q_i = pd.DataFrame (Q_i)
    Q_demanda = pd.DataFrame (Q_demanda)
    P_demanda = pd.DataFrame (P_demanda)
    ID_Barras = pd.DataFrame (ID_Barras)
    
    # Enviamos a Exel los resultados.
    ID_Barras.to_excel(writer, sheet_name='RESULTS NR', header= ['Bus i'], index=False, startrow=1, startcol=0)
    Resultados_NR.to_excel(writer, sheet_name='RESULTS NR', header= ['|V| (pu)'], index=False, startrow=1, startcol=1)
    angulos_grados_NR.to_excel(writer, sheet_name='RESULTS NR', header= ['<V (degree)>'], index=False, startrow=1, startcol=2)
    P_generada.to_excel(writer, sheet_name='RESULTS NR', header= ['Pgen (pu)'], index=False, startrow=1, startcol=5)
    Q_generada.to_excel(writer, sheet_name='RESULTS NR', header= ['Qgen (pu)'], index=False, startrow=1, startcol=6)
    P_demanda.to_excel(writer, sheet_name='RESULTS NR', header= ['Pload (pu)'], index=False, startrow=1, startcol=7)
    Q_demanda.to_excel(writer, sheet_name='RESULTS NR', header= ['Qload (pu)'], index=False, startrow=1, startcol=8)
    P_i.to_excel(writer, sheet_name='RESULTS NR', header= ['Pi (pu)'], index=False, startrow=1, startcol=3)
    Q_i.to_excel(writer, sheet_name='RESULTS NR', header= ['Qi (pu)'], index=False, startrow=1, startcol=4)
    
    # Escribimos los datos en la hoja 'RESULTS GS' en posiciones especificas.
    worksheet = writer.sheets['RESULTS NR']
    worksheet.write(0, 0, 'Iteraciones')
    worksheet.write(0, 1, Iteracion_NR)
    worksheet.write(0, 2, 'Error')
    worksheet.write(0, 3, Error_NR)
    
    return 

def Sflow_NR (writer, Pij_NR, Qij_NR, Pji_NR, Qji_NR, P_loss_NR, Q_loss_NR, ID_lineas, Bus_i_lineas, Bus_j_lineas, SF_NR):
    
    # Extrayendo la parte real de cada elemento en la lista
    P_ij_NR = Pij_NR
    Q_ij_NR = Qij_NR
    P_ji_NR = Pji_NR
    Q_ji_NR = Qji_NR
    
    # =============================================== Transformamos los datos ===========================================================
    ID_Lineas = pd.DataFrame (ID_lineas, columns=['Ident.'])
    Barra_i = pd.DataFrame (Bus_i_lineas, columns=['Bus i'])
    Barra_j = pd.DataFrame (Bus_j_lineas, columns=['Bus j '])
    P_ij_NR = pd.DataFrame (P_ij_NR, columns=['P_ij (pu)'])
    Q_ij_NR = pd.DataFrame (Q_ij_NR, columns=['Q_ij (pu)'])
    P_ji_NR = pd.DataFrame (P_ji_NR, columns=['P_ji (pu)'])
    Q_ji_NR = pd.DataFrame (Q_ji_NR, columns=['Q_ji (pu)'])
    Perdidas_P_NR = pd.DataFrame (P_loss_NR, columns=['Ploss (pu)'])
    Perdidas_Q_NR = pd.DataFrame (Q_loss_NR, columns=['Qloss (pu)'])
    
    # =============================================== Escribimos los resultados del flujo de potencia ===================================================
    ID_Lineas.to_excel(writer, sheet_name='POWER FLOW NR', header= 'Ident.', index=False, startrow=0, startcol=0)
    Barra_i.to_excel(writer, sheet_name='POWER FLOW NR', header= 'Bus i', index=False, startrow=0, startcol=1)
    Barra_j.to_excel(writer, sheet_name='POWER FLOW NR', header= 'Bus j', index=False, startrow=0, startcol=2)
    P_ij_NR.to_excel(writer, sheet_name='POWER FLOW NR', header= 'P_ij', index=False, startrow=0, startcol=3)
    Q_ij_NR.to_excel(writer, sheet_name='POWER FLOW NR', header= 'Q_ij', index=False, startrow=0, startcol=4)
    P_ji_NR.to_excel(writer, sheet_name='POWER FLOW NR', header= 'P_ji', index=False, startrow=0, startcol=5)
    Q_ji_NR.to_excel(writer, sheet_name='POWER FLOW NR', header= 'Q_ji', index=False, startrow=0, startcol=6)
    Perdidas_P_NR.to_excel(writer, sheet_name='POWER FLOW NR', header= 'Ploss', index=False, startrow=0, startcol=7)
    Perdidas_Q_NR.to_excel(writer, sheet_name='POWER FLOW NR', header= 'Qloss', index=False, startrow=0, startcol=8)

    SF_NR.to_excel(writer, sheet_name='POWER FLOW NR', index=False)
    
    
    return

def Lineal (writer, DC, Angulos_Lineales, Bus_i_Barras):
    
    # Colocamos el fomrato correcto por si hacer falta.
    Angulos_Lineales = pd.DataFrame (Angulos_Lineales)
    Bus_i_Barras = pd.DataFrame (Bus_i_Barras)
    
    # ================================================ Escribimos los resultados del metodo lineal ====================================================
    Bus_i_Barras.to_excel(writer, sheet_name='RESULTS DC', header= ['Bus i'], index=False, startcol=0)
    Angulos_Lineales.to_excel(writer, sheet_name='RESULTS DC', header= ['<V (degree)'], index=False, startcol=1)
    
    return

def FD (writer, ID_Barras, Fasores_FD, Angulos_FD, P_gen_FD, Q_gen_FD, P_demanda, Q_demanda, Iteracion_FD, Error_FD):
    
    # =============================================== Transformamos los datos para Gauss Saidel ===========================================================
    # Convertimos los resultados en un dataframe de pandas.
    Resultados_FD = pd.DataFrame (Fasores_FD)
    Resultados_FD = np.round (Resultados_FD, 4)
    angulos_grados_FD = pd.DataFrame (Angulos_FD)
    angulos_grados_FD = np.round (angulos_grados_FD, 4)
    P_generada = pd.DataFrame (P_gen_FD)
    Q_generada = pd.DataFrame (Q_gen_FD)
    P_i = [] # Lista para almacenar la potencia generada menos la demanda
    Q_i = [] # Lista para almacenar la potencia generada menos la demanda
    
    # Agregamos los valores a las listas.
    for i in range(len(P_generada)): 
        P_i.append (P_generada.values[i] - P_demanda.values[i])
        Q_i.append (Q_generada.values[i] - Q_demanda.values[i])

    # Aproximamos nuestros resultados.
    P_i = np.round (P_i, 4)
    Q_i = np.round (Q_i, 4)
    Q_demanda = np.round (Q_demanda, 4)
    P_demanda = np.round (P_demanda,4)

    # Convertimos las vairables a un dataframe de pandas.
    P_i = pd.DataFrame (P_i)
    Q_i = pd.DataFrame (Q_i)
    Q_demanda = pd.DataFrame (Q_demanda)
    P_demanda = pd.DataFrame (P_demanda)
    ID_Barras = pd.DataFrame (ID_Barras)
    
    # Enviamos a Exel los resultados.
    ID_Barras.to_excel(writer, sheet_name='RESULTS FD', header= ['Bus i'], index=False, startrow=1, startcol=0)
    Resultados_FD.to_excel(writer, sheet_name='RESULTS FD', header= ['|V| (pu)'], index=False, startrow=1, startcol=1)
    angulos_grados_FD.to_excel(writer, sheet_name='RESULTS FD', header= ['<V (degree)>'], index=False, startrow=1, startcol=2)
    P_generada.to_excel(writer, sheet_name='RESULTS FD', header= ['Pgen (pu)'], index=False, startrow=1, startcol=5)
    Q_generada.to_excel(writer, sheet_name='RESULTS FD', header= ['Qgen (pu)'], index=False, startrow=1, startcol=6)
    P_demanda.to_excel(writer, sheet_name='RESULTS FD', header= ['Pload (pu)'], index=False, startrow=1, startcol=7)
    Q_demanda.to_excel(writer, sheet_name='RESULTS FD', header= ['Qload (pu)'], index=False, startrow=1, startcol=8)
    P_i.to_excel(writer, sheet_name='RESULTS FD', header= ['Pi (pu)'], index=False, startrow=1, startcol=3)
    Q_i.to_excel(writer, sheet_name='RESULTS FD', header= ['Qi (pu)'], index=False, startrow=1, startcol=4)
    
    # Escribimos los datos en la hoja 'RESULTS GS' en posiciones especificas.
    worksheet = writer.sheets['RESULTS FD']
    worksheet.write(0, 0, 'Iteraciones')
    worksheet.write(0, 1, Iteracion_FD)
    worksheet.write(0, 2, 'Error')
    worksheet.write(0, 3, Error_FD)
    
    return 

def Sflow_FD (writer, Pij_FD, Qij_FD, Pji_FD, Qji_FD, P_loss_FD, Q_loss_FD, ID_lineas, Bus_i_lineas, Bus_j_lineas, SF_FD):
    
    # Extrayendo la parte real de cada elemento en la lista
    P_ij_FD = Pij_FD
    Q_ij_FD = Qij_FD
    P_ji_FD = Pji_FD
    Q_ji_FD = Qji_FD
    
    # =============================================== Transformamos los datos ===========================================================
    ID_Lineas = pd.DataFrame (ID_lineas, columns=['Ident.'])
    Barra_i = pd.DataFrame (Bus_i_lineas, columns=['Bus i'])
    Barra_j = pd.DataFrame (Bus_j_lineas, columns=['Bus j '])
    P_ij_FD = pd.DataFrame (P_ij_FD, columns=['P_ij (pu)'])
    Q_ij_FD = pd.DataFrame (Q_ij_FD, columns=['Q_ij (pu)'])
    P_ji_FD = pd.DataFrame (P_ji_FD, columns=['P_ji (pu)'])
    Q_ji_FD = pd.DataFrame (Q_ji_FD, columns=['Q_ji (pu)'])
    Perdidas_P_FD = pd.DataFrame (P_loss_FD, columns=['Ploss (pu)'])
    Perdidas_Q_FD = pd.DataFrame (Q_loss_FD, columns=['Qloss (pu)'])
    
    # =============================================== Escribimos los resultados del flujo de potencia ===================================================
    ID_Lineas.to_excel(writer, sheet_name='POWER FLOW FD', header= 'Ident.', index=False, startrow=0, startcol=0)
    Barra_i.to_excel(writer, sheet_name='POWER FLOW FD', header= 'Bus i', index=False, startrow=0, startcol=1)
    Barra_j.to_excel(writer, sheet_name='POWER FLOW FD', header= 'Bus j', index=False, startrow=0, startcol=2)
    P_ij_FD.to_excel(writer, sheet_name='POWER FLOW FD', header= 'P_ij', index=False, startrow=0, startcol=3)
    Q_ij_FD.to_excel(writer, sheet_name='POWER FLOW FD', header= 'Q_ij', index=False, startrow=0, startcol=4)
    P_ji_FD.to_excel(writer, sheet_name='POWER FLOW FD', header= 'P_ji', index=False, startrow=0, startcol=5)
    Q_ji_FD.to_excel(writer, sheet_name='POWER FLOW FD', header= 'Q_ji', index=False, startrow=0, startcol=6)
    Perdidas_P_FD.to_excel(writer, sheet_name='POWER FLOW FD', header= 'Ploss', index=False, startrow=0, startcol=7)
    Perdidas_Q_FD.to_excel(writer, sheet_name='POWER FLOW FD', header= 'Qloss', index=False, startrow=0, startcol=8)

    SF_FD.to_excel(writer, sheet_name='POWER FLOW FD', index=False)
    
    
    return