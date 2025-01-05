import numpy as np

def Potencia_entregada (Bus_type, Fasores_GS, Y_Bus): 
    
    # Creamos una lista de 0's compleja para guardar los resultados.
    Potencia_S = np.zeros(len(Bus_type), complex)
    for i in range (len(Bus_type)):
        
        if Bus_type [i] == 'SL':
            
            # Definimos los terminos.
            termi1 = 0; termi2 = 0
            
            # Suma 1.
            termi1 = (abs(Fasores_GS[i])**2)*(np.conjugate(Y_Bus[i,i]))
            
            for h in range (len(Bus_type)):
                if h != i:
                    # Suma 2.
                    termi2 += (np.conjugate(Fasores_GS[h]* Y_Bus[i,h]))
            
            casa = termi2*Fasores_GS[i] 
            
            # Guardamos resultados.
            Potencia_S [i] = termi1 + casa 
            
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
            Imag = (np.imag(Total))*1j
            Potencia_S [i] = Imag

    # Aproximamos resultados para mejor interpretación. 
    Potencia_S = np.round (Potencia_S, 4)

    # Separamos resultados para mejor interpretación.
    P_gen = np.real(Potencia_S)
    Q_gen = np.imag (Potencia_S)

    return P_gen, Q_gen