def Cargas_Variables (P_demanda, Q_demanda,P_gen, Q_gen, Modulos, Z_zip, I_zip, P_zip):
    P_load = P_demanda
    Modulo_V = Modulos

    for i , k in enumerate (P_load):
            
            # Calculamos la potencia activa del modelo Zip.
            P = P_demanda[i]*(Z_zip[i]*(Modulo_V[i]**2) + I_zip[i]*(Modulo_V [i])+ P_zip[i])
            
            # Calculamos la potencia reactiva del modelo Zip.
            Q = Q_demanda[i]*(Z_zip[i]*(Modulo_V[i]**2) + I_zip[i]*(Modulo_V [i])+ P_zip[i])
            
            # Si P o Q son 0, no se hace nada, pero si son diferentes de 0, realizamos las correspondiente sustitución.
            if P == 0: 
                P_demanda [i] = P_demanda[i]
            
            else:
                P_demanda [i] = P
                
            if Q == 0:
                Q_demanda [i] = Q_demanda[i]
            
            else:
                Q_demanda [i] = Q
                
            # Ahora podemos retornar los valores calculados y extraidos de los datos.
            
    P_especifica = P_gen - P_demanda
    Q_especifica = Q_gen - Q_demanda
    
    return P_especifica, Q_especifica, P_demanda, Q_demanda