import pandas as pd
import numpy as np

def Potencia_Barras(Modulo, Fasor, Y_Bus, Bus_type, P_gen, Q_gen, P_demanda, Q_demanda):
    y_bus = np.copy(Y_Bus)  # Copiamos la matriz de admitancias para evitar modificar la original.
    Modulos = np.copy(Modulo)  # Copiamos los modulos de voltaje.
    Fasores = np.copy(Fasor)  # Copiamos los fasores de voltaje.
    Tipo_Barra = np.copy(Bus_type)  # Copiamos el tipo de barra.
    Potencias_S = np.zeros(len(Tipo_Barra), dtype=complex)  # Inicializamos el vector de potencias.

    # Juntamos las nuevas potencias.
    Potencias_S = Potencias_S + (P_gen + 1j*Q_gen)


    for i in range(len(Tipo_Barra)):
        
        # Barra Slack.
        if Tipo_Barra[i] == 'SL':
            
            # Definimos los terminos.
            termi1 = 0; termi2 = 0
            
            # Suma 1.
            termi1 = ((Modulos[i])**2)*(np.conjugate(y_bus[i,i]))

            # Suma 2 (Elementos <i,j>).
            for j in range(len(Tipo_Barra)):
                if j != i:
                    termi2 += (np.conjugate(y_bus[i,j] * Fasores[j])* Fasores[i]) 
            
            # Potencia compleja.
            Potencias_S[i] = termi1 + termi2
            
        # Barra PQ.
        elif Tipo_Barra[i] == 'PQ':
            
            continue
        
        # Barra PV.
        elif Tipo_Barra[i] == 'PV':
            
            # Definimos los terminos.
            termi3 = 0; termi4 = 0
            
            # Suma 1.
            termi3 = ((Modulos[i])**2)*(np.conjugate(y_bus[i,i]))

            # Suma 2 (Elementos <i,j>).
            for j in range(len(Tipo_Barra)):
                if j != i:
                    termi4 += (np.conjugate(y_bus[i,j] * Fasores[j])* Fasores[i]) 
            
            # Potencia compleja.
            previo = termi3 + termi4
            
            Potencias_S[i] = (0 + np.imag (previo) * 1j) + Potencias_S[i]
            
    P_gen = np.real(Potencias_S)  # Actualizamos la potencia activa generada.
    Q_gen = np.imag(Potencias_S)  # Actualizamos la potencia reactiva generada.
    Pi = P_gen - P_demanda  # Potencia activa de inyección.
    Qi = Q_gen - Q_demanda  # Potencia reactiva de inyección.
    
    return P_gen, Q_gen, Pi, Qi