import numpy as np

def Potencia_entregada (Bus_type, Fasores_GS, Y_Bus, P_gen, Q_gen, P_load, Q_load): 
    
    # Creamos una lista de 0's compleja para guardar los resultados.
    Potencia_S = np.zeros(len(Bus_type), complex)
    for i in range (len(Bus_type)):
        
        if Bus_type [i] == 'SL':
            
            # Definimos los terminos.
            termi1 = 0; termi2 = 0; casa = 0
            
            # Suma 1.
            termi1 = (abs(Fasores_GS[i])**2)*(np.conjugate(Y_Bus[i,i]))

            for h in range (len(Bus_type)):
                if h != i:
                    # Suma 2.
                    termi2 += (np.conjugate(Fasores_GS[h])*np.conjugate(Y_Bus[i,h]))
            
            casa = termi2*Fasores_GS[i] 
            
            # Agregamos el resultado.
            DeltaS = termi1 + casa

            # Calculamos la potencia generada.
            Potencia_S [i] = DeltaS + (P_load[i] + 1j*Q_load[i])
            
        elif Bus_type [i] == 'PV':
            
            # Definimos terminos.
            termi3 = 0; termi4 = 0
            
            # Primera suma.
            termi3 = (abs(Fasores_GS[i])**2)*(np.conjugate(Y_Bus[i,i]))
            
            # Segunda suma.
            for k in range (len(Bus_type)):
                if i != k: 
                    termi4 += (np.conjugate(Fasores_GS[k]*Y_Bus [i,k]))
            
            Total = termi3 + (termi4*Fasores_GS[i])
            # Guardamos reusltados.
            DeltaS = (P_gen[i] + 1j*Q_gen[i]) + (0 + 1j*np.imag(Total))

            Potencia_S [i] = DeltaS + (P_load[i] + 1j*Q_load[i])
        
        elif Bus_type [i] == 'PQ':
            # Definimos terminos.
            termi5 = 0; termi6 = 0
            
            # Primera suma.
            termi5 = (abs(Fasores_GS[i])**2)*(np.conjugate(Y_Bus[i,i]))
            
            # Segunda suma.
            for k in range (len(Bus_type)):
                if i != k: 
                    termi6 += (np.conjugate(Fasores_GS[k]*Y_Bus [i,k]))
            
            Total = termi5 + (termi6*Fasores_GS[i])
            
            # Guardamos resultados.
            DeltaS = Total

            Potencia_S [i] = DeltaS + (P_load[i] + 1j*Q_load[i])

    # Aproximamos resultados para mejor interpretación. 
    Potencia_S = np.round (Potencia_S, 4)

    # Separamos resultados para mejor interpretación.
    P_gen = np.real(Potencia_S)
    Q_gen = np.imag (Potencia_S)

    return P_gen, Q_gen