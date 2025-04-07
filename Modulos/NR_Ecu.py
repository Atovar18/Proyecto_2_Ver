import numpy as np
import sympy as sp
from Modulos import Carga_Zip

# // ===============================================================================================================================================================================================================================================================================================

# Copiamos variables para no afectar los valores originales.
P_gen_c = P_gen.copy()
Q_gen_c = Q_gen.copy()
P_demanda_c = P_demanda.copy()
Q_demanda_c = Q_demanda.copy()

# Variables auxiliares para el método.
indice_borrar_SL = []
indice_borrar_PV = []
P_metodo = np.zeros ((len(Bus_type)))
Q_metodo = np.zeros ((len(Bus_type)))

# Transformamos las variables.
P_gen = np.array(P_gen_c)
Q_gen = np.array(Q_gen_c)
P_demanda = np.array(P_demanda_c)
Q_demanda = np.array(Q_demanda_c)
V_pu_c = np.array(V_pu)
V_ang_c = np.array(V_ang)

# Ybus angulos y modulos.
Ybus_modulos = abs(Y_Bus)
Ybus_angulos = np.angle(Y_Bus)

# Transformamos los voltajes a fasores.
Voltajes = np.zeros ((len(V_pu)),dtype=complex)
for i in range(len(V_pu)):
    Voltajes[i] = V_pu[i] * np.exp (1j * np.radians(V_ang[i]))
    
# Calculamos la potencia especifica de cada barra.
P_especifica = P_gen - P_demanda
Q_especifica = Q_gen - Q_demanda

# ===================================================================================== ▲P y ▲Q ===================================================================================
# Definimos las ecuaciones de ▲P y ▲Q.
for i in range(len(Bus_type)):
    if Bus_type[i] == "SL":
        indice_borrar_SL.append(i)
        
    elif Bus_type[i] == "PV":
        indice_borrar_PV.append(i)
        
        for j in range(len(Bus_type)):
            
            if i == j:
                # Diagonal.
                P_metodo[i] += V_pu[i]*Ybus_modulos[i,j]*V_pu[j]*np.cos(Ybus_angulos[i,j])
                
            else:
                # Fuera de diagonal.
                P_metodo[i] += V_pu[i]*Ybus_modulos[i,j]*V_pu[j]*np.cos(V_ang[i] - Ybus_angulos[i,j]- V_ang[j])
                
    elif Bus_type[i] == "PQ":
        
        for j in range(len(Bus_type)):
            
            if i == j:
                # Diagonal.
                P_metodo[i] += V_pu[i]*Ybus_modulos[i,j]*V_pu[j]*np.cos(Ybus_angulos[i,j])
                Q_metodo[i] += (V_pu[i]*Ybus_modulos[i,j]*V_pu[j]*np.sin(Ybus_angulos[i,j])*-1)
                
            else:
                # Fuera de diagonal.
                P_metodo[i] += V_pu[i]*Ybus_modulos[i,j]*V_pu[j]*np.cos(V_ang[i] - Ybus_angulos[i,j]- V_ang[j])
                Q_metodo[i] += (V_pu[i]*Ybus_modulos[i,j]*V_pu[j]*np.sin(V_ang[i] - Ybus_angulos[i,j]- V_ang[j]))
                
# Valores a no eliminar
no_borrar_SL = set([i for i, _ in enumerate(V_pu) if i not in indice_borrar_SL])
no_borrar_PV = set([i for i, _ in enumerate(V_pu) if i not in indice_borrar_PV])
         
# Calculamos el valro de ▲P y ▲Q.
Delta_P = P_especifica - P_metodo     
Delta_Q = Q_especifica - Q_metodo  

# Eliminamos los valores no necesarios. 
Delta_P = np.delete(Delta_P, indice_borrar_SL)
Delta_Q = np.delete(Delta_Q, indice_borrar_SL + indice_borrar_PV)
# Convertimos a P en un vector columna.
Delta_P = Delta_P.reshape(-1, 1)

# ================================================================================== Jacobiana de P - angulos. ===================================================================================
            
# Calculamos la submatriz jacobiana que depende de los angulos.
J_P_angulo = np.zeros ((len(Bus_type), len(Bus_type)))

# Bucle encargado de leer las posiciones de la matriz jacobiana.
for i in range(len(Bus_type)):
    for j in range(len(Bus_type)):
        
        # Condición para la diagonal.
        if i == j: 
            
            # Bucle encargado de calcular valores cuadraticos.
            for k in range(len(Bus_type)):
                if i == k:
                    continue
                else:
                    J_P_angulo[i,j] += V_pu[i]*Ybus_modulos[i,k]*V_pu[k]*np.sin(V_ang[i] - Ybus_angulos[i,k]- V_ang[k])
                    
        
        # Condición para la fuera de diagonal.
        elif i != j:
            J_P_angulo[i,j] = ((V_pu[i]*Ybus_modulos[i,j]*V_pu[j]*np.sin(V_ang[i] - Ybus_angulos[i,j]- V_ang[j]))*-1)
            
            
# Eliminamos las filas y columnas de la matriz jacobiana de la barra SL.
# Las filas.
matriz_sin_filas = np.delete(J_P_angulo, indice_borrar_SL, axis=0)

# Las Columnas.
J_P_angulo = np.delete(matriz_sin_filas, indice_borrar_SL, axis=1)
            

# =================================================================================== Jacobiana de P - Voltajes. ===================================================================================

# Calculamos la submatriz jacobiana que depende de los voltajes.
J_P_Voltaje = np.zeros ((len(Bus_type), len(Bus_type)))

# Bucle encargado de leer las posiciones de la matriz jacobiana.
for i in range(len(Bus_type)):
    for j in range(len(Bus_type)):
        
        # Condición para la diagonal.
        if i == j: 
            
            # Bucle encargado de calcular valores cuadraticos.
            for k in range(len(Bus_type)):
                if i == k:
                    J_P_Voltaje[i,j] += (-2*(V_pu[i]*Ybus_modulos[i,j]*np.cos(Ybus_angulos[i,k])))
                else:
                    J_P_Voltaje[i,j] += (-1*(V_pu[k]*Ybus_modulos[i,k]*np.cos(V_ang[i] - Ybus_angulos[i,k]- V_ang[k])))
                    
        
        # Condición para la fuera de diagonal.
        elif i != j:
            J_P_Voltaje[i,j] = ((V_pu[i]*Ybus_modulos[i,j]*np.cos(V_ang[i] - Ybus_angulos[i,j]- V_ang[j]))*-1)
            
            
# Eliminamos las filas y columnas de la matriz jacobiana de la barra SL y PV.
# Combinamos los índices a eliminar
indices_a_borrar = list(set(indice_borrar_SL + indice_borrar_PV))

# Las columnas.
J_P_Voltaje = np.delete(J_P_Voltaje, indices_a_borrar, axis=1)

# Las filas.
J_P_Voltaje = np.delete(J_P_Voltaje, indice_borrar_SL, axis=0)

# ==================================================================================== Jacobiana de P. ===================================================================================

# Agrega J_P_Voltaje al final de J_P_Angulo
J_P_Completa = np.hstack((J_P_angulo, J_P_Voltaje))

# ==================================================================================== Jacobiana de Q - angulos. ===================================================================================
# Calculamos la submatriz jacobiana que depende de los angulos.
J_Q_angulo = np.zeros ((len(Bus_type), len(Bus_type)))


# Bucle encargado de leer las posiciones de la matriz jacobiana.
for i in range(len(Bus_type)):
    for j in range(len(Bus_type)):
        
        # Condición para la diagonal.
        if i == j: 
            
            # Bucle encargado de calcular valores cuadraticos.
            for k in range(len(Bus_type)):
                if i == k:
                    continue
                else:
                    J_Q_angulo[i,j] += (V_pu[i]*Ybus_modulos[i,k]*V_pu[k]*np.cos(V_ang[i] - Ybus_angulos[i,k]- V_ang[k])*-1)
                    
        
        # Condición para la fuera de diagonal.
        elif i != j:
            J_Q_angulo[i,j] = ((V_pu[i]*Ybus_modulos[i,j]*V_pu[j]*np.cos(V_ang[i] - Ybus_angulos[i,j]- V_ang[j])))
            
# Eliminamos las filas y columnas de la matriz jacobiana de la barra SL.
# Las filas.
matriz_sin_filas = np.delete(J_Q_angulo, indices_a_borrar, axis=0)

# Las Columnas.
J_Q_angulo = np.delete(matriz_sin_filas, indice_borrar_SL, axis=1)


# =================================================================================== Jacobiana de Q - Voltajes. ===================================================================================

# Calculamos la submatriz jacobiana que depende de los voltajes.
J_Q_Voltaje = np.zeros ((len(Bus_type), len(Bus_type)))

# Bucle encargado de leer las posiciones de la matriz jacobiana.
for i in range(len(Bus_type)):
    for j in range(len(Bus_type)):
        
        # Condición para la diagonal.
        if i == j: 
            
            # Bucle encargado de calcular valores cuadraticos.
            for k in range(len(Bus_type)):
                if i == k:
                    J_Q_Voltaje[i,j] += (2*(V_pu[i]*Ybus_modulos[i,j]*np.sin(Ybus_angulos[i,k])))
                    
                else:
                    J_Q_Voltaje[i,j] += (-1*(V_pu[k]*Ybus_modulos[i,k]*np.sin(V_ang[i] - Ybus_angulos[i,k]- V_ang[k])))
                    
        
        # Condición para la fuera de diagonal.
        elif i != j:
            J_Q_Voltaje[i,j] = 1    # Ignorar, solo es un valor de referencia.
            
# Eliminamos las filas y columnas de la matriz jacobiana de la barra SL y PV.
# Las columnas.
J_Q_Voltaje = np.delete(J_Q_Voltaje, indices_a_borrar, axis=1)

# Las filas.
J_Q_Voltaje = np.delete(J_Q_Voltaje, indices_a_borrar, axis=0)

# ==================================================================================== Jacobiana de P. ===================================================================================

# Agrega J_Q_Voltaje al final de J_Q_Angulo
J_Q_Completa = np.hstack((J_Q_angulo, J_Q_Voltaje))


# ===================================================================================== Jacobiana. =======================================================================================
# Agrega J_Q_Completa como filas al final de J_P_Completa
Jacobiana_Completa = np.vstack((J_P_Completa, J_Q_Completa))

# ===========================================================================================================================================================================================================
# Armamos matrices para el método de Newton Raphson.

# Eliminamos la barra SL y PV de Voltajes.
Voltajes = np.delete(V_pu, indices_a_borrar)
# Eliminamos angulos de la barra SL.
Angulos_N = np.delete(V_ang, indice_borrar_SL)
Angulos_N = Angulos_N.reshape(-1, 1)

# Creamos la matriz incognita.
incognita = np.vstack((Angulos_N, Voltajes))

# Contador.
iteraciones = 0

# =================================================================================== Bucle iterativo. ===================================================================================


for h in range(Max_iter):
    
    print (Jacobiana_Completa)
    print ()

    
    # Expresión del Newton Raphson.
    Result = incognita - np.linalg.inv(Jacobiana_Completa) @ np.vstack((Delta_P, Delta_Q))

    # Calculamos el error asociado.
    Error = np.max(abs(Result - incognita))
    
    if Error < Convergencia:
        break
    
    if h == Max_iter - 1:
        print("No se ha alcanzado la convergencia.")
        break
    
    # Verificar si algún valor en la matriz alcanza 1e+170 
    if (Result >= 1e+170).any(): 
        print("Valor muy alto encontrado, rompiendo el bucle.") 
        break

    # Asegúrate de que V_pu y V_ang sean de tipo float
    V_pu = V_pu.astype(float)
    V_ang = V_ang.astype(float)

    # Cambio de valores de voltaje.
    k = 1 #iterador auxiliar
    for i in list(no_borrar_SL.intersection(no_borrar_PV)):
                V_pu[i] = Result[(len(Angulos_N)-1)+k]
                k += 1
                
    # Cambio de valores de ángulo.
    k=0  #iterador auxiliar
    for i in list(no_borrar_SL):
        V_ang[i] = Result[k]
        k += 1
        
    P_especifica, Q_especifica, P_carga, Q_carga = Carga_Zip.Cargas_Variables(P_demanda, Q_demanda, P_gen, Q_gen, V_pu, Z_zip, I_zip, P_zip)

    # ===================================================================================== ▲P y ▲Q ===================================================================================
    # Definimos las ecuaciones de ▲P y ▲Q.
    for i in range(len(Bus_type)):
        if Bus_type[i] == "SL":
            indice_borrar_SL.append(i)
            
        elif Bus_type[i] == "PV":
            indice_borrar_PV.append(i)
            
            for j in range(len(Bus_type)):
                
                if i == j:
                    # Diagonal.
                    P_metodo[i] += V_pu[i]*Ybus_modulos[i,j]*V_pu[j]*np.cos(Ybus_angulos[i,j])
                    
                else:
                    # Fuera de diagonal.
                    P_metodo[i] += V_pu[i]*Ybus_modulos[i,j]*V_pu[j]*np.cos(V_ang[i] - Ybus_angulos[i,j]- V_ang[j])
                    
        elif Bus_type[i] == "PQ":
            
            for j in range(len(Bus_type)):
                
                if i == j:
                    # Diagonal.
                    P_metodo[i] += V_pu[i]*Ybus_modulos[i,j]*V_pu[j]*np.cos(Ybus_angulos[i,j])
                    Q_metodo[i] += (V_pu[i]*Ybus_modulos[i,j]*V_pu[j]*np.sin(Ybus_angulos[i,j])*-1)
                    
                else:
                    # Fuera de diagonal.
                    P_metodo[i] += V_pu[i]*Ybus_modulos[i,j]*V_pu[j]*np.cos(V_ang[i] - Ybus_angulos[i,j]- V_ang[j])
                    Q_metodo[i] += (V_pu[i]*Ybus_modulos[i,j]*V_pu[j]*np.sin(V_ang[i] - Ybus_angulos[i,j]- V_ang[j]))
                    
    # Valores a no eliminar
    no_borrar_SL = set([i for i, _ in enumerate(V_pu) if i not in indice_borrar_SL])
    no_borrar_PV = set([i for i, _ in enumerate(V_pu) if i not in indice_borrar_PV])
            
    # Calculamos el valro de ▲P y ▲Q.
    Delta_P = P_especifica - P_metodo     
    Delta_Q = Q_especifica - Q_metodo 

    # Convertimos a P en un vector columna.
    Delta_P = Delta_P.reshape(-1, 1)
    
    # Eliminamos los valores no necesarios. 
    Delta_P = np.delete(Delta_P, indice_borrar_SL)
    Delta_Q = np.delete(Delta_Q, indice_borrar_SL + indice_borrar_PV)
    # Convertimos a P en un vector columna.
    Delta_P = Delta_P.reshape(-1, 1)

    # ================================================================================== Jacobiana de P - angulos. ===================================================================================
                
    # Calculamos la submatriz jacobiana que depende de los angulos.
    J_P_angulo = np.zeros ((len(Bus_type), len(Bus_type)))

    # Bucle encargado de leer las posiciones de la matriz jacobiana.
    for i in range(len(Bus_type)):
        for j in range(len(Bus_type)):
            
            # Condición para la diagonal.
            if i == j: 
                
                # Bucle encargado de calcular valores cuadraticos.
                for k in range(len(Bus_type)):
                    if i == k:
                        continue
                    else:
                        J_P_angulo[i,j] += V_pu[i]*Ybus_modulos[i,k]*V_pu[k]*np.sin(V_ang[i] - Ybus_angulos[i,k]- V_ang[k])
                        
            
            # Condición para la fuera de diagonal.
            elif i != j:
                J_P_angulo[i,j] = ((V_pu[i]*Ybus_modulos[i,j]*V_pu[j]*np.sin(V_ang[i] - Ybus_angulos[i,j]- V_ang[j]))*-1)
                
                
    # Eliminamos las filas y columnas de la matriz jacobiana de la barra SL.
    # Las filas.
    matriz_sin_filas = np.delete(J_P_angulo, indice_borrar_SL, axis=0)

    # Las Columnas.
    J_P_angulo = np.delete(matriz_sin_filas, indice_borrar_SL, axis=1)
                

    # =================================================================================== Jacobiana de P - Voltajes. ===================================================================================

    # Calculamos la submatriz jacobiana que depende de los voltajes.
    J_P_Voltaje = np.zeros ((len(Bus_type), len(Bus_type)))

    # Bucle encargado de leer las posiciones de la matriz jacobiana.
    for i in range(len(Bus_type)):
        for j in range(len(Bus_type)):
            
            # Condición para la diagonal.
            if i == j: 
                
                # Bucle encargado de calcular valores cuadraticos.
                for k in range(len(Bus_type)):
                    if i == k:
                        J_P_Voltaje[i,j] += (-2*(V_pu[i]*Ybus_modulos[i,j]*np.cos(Ybus_angulos[i,k])))
                    else:
                        J_P_Voltaje[i,j] += (-1*(V_pu[k]*Ybus_modulos[i,k]*np.cos(V_ang[i] - Ybus_angulos[i,k]- V_ang[k])))
                        
            
            # Condición para la fuera de diagonal.
            elif i != j:
                J_P_Voltaje[i,j] = ((V_pu[i]*Ybus_modulos[i,j]*np.cos(V_ang[i] - Ybus_angulos[i,j]- V_ang[j]))*-1)
                
                
    # Eliminamos las filas y columnas de la matriz jacobiana de la barra SL y PV.
    # Combinamos los índices a eliminar
    indices_a_borrar = list(set(indice_borrar_SL + indice_borrar_PV))

    # Las columnas.
    J_P_Voltaje = np.delete(J_P_Voltaje, indices_a_borrar, axis=1)

    # Las filas.
    J_P_Voltaje = np.delete(J_P_Voltaje, indice_borrar_SL, axis=0)

    # ==================================================================================== Jacobiana de P. ===================================================================================

    # Agrega J_P_Voltaje al final de J_P_Angulo
    J_P_Completa = np.hstack((J_P_angulo, J_P_Voltaje))

    # ==================================================================================== Jacobiana de Q - angulos. ===================================================================================
    # Calculamos la submatriz jacobiana que depende de los angulos.
    J_Q_angulo = np.zeros ((len(Bus_type), len(Bus_type)))


    # Bucle encargado de leer las posiciones de la matriz jacobiana.
    for i in range(len(Bus_type)):
        for j in range(len(Bus_type)):
            
            # Condición para la diagonal.
            if i == j: 
                
                # Bucle encargado de calcular valores cuadraticos.
                for k in range(len(Bus_type)):
                    if i == k:
                        continue
                    else:
                        J_Q_angulo[i,j] += (V_pu[i]*Ybus_modulos[i,k]*V_pu[k]*np.cos(V_ang[i] - Ybus_angulos[i,k]- V_ang[k])*-1)
                        
            
            # Condición para la fuera de diagonal.
            elif i != j:
                J_Q_angulo[i,j] = ((V_pu[i]*Ybus_modulos[i,j]*V_pu[j]*np.cos(V_ang[i] - Ybus_angulos[i,j]- V_ang[j])))
                
    # Eliminamos las filas y columnas de la matriz jacobiana de la barra SL.
    # Las filas.
    matriz_sin_filas = np.delete(J_Q_angulo, indices_a_borrar, axis=0)

    # Las Columnas.
    J_Q_angulo = np.delete(matriz_sin_filas, indice_borrar_SL, axis=1)


    # =================================================================================== Jacobiana de Q - Voltajes. ===================================================================================

    # Calculamos la submatriz jacobiana que depende de los voltajes.
    J_Q_Voltaje = np.zeros ((len(Bus_type), len(Bus_type)))

    # Bucle encargado de leer las posiciones de la matriz jacobiana.
    for i in range(len(Bus_type)):
        for j in range(len(Bus_type)):
            
            # Condición para la diagonal.
            if i == j: 
                
                # Bucle encargado de calcular valores cuadraticos.
                for k in range(len(Bus_type)):
                    if i == k:
                        J_Q_Voltaje[i,j] += (2*(V_pu[i]*Ybus_modulos[i,j]*np.sin(Ybus_angulos[i,k])))
                        
                    else:
                        J_Q_Voltaje[i,j] += (-1*(V_pu[k]*Ybus_modulos[i,k]*np.sin(V_ang[i] - Ybus_angulos[i,k]- V_ang[k])))
                        
            
            # Condición para la fuera de diagonal.
            elif i != j:
                J_Q_Voltaje[i,j] = 1    # Ignorar, solo es un valor de referencia.
                
    # Eliminamos las filas y columnas de la matriz jacobiana de la barra SL y PV.
    # Las columnas.
    J_Q_Voltaje = np.delete(J_Q_Voltaje, indices_a_borrar, axis=1)

    # Las filas.
    J_Q_Voltaje = np.delete(J_Q_Voltaje, indices_a_borrar, axis=0)

    # ==================================================================================== Jacobiana de P. ===================================================================================

    # Agrega J_Q_Voltaje al final de J_Q_Angulo
    J_Q_Completa = np.hstack((J_Q_angulo, J_Q_Voltaje))


    # ===================================================================================== Jacobiana. =======================================================================================
    # Agrega J_Q_Completa como filas al final de J_P_Completa
    Jacobiana_Completa = np.vstack((J_P_Completa, J_Q_Completa))

    # ===========================================================================================================================================================================================================
    # Armamos matrices para el método de Newton Raphson.

    # Eliminamos la barra SL y PV de Voltajes.
    Voltajes = np.delete(V_pu, indices_a_borrar)
    # Eliminamos angulos de la barra SL.
    Angulos_N = np.delete(V_ang, indice_borrar_SL)
    Angulos_N = Angulos_N.reshape(-1, 1)

    # Creamos la matriz incognita.
    incognita = np.vstack((Angulos_N, Voltajes))
    
    iteraciones += 1
    