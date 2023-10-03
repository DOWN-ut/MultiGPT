import tkinter as tk
from tkinter import scrolledtext
from tkinter import PhotoImage
import math
import random
import time

# Données de la conversation
messagesList = [
    {"name": "Normi", "text": "Coucou je suis un loup garou"},
    {"name": "Adele", "text": "Salut ! Je suis voyante aaaaaaaaaaaaaaaaaa"}
]

def addAMessage(player, message):
    messagesList.append({"name": player, "text": message})

agents = [
	{"name": "Bob", "image_path": "images/werewolf.png"}, 
    {"name": "Alice", "image_path": "images/villager.png"},
    {"name": "Adele", "image_path": "images/seer.png"},
    {"name": "Yahnis", "image_path": "images/witch.png"},
    {"name": "Lea", "image_path": "images/werewolf.png"},
    {"name": "Normi", "image_path": "images/traitre.png"}
]

num_circles = 6
random_color = []

for _ in range(num_circles):
    while True:
        # Générer des composants de couleur RVB aléatoires
        red = random.randint(100, 255)
        green = random.randint(100, 255)
        blue = random.randint(100, 255)
        
        # Vérifier si la couleur est suffisamment lumineuse (non foncée)
        if (red + green + blue) / 3 > 150:  # Exemple de seuil de luminosité
            break

    # Ajouter la couleur générée à la liste
    random_color.append("#{:02X}{:02X}{:02X}".format(red, green, blue))

# Créez une liste pour stocker les objets PhotoImage
image_list = []

# Modifiez la fonction pour dessiner les cercles et afficher les images
def draw_circles_with_names_and_images(canvas):
    circle_radius = 60
    circle_center_x = 400
    circle_center_y = 300
    circle_spacing = 150

    # Dessiner les cercles
    for i in range(num_circles):
        angle = 2 * math.pi * i / num_circles
        x = circle_center_x + (circle_radius + circle_spacing) * math.cos(angle)
        y = circle_center_y + (circle_radius + circle_spacing) * math.sin(angle)
        canvas.create_oval(x - circle_radius, y - circle_radius, x + circle_radius, y + circle_radius, fill=random_color[i])

        # Ajouter les noms au-dessus des cercles
        element = agents[i]
        name = element["name"]
        canvas.create_text(x, y, text=name)

        # Ajouter les images en dessous des cercles
        image_path = element.get("image_path")  # Obtenir le chemin de l'image
        if image_path:
            image = PhotoImage(file=image_path)  # Charger l'image
            image = image.subsample(6, 6)
            image_list.append(image)  # Ajouter l'image à la liste
            canvas.create_image(x, y + circle_radius + 10, anchor=tk.N, image=image)


        # Ajouter les noms au-dessus des cercles
        element = agents[i]
        name = element["name"]
        canvas.create_text(x, y, text=name)


def displayConversation(right_frame, fenetre) :
    # Créer un widget Texte défilant pour la conversation dans la partie droite
    conversation = scrolledtext.ScrolledText(right_frame, wrap=tk.WORD, state=tk.DISABLED, width=30)
    conversation.pack(fill=tk.BOTH, expand=True)
    conversation.configure(bg="#262626")

    for i in range (6) :
        conversation.tag_configure(agents[i]["name"], foreground=random_color[i])

    # Parcourir la liste de messages et les afficher
    for message_data in messagesList:
        name = message_data["name"]
        message = message_data["text"]
        conversation.config(state=tk.NORMAL)  # Activer l'édition
        conversation.insert(tk.END, f" {name} : {message}\n", message_data["name"])
        conversation.config(state=tk.DISABLED)  # Désactiver l'édition
        conversation.yview(tk.END)  # Faire défiler vers le bas
        fenetre.update()
        time.sleep(1.5)


def display_game() :

    # Créer une fenêtre
    fenetre = tk.Tk()
    fenetre.title("Chat Fenêtre")

    # Réduire la largeur de la fenêtre avec le texte
    fenetre.geometry("1200x700")  # Largeur x Hauteur

    # Diviser la fenêtre en deux parties (gauche et droite)
    left_frame = tk.Frame(fenetre)
    right_frame = tk.Frame(fenetre)

    fenetre.configure(bg="white")

    left_frame.pack(side=tk.LEFT, padx=10)
    right_frame.pack(side=tk.RIGHT, padx=10, fill=tk.BOTH, expand=True)

    # Créer un canevas pour dessiner les cercles dans la partie gauche
    canvas = tk.Canvas(left_frame, width=800, height=700)
    canvas.configure(bg="white")
    canvas.pack()
    draw_circles_with_names_and_images(canvas)

    addAMessage("Bob", "Salut, comment ça va ?")
    addAMessage("Yahnis", "Test")

    displayConversation(right_frame, fenetre)

    # Démarrer la fenêtre principale
    fenetre.mainloop()

display_game()




