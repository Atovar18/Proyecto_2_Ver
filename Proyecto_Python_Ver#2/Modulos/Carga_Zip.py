def Cargas_Variables(P_demanda, Q_demanda, P_gen, Q_gen, Modulo_V, Z_zip, I_zip, P_zip, Bus_type):
    # --------------------------------------------------- Creamos copias de las variables a trabajar ---------------------------------------------------------------------------------------------
    P_load = P_demanda.copy()
    Modulo_Vol = Modulo_V.copy()
    Tipo_Barra = Bus_type.copy()

    # Bucle para calcular las cargas del modelo Zip.
    for i, k in enumerate(P_load):
        if Tipo_Barra[i] == 'SL':
            # Si la barra es de tipo SL, no se hace nada.
            continue
        
        elif Tipo_Barra[i] == 'PV':
            # Si la barra es de tipo PV, no se hace nada.
            continue
        
        elif Tipo_Barra[i] == 'PQ':
            # Calculamos la potencia activa del modelo Zip.
            P = P_demanda[i] * (Z_zip[i] * (Modulo_Vol[i] ** 2) + I_zip[i] * Modulo_Vol[i] + P_zip[i])
            
            # Calculamos la potencia reactiva del modelo Zip.
            Q = Q_demanda[i] * (Z_zip[i] * (Modulo_Vol[i] ** 2) + I_zip[i] * Modulo_Vol[i] + P_zip[i])
            
            # Si P o Q son 0, no se hace nada, pero si son diferentes de 0, realizamos las correspondiente sustitución.
            if P == 0:
                P_demanda[i] = P_demanda[i]
            
            else:
                P_demanda[i] = P
                
            if Q == 0:
                Q_demanda[i] = Q_demanda[i]
            
            else:
                Q_demanda[i] = Q
            
    # Ahora podemos retornar las nuevas Potencias especificas y las nuevas demandas del sistema.
    P_especifica = P_gen - P_demanda
    Q_especifica = Q_gen - Q_demanda
    
    return P_especifica, Q_especifica, P_demanda, Q_demanda