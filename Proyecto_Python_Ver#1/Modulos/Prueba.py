import numpy as np
import math as mt
from Modulos import Calculos_PQ



# =================================================================================================================================================================

""" Intento fallido de implementar el método de Newton Raphson. """
def Fallido (V_pu, V_ang, P_gen, Q_gen, P_demanda, Q_demanda, Y_Bus, Bus_type, Convergencia, Max_iter):
    # Inicializa las listas para almacenar los módulos y ángulos
    Y_modulos = []
    Y_angulos = []
    Angulo_grados = V_ang
    Modulo = V_pu.copy()
    Dan = 0 

    #Recorre la matriz Y_bus de forma lineal, gracias al .flat, y crea un vector fila con todas las operaciones.
    for z in Y_Bus.flat:
        modulo = abs(z)
        angulo = np.angle(z)  # Calcula el ángulo en radianes
        Y_modulos.append(modulo)
        Y_angulos.append(angulo)

    # Convierte las listas en matrices con la misma disposición matricial de la Y_Bus.
    Y_modulos_matriz = np.array(Y_modulos).reshape(Y_Bus.shape)
    Y_angulos_matriz = np.array(Y_angulos).reshape(Y_Bus.shape)

    # Transformamos el angulo de los fasores en grad a rad.
    angulo_radianes = np.deg2rad(Angulo_grados)

    # Calculamos las potencias especificadas.    
    P_especificada = P_gen - P_demanda
    Q_especificada = Q_gen - Q_demanda 

    # Definimos las listas de constantes.
    Angulos_v = []
    Voltajes_v = []

    # Bucle para crear la matriz de datos.
    for i in range (len(Bus_type)):

        if Bus_type [i] == 'SL':
            continue
        
        if Bus_type [i] == 'PV':
            Angulos_v.append (angulo_radianes[i])
            
        if Bus_type [i] == 'PQ':
            Angulos_v.append (angulo_radianes[i])
            Voltajes_v.append (Modulo[i])

    # Convertimos los datos en una sola matriz columna.
    Angulo_v = Angulos_v.copy()
    Voltaje_v = Voltajes_v.copy()
    Angulos_v += Voltajes_v
    Datos = np.matrix (Angulos_v)
    Datos = np.transpose(Datos)
    indice = 0

    # Calculamos las potencias activas y reactivas y la matriz asociada.
    P_activa, Q_reactiva, Matriz_Potencias = Calculos_PQ.Potencias_NR (Bus_type, Modulo, Y_modulos_matriz, Y_angulos_matriz, angulo_radianes, P_especificada, Q_especificada)
        
        # Calculamos la matriz jacobiana.   
    Jacobiana = Calculos_PQ.Jacobiana_Potencias (Bus_type, Modulo, Y_modulos_matriz, Y_angulos_matriz, angulo_radianes)
    

    # ========================================================================== Bucle para el método. ========================================================================================================================================================================================================

    for _ in range (Max_iter):
        indice += 1      
        
        # Calculamos la inversa de la jacobiana.
        Inversa = np.linalg.inv(Jacobiana)
        
        # Calculamos las incognitas. 
        Resultado = Datos - Inversa @ Matriz_Potencias
        
        # Calculamos los errores.
        Error = max(abs(Resultado - Datos)) 
        
        # Establecemos las condiciones de ruptura.
        if Error < Convergencia:
            break
        
        else:
            print ('====================================================================================================')
            print ('Iteración:', indice)
            print (Resultado)
            Datos = Resultado.copy()
            Angulos_nuevos = Resultado [:len(Angulo_v)]
            Voltajes_nuevos = Resultado[len(Angulo_v):len(Angulo_v) + len(Voltaje_v)]
            
            # Selección de los indices a sustituir.
            indices_a_eliminar_PV = [i for i, tipo in enumerate(Bus_type) if tipo == "PV"]
            indices_a_eliminar_PQ = [i for i, tipo in enumerate(Bus_type) if tipo == "PQ"]
            indices_a_eliminar = indices_a_eliminar_PV + indices_a_eliminar_PQ
                
            # Sustitución de los valores.
            for i, indices in enumerate(indices_a_eliminar):
                angulo_radianes [indices] = Angulos_nuevos[i]
            
            for i, indices in enumerate(indices_a_eliminar_PQ):
                Modulo [indices] = Voltajes_nuevos[i]
            #print ()
            #print (Matriz_Potencias)
            #print ('====================================================================================================')
            #print (f'iteracion: {indice}')

            # Calculamos las potencias activas y reactivas y la matriz asociada.
            P_activa, Q_reactiva, Matriz_Potencias = Calculos_PQ.Potencias_NR (Bus_type, Modulo, Y_modulos_matriz, Y_angulos_matriz, angulo_radianes, P_especificada, Q_especificada)

            # Calculamos la matriz jacobiana.   
            #Jacobiana = Calculos_PQ.Jacobiana_Potencias (Bus_type, Modulo, Y_modulos_matriz, Y_angulos_matriz, angulo_radianes)
            #Jacobiana = np.transpose(Jacobiana)
            
        if indice == 2:
            break
            
            
                
        
        if _ == Max_iter-1:
            print ('El método no ha convergido alcanzó la iteración', indice)
            break
        
    return Modulo, angulo_radianes, P_activa, Q_reactiva, indice, Error, Matriz_Potencias

