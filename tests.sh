#!/bin/bash

echo "=== Iniciando Suite de Pruebas de Red Bayesiana ==="

# Crear directorio para resultados si no existe
mkdir -p test_results

# 1. Pruebas de Validación
echo -e "\n=== 1. Pruebas de Validación ==="
echo "Test 1: Validación básica de la red"
python3 src/valida_red.py --edges data/edges.csv --cpts data/ 2>&1 | tee test_results/test1.log

echo "Test 2: Prueba con archivo edges incorrecto"
python3 src/valida_red.py --edges data/edges_invalid.csv --cpts data/ 2>&1 | tee test_results/test2.log

echo "Test 3: Prueba con CPTs incompletos"
python3 src/valida_red.py --edges data/edges.csv --cpts data/incomplete/ 2>&1 | tee test_results/test3.log

# 2. Pruebas de Consultas Básicas
echo -e "\n=== 2. Pruebas de Consultas Básicas ==="
echo "Test 4: Consulta simple sin evidencia"
python3 src/consulta.py --edges data/edges.csv --cpts data/ --query NodoFinal 2>&1 | tee test_results/test4.log

echo "Test 5: Consulta con una evidencia"
python3 src/consulta.py --edges data/edges.csv --cpts data/ --query NodoFinal --evidence "NodoInicial=true" 2>&1 | tee test_results/test5.log

echo "Test 6: Consulta con múltiples evidencias"
python3 src/consulta.py --edges data/edges.csv --cpts data/ --query NodoFinal --evidence "NodoInicial=true,NodoMedio=false" 2>&1 | tee test_results/test6.log

# 3. Pruebas de Casos Especiales
echo -e "\n=== 3. Pruebas de Casos Especiales ==="
echo "Test 7: Consulta sobre nodo con 3+ padres"
python3 src/consulta.py --edges data/edges.csv --cpts data/ --query NodoComplejo 2>&1 | tee test_results/test7.log

echo "Test 8: Consulta sobre nodo con un solo padre"
python3 src/consulta.py --edges data/edges.csv --cpts data/ --query NodoSimple 2>&1 | tee test_results/test8.log

echo "Test 9: Consulta con todas las evidencias posibles"
python3 src/consulta.py --edges data/edges.csv --cpts data/ --query NodoFinal --evidence "Nodo1=true,Nodo2=false,Nodo3=true" 2>&1 | tee test_results/test9.log

# Resumen de resultados
echo -e "\n=== Resumen de Pruebas ==="
echo "Los resultados detallados se encuentran en el directorio test_results/"
echo "Revise los archivos .log para ver la salida completa de cada prueba"

echo -e "\n=== Pruebas Completadas ==="