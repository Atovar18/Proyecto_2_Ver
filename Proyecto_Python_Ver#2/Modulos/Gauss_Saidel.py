from Modulos import Carga_Zip
import time
import numpy as np

def Gauss_Seidel(P_gen, Q_gen, P_demanda, Q_demanda, Angulos_grados, Modulo_V, Y_Bus, Bus_type, Convergencia, Max_iter, Z_zip, I_zip, P_zip):
    # Inicializamos el tiempo de ejecucion.
    Inicio = time.time()

    # --------------------------------------------------- Creamos copias de las variables a trabajar ---------------------------------------------------------------------------------------------
    P_gen_GS = P_gen.copy()
    Q_gen_GS = Q_gen.copy()
    P_demanda_GS = P_demanda.copy()
    Q_demanda_GS = Q_demanda.copy()
    Angulos_grados_GS = Angulos_grados.copy()
    Modulo_V_GS = Modulo_V.copy()
    Convergencia_GS = Convergencia

    # Calculamos la potencia especifica de cada barra.
    P_especifica_GS = P_gen_GS - P_demanda_GS
    Q_especifica_GS = Q_gen_GS - Q_demanda_GS

    # Creamos el fasor de voltaje con angulo 0 inicial.
    Fasor_V = Modulo_V_GS * np.exp(1j * np.radians(Angulos_grados_GS))

    # Creamos los elementos necesarios para llevar un mejor control.
    Indice = 0
    V_salida = Fasor_V.copy()

    for _ in range(Max_iter):
        
        # Contador de iteraciones.
        Indice += 1
        
        # Calculamos los valores de las tensiones.
        for i in range(len(Y_Bus)):
            
            if Bus_type[i] == 'SL':
                
                # Sustituimos el valor de la tensión de la barra SL.
                V_salida[i] = Fasor_V[i]
            
            if Bus_type[i] == 'PQ':
                
                # Separamos la cuenta en dos partes.
                Sum1 = 0; termino1 = 0

                for j in range(len(Y_Bus)):
                    
                    # Calculamos los elementos de la suma.
                    if j != i:
                        Sum1 += Y_Bus[i][j] * V_salida[j]

                # Calculamos el termino constante.
                termino1 = np.conjugate((P_especifica_GS[i] + 1j * Q_especifica_GS[i]) / V_salida[i])

                # Calculamos el valor de la tensión.
                V_salida[i] = (termino1 - Sum1) / Y_Bus[i][i]

            if Bus_type[i] == 'PV':

                # Establecemos los valores iniciales.
                Sum2 = 0; termino2 = 0; q2 = 0
                Dato = abs(V_salida[i])

                for j in range(len(Y_Bus)):

                    # Sumamos sobre los valores fuera de la diagonal.
                    if j != i:
                        Sum2 += Y_Bus[i][j] * V_salida[j]
                        q2 += Y_Bus[i][j] * V_salida[j]
                        
                    # Sumamos el valor dentro de la diagonal.
                    else:
                        q2 += Y_Bus[i][i] * V_salida[i]
                
                # Sustituimos el valor de la Q de la barra PV.
                Q_especifica_GS[i] = -1 * np.imag(q2 * np.conjugate(V_salida[i]))

                # Calculamos el termino constante.
                termino2 = np.conjugate((P_especifica_GS[i] + 1j * Q_especifica_GS[i]) / V_salida[i])

                # Calculamos el valor de la tensión.
                V_salida[i] = (termino2 - Sum2) / Y_Bus[i][i]
                
                # Obtenemos la magnitud y el ángulo de la tensión.
                V_salida[i] = (V_salida[i]/ abs(V_salida[i]))*Dato
                
        # Calculamos el error de convergencia.
        Error_GS = max(abs(V_salida - Fasor_V))
        
        if Error_GS < Convergencia_GS:
            # Si el error es menor que la convergencia, salimos del bucle.
            break
        
        else:
            # Actualizamos el fasor de voltaje.
            Fasor_V = V_salida.copy()
            Modulo_V_GS = abs(Fasor_V)
            P_especifica_GS, Q_especifica_GS, P_demanda2_GS, Q_demanda2_GS = Carga_Zip.Cargas_Variables(P_demanda_GS, Q_demanda_GS, P_gen_GS, Q_gen_GS, Modulo_V_GS, Z_zip, I_zip, P_zip, Bus_type)
                
        # Actualizamos los valores de las potencias.
        P_return = P_demanda2_GS
        Q_return = Q_demanda2_GS

        # Condición de ruptura.
        if Indice == Max_iter:
            print("El sistema no converge en GS.")
            break
        
    # =========================================================================== Fin del calculo del sistema ============================================================================================================
    # ************************************************************************************************************************************************************************************************************************
    # ************************************************************************************************************************************************************************************************************************
    # =========================================================================== Definimos variables de salida ==========================================================================================
    # Definimos la listas para almacenar los valores de los modulos y los angulos.
    Modulos_GS = []
    Angulos_GS = []    

    # Bucle para sustituir los valores de los fasores.
    for i in V_salida:
        modulo = abs(i)
        modulo = round(modulo, 4)
        angulo = np.angle(i, deg = True)
        angulo = round(angulo, 4)
        Modulos_GS.append(modulo)
        Angulos_GS.append(angulo)
        
    # Almacenamos los valores de los fasores.
    Fasores_GS = V_salida

    # Finalizamos el tiempo de ejecución.
    Final = time.time()
    tiempo_transcurrido = Final - Inicio
    print (f"El tiempo de ejecucion en GS fue de {tiempo_transcurrido:.3f} segundos.")
    print ()
    return Modulos_GS, Angulos_GS, Fasores_GS, Indice, Error_GS, P_return, Q_return