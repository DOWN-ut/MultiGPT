import tkinter as tk
from tkinter import scrolledtext
import math

# Données de la conversation
messagesList = [
    {"name": "Normi", "text": "Coucou je suis un loup garou"},
    {"name": "Adèle", "text": "Salut ! Je suis voyante"}
]

# Fonction pour dessiner les cercles et les noms
def draw_circles_with_names(canvas):
    num_circles = 6
    circle_radius = 60
    circle_center_x = 300
    circle_center_y = 300
    circle_spacing = 100

    # Dessiner les cercles
    for i in range(num_circles):
        angle = 2 * math.pi * i / num_circles
        x = circle_center_x + (circle_radius + circle_spacing) * math.cos(angle)
        y = circle_center_y + (circle_radius + circle_spacing) * math.sin(angle)
        canvas.create_oval(x - circle_radius, y - circle_radius, x + circle_radius, y + circle_radius, fill="red")

        # Ajouter les noms au-dessus des cercles
        name = f"Joueur {i+1}"
        canvas.create_text(x, y, text=name)

# Créer une fenêtre
fenetre = tk.Tk()
fenetre.title("Chat Fenêtre")

# Réduire la largeur de la fenêtre avec le texte
fenetre.geometry("1000x600")  # Largeur x Hauteur

# Diviser la fenêtre en deux parties (gauche et droite)
left_frame = tk.Frame(fenetre)
right_frame = tk.Frame(fenetre)

fenetre.configure(bg="white")

left_frame.pack(side=tk.LEFT, padx=10)
right_frame.pack(side=tk.RIGHT, padx=10, fill=tk.BOTH, expand=True)

# Créer un canevas pour dessiner les cercles dans la partie gauche
canvas = tk.Canvas(left_frame, width=600, height=600)
canvas.configure(bg="white")
canvas.pack()
draw_circles_with_names(canvas)

# Créer un widget Texte défilant pour la conversation dans la partie droite
conversation = scrolledtext.ScrolledText(right_frame, wrap=tk.WORD, state=tk.DISABLED, width=30)
conversation.pack(fill=tk.BOTH, expand=True)
conversation.configure(bg="#262626")
conversation.tag_configure("user", foreground="blue")

# Parcourir la liste de messages et les afficher
for message_data in messagesList:
    name = message_data["name"]
    message = message_data["text"]
    conversation.config(state=tk.NORMAL)  # Activer l'édition
    conversation.insert(tk.END, f" {name} : {message}\n", "user")
    conversation.config(state=tk.DISABLED)  # Désactiver l'édition
    conversation.yview(tk.END)  # Faire défiler vers le bas

# Démarrer la fenêtre principale
fenetre.mainloop()




