#!/usr/bin/env python3
"""
Sistema de Otimização de Rotas com 2 Veículos
Algoritmo Genético para Roteamento de Atendimentos em Saúde da Mulher

Autor: Fernanda Valdevino - Projeto Fase 2
"""

import sys
import os

# Adicionar src ao path (ajustar para a nova estrutura)
project_root = os.path.join(os.path.dirname(__file__), '..')
sys.path.insert(0, project_root)
sys.path.insert(0, os.path.join(project_root, 'src'))

from src.visualization.pygame_viewer_2v import main as run_visualization

if __name__ == '__main__':
    # Verificar se foi passado o número de gerações como argumento
    max_generations = 10  # Valor padrão
    if len(sys.argv) > 1:
        try:
            max_generations = int(sys.argv[1])
        except ValueError:
            print(f"Aviso: Argumento inválido '{sys.argv[1]}', usando padrão de {max_generations} gerações")
    
    print("="*60)
    print("SISTEMA DE ROTEAMENTO COM 2 VEÍCULOS + DEPÓSITO")
    print("="*60)
    print(f"\nGerações: {max_generations}")
    print("\nControles:")
    print("  Q ou ESC - Sair")
    print("  R - Reiniciar com novos pontos")
    print("\nObjetivo:")
    print("  - Veículos partem e retornam ao depósito (D)")
    print("  - Pontos prioritários (EME, VIO, MED, POS) até 12h")
    print("  - Pontos regulares (REG) após 12h")
    print("  - Todos os 20 pontos em 1 dia")
    print("\nVisualização:")
    print("  - Linhas finas coloridas: prioridade de cada entrega")
    print("  - Linhas grossas verde/ciano: veículo responsável")
    print("  - Círculo 'D' amarelo: depósito (origem/destino)")
    print("\n" + "="*60)
    print("Iniciando visualização...\n")
    
    run_visualization(max_generations)
