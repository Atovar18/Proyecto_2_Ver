import pandas as pd
import numpy as np

def Datos (writer, Lineas, Bus, TRX, SHUNT_ELEMENTS):
    
    # Eliminamos los datos que estan apagados, para simplificar la cuentas.
    Lineas = Lineas[Lineas.iloc[:, 0] != 'OFF']
    Bus = Bus[Bus.iloc[:, 0] != 'OFF']
    TRX = TRX[TRX.iloc[:, 0] != 'OFF']
    SHUNT_ELEMENTS = SHUNT_ELEMENTS[SHUNT_ELEMENTS.iloc[:, 0] != 'OFF']
    
    # Exportamos los datos al archivo Excel.
    Bus.to_excel(writer, sheet_name='BUS', index=False)
    Lineas.to_excel(writer, sheet_name='LINES', index=False)
    TRX.to_excel(writer, sheet_name='TRX', index=False)
    SHUNT_ELEMENTS.to_excel(writer, sheet_name='SHUNT ELEMENTS', index=False)
    
    return

def Salida_GS(writer, Modulos_GS, Angulos_GS, P_gen_GS, Q_gen_GS, P_demanda_GS, Q_demanda_GS, Error_GS, Iteraciones_GS, ID_Barras, Pi_GS, Qi_GS):
    
    # Aproximamos.
    Modulos_GS = np.round(Modulos_GS, 4)  # Redondeamos los modulos de voltaje.
    Angulos_GS = np.round(Angulos_GS, 4)  # Redondeamos los angulos de voltaje.
    P_gen_GS = np.round(P_gen_GS, 4)  # Redondeamos la potencia activa generada.
    Q_gen_GS = np.round(Q_gen_GS, 4)  # Redondeamos la potencia reactiva generada.
    Pi_GS = np.round(Pi_GS, 4)  # Redondeamos la potencia activa de inyección.
    Qi_GS = np.round(Qi_GS, 4)  # Redondeamos la potencia reactiva de inyección.

    # Convertimos las variables a series de pandas.
    Modulos_GS_S = pd.Series (Modulos_GS)
    Angulos_GS_S = pd.Series (Angulos_GS)
    P_gen_GS_S = pd.Series (P_gen_GS)
    Q_gen_GS_S = pd.Series (Q_gen_GS)
    Pi_GS_S = pd.Series (Pi_GS)
    Qi_GS_S = pd.Series (Qi_GS)
    P_demanda_GS_S = pd.Series(P_demanda_GS)
    Q_demanda_GS_S = pd.Series(Q_demanda_GS)

    # Escribimos los datos en la hoja 'RESULTS GS' en posiciones especificas.
    worksheet = writer.sheets['RESULTS GS']
    worksheet.write(0, 0, 'Iteraciones')
    worksheet.write(0, 1, Iteraciones_GS)
    worksheet.write(0, 2, 'Error')
    worksheet.write(0, 3, Error_GS)

    # Escribimos las listas
    ID_Barras.to_excel(writer, sheet_name='RESULTS GS', header= ['Bus i'], index=False, startrow=1, startcol=0)
    Modulos_GS_S.to_excel(writer, sheet_name='RESULTS GS', header= ['Modulo V'], index=False, startrow=1, startcol=1)
    Angulos_GS_S.to_excel(writer, sheet_name='RESULTS GS', header= ['Angulo V'], index=False, startrow=1, startcol=2)
    Pi_GS_S.to_excel(writer, sheet_name='RESULTS GS', header= ['P_i (pu)'], index=False, startrow=1, startcol=3)
    Qi_GS_S.to_excel(writer, sheet_name='RESULTS GS', header= ['Q_i (pu)'], index=False, startrow=1, startcol=4)
    P_gen_GS_S.to_excel(writer, sheet_name='RESULTS GS', header= ['P_gen(pu)'], index=False, startrow=1, startcol=5)
    Q_gen_GS_S.to_excel(writer, sheet_name='RESULTS GS', header= ['Q_gen(pu)'], index=False, startrow=1, startcol=6)
    P_demanda_GS_S.to_excel(writer, sheet_name='RESULTS GS', header= ['P_demanda(pu)'], index=False, startrow=1, startcol=7)
    Q_demanda_GS_S.to_excel(writer, sheet_name='RESULTS GS', header= ['Q_demanda(pu)'], index=False, startrow=1, startcol=8)
    
    return

def Sflow_GS(writer, P_perdidas_GS, Q_perdidas_GS, P_ij_GS, P_ji_GS, Salidas_GS, Llegadas_GS, ID_GS, Q_ij_GS, Q_ji_GS):
    # Aproximamos.
    P_perdidas_GS = np.round(P_perdidas_GS, 4)  # Redondeamos la potencia activa perdida.
    Q_perdidas_GS = np.round(Q_perdidas_GS, 4)  # Redondeamos la potencia reactiva perdida.
    P_ij_GS = np.round(P_ij_GS, 4)  # Redondeamos la potencia activa de inyección.
    P_ji_GS = np.round(P_ji_GS, 4)  # Redondeamos la potencia activa de inyección.
    Q_ij_GS = np.round(Q_ij_GS, 4)  # Redondeamos la potencia reactiva de inyección.
    Q_ji_GS = np.round(Q_ji_GS, 4)  # Redondeamos la potencia reactiva de inyección.

    # Convertimos las variables a series de pandas.
    ID_GS = pd.Series(ID_GS)
    Salidas_GS_S = pd.Series(Salidas_GS)
    Llegadas_GS_S = pd.Series(Llegadas_GS)
    P_perdidas_GS_S = pd.Series(P_perdidas_GS)
    Q_perdidas_GS_S = pd.Series(Q_perdidas_GS)
    P_ij_GS_S = pd.Series(P_ij_GS)
    P_ji_GS_S = pd.Series(P_ji_GS)
    Q_ij_GS_S = pd.Series(Q_ij_GS)
    Q_ji_GS_S = pd.Series(Q_ji_GS)


    ID_GS.to_excel(writer, sheet_name='POWER FLOW GS', header= ['Ident.'], index=False, startrow=0, startcol=0)
    Salidas_GS_S.to_excel(writer, sheet_name='POWER FLOW GS', header= ['Bus i'], index=False, startrow=0, startcol=1)
    Llegadas_GS_S.to_excel(writer, sheet_name='POWER FLOW GS', header= ['Bus j'], index=False, startrow=0, startcol=2)
    P_ij_GS_S.to_excel(writer, sheet_name='POWER FLOW GS', header= ['P_ij (pu)'], index=False, startrow=0, startcol=3)
    Q_ij_GS_S.to_excel(writer, sheet_name='POWER FLOW GS', header= ['Q_ij (pu)'], index=False, startrow=0, startcol=4)
    P_ji_GS_S.to_excel(writer, sheet_name='POWER FLOW GS', header= ['P_ji (pu)'], index=False, startrow=0, startcol=5)
    Q_ji_GS_S.to_excel(writer, sheet_name='POWER FLOW GS', header= ['Q_ji (pu)'], index=False, startrow=0, startcol=6)
    P_perdidas_GS_S.to_excel(writer, sheet_name='POWER FLOW GS', header= ['P_perdidas (pu)'], index=False, startrow=0, startcol=7)
    Q_perdidas_GS_S.to_excel(writer, sheet_name='POWER FLOW GS', header= ['Q_perdidas (pu)'], index=False, startrow=0, startcol=8)
    
    return