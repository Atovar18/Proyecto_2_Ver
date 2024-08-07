import numpy as np
import time
from Modulos import Carga_Zip

def Gauss_Seidel (Y_Bus, Bus_type, P_gen, Q_gen, P_demanda, Q_demanda, V_pu, V_ang, Convergencia, Max_iter, Z_zip, I_zip, P_zip):
    Inicio = time.time()
    # Creamos copias de los datos para no afectar las variables.
    P_gen2 = P_gen.copy()
    Q_gen2 = Q_gen.copy()
    P_demanda2 = P_demanda.copy()
    Q_demanda2 = Q_demanda.copy()

    # Calculamos la potencia especifica de cada barra.
    P_especifica = P_gen2 - P_demanda2
    Q_espeficia = Q_gen2 - Q_demanda2

    # Creamos el fasor de voltaje con angulo 0 inicial. 
    Fasor_V = V_pu * np.exp(1j * np.radians(V_ang))

    # Creamos los elementos necesarios para llevar un mejor control.
    Indice = 0
    V_salida = Fasor_V.copy()

    for _ in range (Max_iter):
        Indice += 1
        # Calculamos los valores de las tensiones.
        
        for i in range (len(Y_Bus)):
            
            if Bus_type[i] == 'SL':
                V_salida [i] = V_salida[i]
            
            
            elif Bus_type[i] == 'PQ':
                
                # Establecemos los valores iniciales. 
                Sum1 = 0; termino1 = 0 
            
                for j in range (len(Y_Bus)):
                    
                    # Calculamos los elementos de la suma.
                    if j != i:
                        Sum1 += Y_Bus[i][j] * V_salida[j]
                
                # Calculamos el termino constante.
                termino1 = np.conjugate((P_especifica [i] + 1j * Q_espeficia [i]) / V_salida[i])
                
                # Calculamos el valor de la tensión.
                V_salida [i] = (termino1 - Sum1) / Y_Bus[i][i]               

            elif Bus_type[i] == 'PV':
                
                # Establecemos los valores iniciales.
                Sum2 = 0; termino2 = 0; q2 = 0
                Dato = abs(V_salida[i])
                
                for p in range (len(Y_Bus)):
                    
                    # Calculamos los elementos de la suma.
                    if p != i:
                        Sum2 += Y_Bus[i][p] * V_salida[p]
                        q2 += Y_Bus[i][p] * V_salida[p]
                        
                    else: 
                        q2 += Y_Bus[i][p] * V_salida[p]
                        
                # Sustituimos el valor de Q_especifica.
                Q_espeficia [i] = - np.imag(q2 * (np.conjugate(V_salida[i])))
                
                # Calculamos el termino constante.
                termino2 = np.conjugate((P_especifica [i] + 1j * Q_espeficia [i]) / V_salida[i])
                
                # Calculamos el valor de la tensión.
                V_salida [i] = (termino2 - Sum2) / Y_Bus[i][i]
                
                # Sustituimos el valor de la tensión.
                V_salida [i] = V_salida[i]/abs(V_salida[i]) * Dato
                
        # Calculamos el error.
        Error = max(abs(V_salida - Fasor_V))
            
        if Error < Convergencia:
            break  
        
        else:
            Fasor_V = V_salida.copy()
            Modulos = abs (V_salida)
            P_especifica, Q_espeficia = Carga_Zip.Cargas_Variables(P_demanda, Q_demanda, P_gen2, Q_gen2, Modulos, Z_zip, I_zip, P_zip)

        
        if Indice == Max_iter:
            break
        
    # Definimos la listas para almacenar los valores de los modulos y los angulos.
    Modulos_GS = []
    Angulos_GS = []    
    for i in V_salida:
        modulo = abs(i)
        modulo = round(modulo, 4)
        angulo = np.angle(i, deg = True)
        angulo = round(angulo, 4)
        Modulos_GS.append(modulo)
        Angulos_GS.append(angulo)

    Fasores_GS = V_salida

    Final = time.time()
    tiempo_transcurrido = Final - Inicio
    print (f"El tiempo de ejecucion en GS fue de {tiempo_transcurrido:.3f} segundos.")
    print ()
    
    return Modulos_GS, Angulos_GS, Fasores_GS, Indice, Error