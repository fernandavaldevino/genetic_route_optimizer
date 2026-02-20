#!/usr/bin/env python3
"""
Sistema de Otimização de Rotas com Restrições
Algoritmo Genético para Roteamento de Atendimentos em Saúde da Mulher

Autor: Fernanda Valdevino - Projeto Fase 2
"""

import sys
import os

# Adicionar src ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from visualization.pygame_viewer import main as run_visualization

if __name__ == '__main__':
    print("="*60)
    print("SISTEMA DE ROTEAMENTO COM RESTRIÇÕES")
    print("="*60)
    print("\nControles:")
    print("  Q ou ESC - Sair")
    print("  R - Reiniciar com novos pontos")
    print("\nLegenda de Cores:")
    print("  Vermelho - Emergência Obstétrica (prioridade máxima)")
    print("  Laranja - Violência Doméstica (protocolo especial)")
    print("  Azul - Medicamento Hormonal (temperatura controlada)")
    print("  Roxo - Pós-Parto (janela de tempo específica)")
    print("  Cinza - Atendimento Regular")
    print("\n" + "="*60)
    print("Iniciando visualização...\n")
    
    run_visualization()
