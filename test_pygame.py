import pygame
import sys

# Initialisation de Pygame
pygame.init()

# Couleurs
BLANC = (255, 255, 255)
ROUGE = (255, 0, 0)

# Paramètres de la fenêtre
largeur_fenetre = 400
hauteur_fenetre = 200
fenetre = pygame.display.set_mode((largeur_fenetre, hauteur_fenetre))
pygame.display.set_caption('Deux cercles')

# Paramètres des cercles
rayon = 20
cercle1_x = 50
cercle2_x = 200
cercle_y = hauteur_fenetre // 2

# Vitesse de déplacement
vitesse = 5

en_deplacement = False

# Boucle principale
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_p:
                en_deplacement = not en_deplacement

    if en_deplacement:
        cercle1_x += vitesse

        # Si les cercles sortent de l'écran, réinitialise leur position
        if cercle1_x > cercle2_x - 20:
            cercle1_x = cercle2_x - 20

    # Efface l'écran
    fenetre.fill(BLANC)

    # Dessine les cercles
    pygame.draw.circle(fenetre, ROUGE, (cercle1_x, cercle_y), rayon)
    pygame.draw.circle(fenetre, ROUGE, (cercle2_x, cercle_y), rayon)

    # Met à jour l'affichage
    pygame.display.flip()

    # Limite le taux de rafraîchissement
    pygame.time.delay(30)
