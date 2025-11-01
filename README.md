# Proyecto3_IA
Tercer proyecto de la clase introducción a inteligencia artificial, realizado en pyton

# Estructura del Proyecto
```
Proyecto3_IA/
├── src/
│   ├── bn.py                     # Implementación de la red bayesiana
│   ├── consulta.py              # Sistema de consultas
│   ├── inferencia_enumeracion.py # Motor de inferencia
│   └── valida_red.py            # Validador de la red
├── data/
│   ├── edges.csv                # Estructura de la red
│   └── cpt_*.csv               # Tablas de probabilidad condicional
└── out/                        # Directorio para resultados
```

# Preparación de Datos
1. edges.csv
Debe contener la estructura de la red con el siguiente formato:
``` 
child,parent
NodoHijo,NodoPadre
```
2. CPT
Para cada nodo, crear un archivo ```cpt_NOMBRE.csv```:
```
NodoPadre1,NodoPadre2,Nodo,P
true,true,true,0.9
true,true,false,0.1
```

# Uso
1. Validar la Red
```py
python src/valida_red.py --edges data/edges.csv --cpts data/
```

2. Realizar Consultas
```py
python src/consulta.py --edges data/edges.csv --cpts data/ --query VARIABLE [--evidence "VAR1=valor,VAR2=valor"]
```

# Salida del Sistema
* Los resultados se guardan en out/traza_VARIABLE_TIMESTAMP.txt
* El archivo incluye:
    * Visualización del grafo
    * Traza detallada del proceso de inferencia
    * Distribución de probabilidad resultante

