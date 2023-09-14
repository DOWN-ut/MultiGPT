import pygame
import sys
import random
import math

# Initialisation de Pygame
pygame.init()

# Définition de la taille de la fenêtre
largeur = 800
hauteur = 600

# Création de la fenêtre
fenetre = pygame.display.set_mode((largeur, hauteur))

# Titre de la fenêtre
pygame.display.set_caption("MultiGPT")

agents = [
	{"name": "Bob", "x": 0, "y": 0}
]

# Position du cercle central
cercle_central_x = largeur // 2
cercle_central_y = hauteur // 2

# Rayon du cercle central
rayon_central = 50

# Couleur du cercle central
couleur_central = (255, 0, 0)  # Rouge

# Nombre de cercles autour du cercle central
nombre_cercles = 8

# Rayon des cercles autour
rayon_cercles = 200

# Texte au-dessus du cercle central
texte = "Game Master"

# Police pour le texte
police = pygame.font.Font(None, 36)

# Liste de couleurs aléatoires pour les cercles
couleurs_aleatoires = [(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)) for _ in range(nombre_cercles)]

vitesse = 5

en_deplacement = False

# Boucle principale du jeu
en_cours = True
while en_cours:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            en_cours = False

        '''
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_p:
                en_deplacement = not en_deplacement
        '''

    # Effacer l'écran avec la couleur de fond (blanc)
    fenetre.fill((255, 255, 255))

    # Dessiner le cercle central
    pygame.draw.circle(fenetre, couleur_central, (cercle_central_x, cercle_central_y), rayon_central)

    # Dessiner les cercles autour avec des couleurs aléatoires
    for i in range(nombre_cercles):
        angle = (2 * math.pi / nombre_cercles) * i
        x = cercle_central_x + int(rayon_cercles * math.cos(angle))
        y = cercle_central_y + int(rayon_cercles * math.sin(angle))

        if (i == 0) :
            '''
            if en_deplacement:
                x += 20
            '''

            #Stock de la position des agents
            element = agents[0]
            element['x'] = x
            element['y'] = y

        pygame.draw.circle(fenetre, couleurs_aleatoires[i], (x, y), 30)  # Couleurs aléatoires

    # Afficher le texte au-dessus du cercle central
    texte_surface = police.render(texte, True, couleur_central)
    texte_rect = texte_surface.get_rect()
    texte_rect.center = (cercle_central_x, cercle_central_y - rayon_central - 20)
    fenetre.blit(texte_surface, texte_rect)

    # Mettre à jour l'affichage
    pygame.display.flip()

# Quitter Pygame
pygame.quit()
sys.exit()
