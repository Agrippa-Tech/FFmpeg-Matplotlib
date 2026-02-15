"""
Exemplo de uso do módulo ffmpeg_config com animação heliocêntrica
=================================================================

Este arquivo demonstra como usar o módulo ffmpeg_config para
simplificar o salvamento de animações Matplotlib.

=================================================================
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from collections import deque

# IMPORTAR O MÓDULO FFMPEG_CONFIG
from ffmpeg_config import configurar_ffmpeg, salvar_animacao

# ===================================================================
# CONFIGURAÇÃO DO FFMPEG (UMA ÚNICA VEZ NO INÍCIO)
# ===================================================================

# Opção 1: Detecção automática (RECOMENDADO)
configurar_ffmpeg()

# Opção 2: Se preferir definir o caminho manualmente (Windows)
# configurar_ffmpeg(r'C:\ffmpeg\bin\ffmpeg.exe')

# Opção 3: Para macOS/Linux (se não estiver no PATH)
# configurar_ffmpeg('/usr/local/bin/ffmpeg')

# ===================================================================
# CÓDIGO DA ANIMAÇÃO 
# ===================================================================

# Configuração da figura 2D com alta resolução
fig, ax = plt.subplots(figsize=(6, 6), dpi=150) 
ax.set_xlim(-55, 55)
ax.set_ylim(-55, 55)
ax.set_facecolor('black')
fig.patch.set_facecolor('black')
ax.set_aspect('equal')
ax.axis('off')
plt.rcParams['font.family'] = 'serif'

# Adiciona estrelas
np.random.seed(42)  
num_estrelas = 300
estrelas_x = np.random.uniform(-60, 60, num_estrelas)
estrelas_y = np.random.uniform(-60, 60, num_estrelas)
estrelas_tamanhos = np.random.uniform(0.1, 1.5, num_estrelas)
estrelas_brilho = np.random.uniform(0.3, 1.0, num_estrelas)

# Desenhar as estrelas fixas
for i in range(num_estrelas):
    ax.plot(estrelas_x[i], estrelas_y[i], 'o', color='white', 
            markersize=estrelas_tamanhos[i], alpha=estrelas_brilho[i], zorder=1)

# Dados dos planetas (raio orbital, velocidade, cor, tamanho, nome, epiciclos)
planetas_dados = [
    {'nome': 'Mercúrio', 'raio': 10, 'velocidade': 0.08, 'cor': '#8C7853', 'tamanho': 75,
     'epiciclo1_raio': 1.5, 'epiciclo1_vel': 0.15,
     'epiciclo2_raio': 1.0, 'epiciclo2_vel': -0.22},
    {'nome': 'Vênus', 'raio': 16, 'velocidade': 0.06, 'cor': '#FFC649', 'tamanho': 100,
     'epiciclo1_raio': 1.8, 'epiciclo1_vel': -0.12,
     'epiciclo2_raio': 1.2, 'epiciclo2_vel': 0.18},
    {'nome': 'Terra', 'raio': 22, 'velocidade': 0.05, 'cor': '#4169E1', 'tamanho': 120,
     'epiciclo1_raio': 2.0, 'epiciclo1_vel': 0.08,
     'epiciclo2_raio': 0, 'epiciclo2_vel': 0},  
    {'nome': 'Marte', 'raio': 29, 'velocidade': 0.04, 'cor': '#CD5C5C', 'tamanho': 80,
     'epiciclo1_raio': 2.2, 'epiciclo1_vel': -0.18,
     'epiciclo2_raio': 1.4, 'epiciclo2_vel': 0.25},
    {'nome': 'Júpiter', 'raio': 38, 'velocidade': 0.03, 'cor': '#DAA520', 'tamanho': 280,
     'epiciclo1_raio': 2.5, 'epiciclo1_vel': 0.08,
     'epiciclo2_raio': 1.6, 'epiciclo2_vel': -0.14},
    {'nome': 'Saturno', 'raio': 48, 'velocidade': 0.025, 'cor': '#F4A460', 'tamanho': 220,
     'epiciclo1_raio': 2.8, 'epiciclo1_vel': -0.09,
     'epiciclo2_raio': 1.8, 'epiciclo2_vel': 0.16}
]

# Dados da Lua 
lua_dados = {
    'raio_orbital': 2.0, 
    'velocidade': 0.15,
    'epiciclo_raio': 1.5,      
    'epiciclo_vel': 0.25,   
    'cor': '#C0C0C0',    
    'tamanho': 50         
}

# SOL - círculo dourado brilhante no centro
sol = plt.Circle((0, -0.5), 2.5, color="#FBFF00FF", zorder=100)
ax.add_patch(sol)

# Adicionar halo ao redor do sol
halo = plt.Circle((0, -0.5), 3.5, color="#FFD000FF", alpha=0.3, zorder=99)
ax.add_patch(halo)

# Adicionar texto "Sol" próximo ao sol
ax.text(0, 3.8, 'Sol', color='white', fontsize=12, 
        ha='center', zorder=101)

# Criar órbitas principais (deferentes - círculos completos)
for planeta in planetas_dados:
    orbita = plt.Circle((0, 0), planeta['raio'], color=planeta['cor'], 
                        fill=False, alpha=0.3, linewidth=1.5, linestyle='--')
    ax.add_patch(orbita)

# Criar círculos dos epiciclos (serão movidos durante animação)
epiciclos1_circulos = []
epiciclos2_circulos = []
for planeta in planetas_dados:
    # Primeiro epiciclo
    if planeta['epiciclo1_raio'] > 0:
        epiciclo1 = plt.Circle((0, 0), planeta['epiciclo1_raio'], 
                             color=planeta['cor'], fill=False, 
                             alpha=0.4, linewidth=2, linestyle='-')
        ax.add_patch(epiciclo1)
        epiciclos1_circulos.append(epiciclo1)
    else:
        epiciclos1_circulos.append(None)  
    
    # Segundo epiciclo
    if planeta['epiciclo2_raio'] > 0:
        epiciclo2 = plt.Circle((0, 0), planeta['epiciclo2_raio'], 
                             color=planeta['cor'], fill=False, 
                             alpha=0.4, linewidth=1.5, linestyle='-')
        ax.add_patch(epiciclo2)
        epiciclos2_circulos.append(epiciclo2)
    else:
        epiciclos2_circulos.append(None)  

# Criar círculo para o epiciclo da Lua
epiciclo_lua = plt.Circle((0, 0), lua_dados['epiciclo_raio'], 
                          color=lua_dados['cor'], fill=False, 
                          alpha=0.3, linewidth=2, linestyle='-')
ax.add_patch(epiciclo_lua)

# Criar círculo da órbita da Lua ao redor da Terra (será movido durante animação)
orbita_lua = plt.Circle((0, 0), lua_dados['raio_orbital'], 
                        color=lua_dados['cor'], fill=False, 
                        alpha=0.3, linewidth=1.5, linestyle=':')
ax.add_patch(orbita_lua)

# Criar círculos para cada planeta
planetas_circulos = []
for planeta in planetas_dados:
    # Calcular raio do círculo baseado no tamanho
    raio = np.sqrt(planeta['tamanho'] / np.pi) / 7
    circulo = plt.Circle((0, 0), raio, color=planeta['cor'], zorder=50)
    ax.add_patch(circulo)
    planetas_circulos.append(circulo)

# Criar círculo para a Lua
raio_lua = np.sqrt(lua_dados['tamanho'] / np.pi) / 7
circulo_lua = plt.Circle((0, 0), raio_lua, color=lua_dados['cor'], zorder=51)
ax.add_patch(circulo_lua)

# Criar labels dos planetas
labels_planetas = []
for planeta in planetas_dados:
    label = ax.text(0, 0, planeta['nome'], color='white', 
                    fontsize=10, ha='center', va='bottom', zorder=60)
    labels_planetas.append(label)

# Criar label da Lua
label_lua = ax.text(0, 0, 'Lua', color='white', 
                    fontsize=8, ha='center', va='bottom', zorder=60)

# Fase inicial aleatória para cada planeta e seus epiciclos
fases_iniciais_deferente = [np.random.uniform(0, 2*np.pi) for _ in planetas_dados]
fases_iniciais_epiciclo1 = [np.random.uniform(0, 2*np.pi) for _ in planetas_dados]
fases_iniciais_epiciclo2 = [np.random.uniform(0, 2*np.pi) for _ in planetas_dados]
fase_inicial_lua = np.random.uniform(0, 2*np.pi)
fase_inicial_lua_epiciclo = np.random.uniform(0, 2 *np.pi)

def init():
    """Inicializa a animação"""
    elementos_animados = planetas_circulos + labels_planetas 
    elementos_animados += [e for e in epiciclos1_circulos if e is not None]
    elementos_animados += [e for e in epiciclos2_circulos if e is not None]
    elementos_animados += [circulo_lua, label_lua, orbita_lua, epiciclo_lua]
    return elementos_animados

def update(frame):
    """Atualiza posições a cada frame"""
    
    # Posição da Terra (necessária para calcular posição da Lua)
    x_terra_final = 0
    y_terra_final = 0
    
    # Atualizar cada planeta
    for i, planeta in enumerate(planetas_dados):
        # Calcular ângulo atual no deferente (órbita principal)
        angulo_deferente = fases_iniciais_deferente[i] + planeta['velocidade'] * frame
        
        # Posição do centro do primeiro epiciclo no deferente
        x_deferente = planeta['raio'] * np.cos(angulo_deferente)
        y_deferente = planeta['raio'] * np.sin(angulo_deferente)
        
        # Se o planeta tem epiciclos 
        if planeta['epiciclo1_raio'] > 0:
            # Atualizar posição do círculo do primeiro epiciclo
            if epiciclos1_circulos[i] is not None:
                epiciclos1_circulos[i].set_center((x_deferente, y_deferente))
            
            # Calcular ângulo no primeiro epiciclo
            angulo_epiciclo1 = fases_iniciais_epiciclo1[i] + planeta['epiciclo1_vel'] * frame
            
            # Posição do centro do segundo epiciclo no primeiro epiciclo
            x_epiciclo1 = x_deferente + planeta['epiciclo1_raio'] * np.cos(angulo_epiciclo1)
            y_epiciclo1 = y_deferente + planeta['epiciclo1_raio'] * np.sin(angulo_epiciclo1)
            
            # Atualizar posição do círculo do segundo epiciclo
            if epiciclos2_circulos[i] is not None:
                epiciclos2_circulos[i].set_center((x_epiciclo1, y_epiciclo1))
            
            # Calcular ângulo no segundo epiciclo
            angulo_epiciclo2 = fases_iniciais_epiciclo2[i] + planeta['epiciclo2_vel'] * frame
            
            # Posição final do planeta: centro do segundo epiciclo + deslocamento no segundo epiciclo
            x_epiciclo2 = planeta['epiciclo2_raio'] * np.cos(angulo_epiciclo2)
            y_epiciclo2 = planeta['epiciclo2_raio'] * np.sin(angulo_epiciclo2)
            
            x_final = x_epiciclo1 + x_epiciclo2
            y_final = y_epiciclo1 + y_epiciclo2
        else:
            # Terra move-se apenas no deferente (sem epiciclos)
            x_final = x_deferente
            y_final = y_deferente
        
        # Guardar posição da Terra (índice 2)
        if i == 2:
            x_terra_final = x_final
            y_terra_final = y_final
        
        # Atualizar posição do círculo do planeta
        planetas_circulos[i].set_center((x_final, y_final))
        
        # Atualizar label do planeta (posicionado acima)
        raio_circulo = np.sqrt(planeta['tamanho'] / np.pi) / 7
        labels_planetas[i].set_position((x_final, y_final + raio_circulo + 1))
        
        
    
    # Atualizar órbita da Lua (centrada na Terra)
    orbita_lua.set_center((x_terra_final, y_terra_final))

    # Calcular ângulo no deferente lunar
    angulo_lua_def = fase_inicial_lua + lua_dados['velocidade'] * frame

    # Centro do epiciclo lunar (ponto no deferente)
    x_centro_epiciclo = x_terra_final + lua_dados['raio_orbital'] * np.cos(angulo_lua_def)
    y_centro_epiciclo = y_terra_final + lua_dados['raio_orbital'] * np.sin(angulo_lua_def)

    # Atualizar posição do círculo do epiciclo lunar
    epiciclo_lua.set_center((x_centro_epiciclo, y_centro_epiciclo))

    # Calcular ângulo no epiciclo lunar
    angulo_lua_epi = fase_inicial_lua_epiciclo + lua_dados['epiciclo_vel'] * frame

    # Posição final da Lua: centro do epiciclo + deslocamento no epiciclo
    x_lua = x_centro_epiciclo + lua_dados['epiciclo_raio'] * np.cos(angulo_lua_epi)
    y_lua = y_centro_epiciclo + lua_dados['epiciclo_raio'] * np.sin(angulo_lua_epi)

    # Atualizar posição da Lua
    circulo_lua.set_center((x_lua, y_lua))

    # Atualizar label da Lua
    label_lua.set_position((x_lua, y_lua + raio_lua + 0.5))
    
    elementos_animados = planetas_circulos + labels_planetas 
    elementos_animados += [e for e in epiciclos1_circulos if e is not None]
    elementos_animados += [e for e in epiciclos2_circulos if e is not None]
    elementos_animados += [circulo_lua, label_lua, orbita_lua, epiciclo_lua]
    return elementos_animados

# Título principal
plt.suptitle('Sistema Heliocêntrico de Copérnico', 
             color='white', fontsize=16, y=0.96, weight='bold')

# Legenda com informações
legenda_texto = 'De Revolutionibus Orbium Coelestium - 1543'
fig.text(0.5, 0.02, legenda_texto, ha='center', color='gray', fontsize=11)

plt.tight_layout()


# ===================================================================
# CRIAR E SALVAR ANIMAÇÃO 
# ===================================================================

print("Criando animação...")

# Número de frames
#600 frames equivale a 30 segundos
num_frames = 600

# Criar animação
ani = FuncAnimation(fig, update, init_func=init, frames=num_frames, 
                   interval=50, blit=True, cache_frame_data=False)

# ===================================================================
# SALVAR VÍDEO 
# ===================================================================

# Opção 1: Uso simples (qualidade alta, 20 FPS)
salvar_animacao(ani, 'sistema_heliocentrico_simples.mp4')

# Opção 2: Customizar FPS e qualidade
# salvar_animacao(ani, 'sistema_heliocentrico_hd.mp4', 
#                 fps=30, quality='ultra', dpi=200)

# Opção 3: Vídeo rápido para preview (baixa qualidade)
# salvar_animacao(ani, 'preview.mp4', 
#                 fps=15, quality='low', dpi=100)

# Opção 4: Com metadados personalizados
# salvar_animacao(ani, 'sistema_heliocentrico.mp4',
#                 fps=24, 
#                 quality='high',
#                 metadata={'artist': 'Seu Nome', 'title': 'Sistema Heliocêntrico'})

print("\n✓ Processo concluído!")



'''
      db            .g8"""bgd      `7MM"""Mq.      `7MMF'    `7MM"""Mq.     `7MM"""Mq.           db
     ;MM:         .dP'     `M        MM   `MM.       MM        MM   `MM.      MM   `MM.         ;MM:
    ,V^MM.        dM'       `        MM   ,M9        MM        MM   ,M9       MM   ,M9         ,V^MM.
   ,M  `MM        MM                 MMmmdM9         MM        MMmmdM9        MMmmdM9         ,M  `MM
   AbmmmqMA       MM.    `7MMF'      MM  YM.         MM        MM             MM              AbmmmqMA
  A'     VML      `Mb.     MM        MM   `Mb.       MM        MM             MM             A'     VML
.AMA.   .AMMA.      `"bmmmdPY      .JMML. .JMM.    .JMML.    .JMML.         .JMML.         .AMA.   .AMMA.
'''