# 🤖 IA para Hex con Monte Carlo Tree Search (MCTS)

Este proyecto implementa una Inteligencia Artificial para el juego de **Hex** en la clase **AIPlayer**, utilizando el algoritmo **Monte Carlo Tree Search (MCTS)**. El objetivo es permitir que la IA tome decisiones estratégicas basadas en simulaciones rápidas y efectivas.

## 🎯 Objetivo

Desarrollar un agente capaz de jugar Hex de manera autónoma, tomando decisiones informadas mediante simulaciones. La IA analiza miles de posibles partidas en un tiempo limitado y elige el movimiento más prometedor.

## 🧠 ¿Qué es MCTS?

**Monte Carlo Tree Search** es un algoritmo de búsqueda basado en simulaciones. Se utiliza en juegos con muchos estados posibles (como Hex) porque no requiere una evaluación estática del tablero. En su lugar, realiza partidas aleatorias para estimar la calidad de cada jugada.

El algoritmo se divide en cuatro fases principales:

1. **Selección**: se elige el camino más prometedor según una fórmula que equilibra exploración y explotación.
2. **Expansión**: se agregan nuevos nodos al árbol para representar nuevas jugadas.
3. **Simulación**: se realizan partidas aleatorias desde ese estado.
4. **Retropropagación**: se actualizan las estadísticas del árbol con los resultados obtenidos.
