import pygame
import textwrap
import random
import math

# Initialisation de Pygame
pygame.init()

# Dimensions de la fenêtre
largeur_fenetre = 1100
hauteur_fenetre = 600

# Création de la fenêtre
fenetre = pygame.display.set_mode((largeur_fenetre, hauteur_fenetre))

# Titre de la fenêtre
pygame.display.set_caption("MultiGPT")

# Couleurs
blanc = (255, 255, 255)
gris = (59, 63, 64)

# Position de séparation
separation_x = largeur_fenetre // 4

# Texte pour la boîte de dialogue
texte_boite_dialogue = "Bob : Hi!"

# Liste de textes à afficher à droite
textes_a_afficher = [
    "Texte 1 ddddddddddddddddddddddddddddddd",
    "Texte 2",
    "Texte 3",
]

# Police de texte
police = pygame.font.Font(None, 25)

# Diviser le texte en lignes
#texte_divise = textwrap.wrap(texte_boite_dialogue, width=21)

for texte in textes_a_afficher :
    texte_divise = textwrap.wrap(texte, width=21)


agents = [
    {"name": "Bob", "x": 0, "y": 0}, 
    {"name": "Alice", "x": 0, "y": 0},
    {"name": "Adele", "x": 0, "y": 0},
    {"name": "Toto", "x": 0, "y": 0},
    {"name": "Lilou", "x": 0, "y": 0},
    {"name": "Patrick", "x": 0, "y": 0}
]

# Position du cercle central
cercle_central_x = (largeur_fenetre // 3) - 60
cercle_central_y = hauteur_fenetre // 2

# Rayon du cercle central
rayon_central = 20

# Couleur du cercle central
couleur_central = (255, 0, 0)  # Rouge

# Nombre de cercles autour du cercle central
nombre_cercles = 6

# Rayon des cercles autour
rayon_cercles = 200

# Texte au-dessus du cercle central
gameMasterName = "Game Master"

# Police pour le texte
police = pygame.font.Font(None, 36)

# Liste de couleurs aléatoires pour les cercles
couleurs_aleatoires = [(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)) for _ in range(nombre_cercles)]


# Rendre le texte sur une surface
texte_surfaces = []
for ligne in texte_divise:
    texte_surface = police.render(ligne, True, (0, 0, 0))
    texte_surfaces.append(texte_surface)

# Position du point
x_point = separation_x // 2
y_point = hauteur_fenetre // 2
rayon_point = 10

# Vitesse de rotation du point
vitesse_rotation = 2

# Boucle de jeu
en_cours = True
while en_cours:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            en_cours = False

    # Effacer l'écran
    fenetre.fill(blanc)

    # Dessiner la ligne de séparation
    pygame.draw.line(fenetre, (0, 0, 0), (largeur_fenetre - separation_x - (largeur_fenetre // 6), 0), (largeur_fenetre - separation_x - (largeur_fenetre // 6), hauteur_fenetre), 2)

    # Dessiner le carré gris derrière le texte de droite
    pygame.draw.rect(fenetre, gris, (largeur_fenetre - separation_x - (largeur_fenetre // 6), 0, separation_x + (largeur_fenetre // 6), hauteur_fenetre))

    # Dessiner le cercle central
    pygame.draw.circle(fenetre, couleur_central, (cercle_central_x, cercle_central_y), rayon_central)

    # Dessiner les cercles autour avec des couleurs aléatoires
    for i in range(nombre_cercles):
        angle = (2 * math.pi / nombre_cercles) * i
        x = cercle_central_x + int(rayon_cercles * math.cos(angle))
        y = cercle_central_y + int(rayon_cercles * math.sin(angle))

        #Stock de la position des agents
        element = agents[i]

        texte_surface = police.render(element['name'], True, couleurs_aleatoires[i])
        texte_rect = texte_surface.get_rect()
        texte_rect.center = (x, y - 50)
        fenetre.blit(texte_surface, texte_rect)

        pygame.draw.circle(fenetre, couleurs_aleatoires[i], (x, y), 30)  # Couleurs aléatoires

    # Afficher le texte au-dessus du cercle central
    texte_surface = police.render(gameMasterName, True, couleur_central)
    texte_rect = texte_surface.get_rect()
    texte_rect.center = (cercle_central_x, cercle_central_y - rayon_central - 20)
    fenetre.blit(texte_surface, texte_rect)

    # Afficher le texte dans la partie droite
    y_texte = 20

    # Afficher la liste de textes à droite
    for texte in textes_a_afficher:
        texte_surface = police.render(texte, True, (0, 0, 0))
        texte_rect = texte_surface.get_rect()
        texte_rect.topleft = (largeur_fenetre - separation_x - (largeur_fenetre // 6) + 20, y_texte - 10)
        fenetre.blit(texte_surface, texte_rect)
        y_texte += texte_surface.get_height()

    # Mettre à jour l'affichage
    pygame.display.flip()

# Quitter Pygame
pygame.quit()
