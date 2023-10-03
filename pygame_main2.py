import tkinter as tk
from tkinter import scrolledtext
from tkinter import PhotoImage
import math
import random
import time

# Données de la conversation
messagesList = []

gameMasterColor = [0,0,0]

roleImages = {}
roleImages["Villager"] = "images/villager.png"
roleImages["Werewolf"] = "images/werewolf.png"
roleImages["Seer"] = "images/seer.png"
roleImages["Traitor"] = "images/traitor.png"
roleImages["Witch"] = "images/witch.png"

headImages = {}
headImages["Neutral"] = "images/smile.png"
headImages["Sad"] = "images/sad.png"
headImages["Cry"] = "images/cry.png"
headImages["Winner"] = "images/tongue.png"
headImages["Sleep"] = "images/sleep.png"

playerDisplayers = []

window_size = (800,700)
right_frame = ""
left_frame = ""
conversation = ""
canvas = ""
fenetre = ""

def addAMessage(playerName, message):
    conversation.config(state=tk.NORMAL)  # Activer l'édition
    conversation.insert(tk.END, f"  {playerName} : {message}\n", playerName)
    conversation.config(state=tk.DISABLED)  # Désactiver l'édition
    conversation.yview(tk.END) # Faire défiler vers le bas
    #messagesList.append({"name": player, "text": message})
    fenetre.update()

def colorOf(rgb):
    return "#{:02X}{:02X}{:02X}".format(rgb[0],rgb[1],rgb[2])

player_circle_distance = 300
player_card_distance = 225
player_name_distance = 375


# Créez une liste pour stocker les objets PhotoImage
image_list = []

def mul(v1,f):
    return (v1[0] * f, v1[1] * f)

def window_center():
    return (window_size[0] * 0.5, window_size[1] * 0.5)

def draw_gamemaster(canvas):
    draw_circle(canvas,(0,0),75,gameMasterColor)
    draw_text(canvas,(0,0),(50,15),"Game Master",[200,200,200])

def draw_player(canvas,player):
    direction = (math.cos(math.radians(player.position)),math.sin(math.radians(player.position)))
    circle_position = mul(direction,player_circle_distance)
    card_position = mul(direction,player_card_distance)
    name_position = mul(direction,player_name_distance)

    #draw_circle(canvas,circle_position,55,player.color)
    draw_head(canvas,circle_position,"Sleep")
    draw_text(canvas,name_position,(len(player.name)*10,15),player.name,player.color)
    draw_card(canvas,card_position,player.role)

def draw_circle(canvas,center,r,color):
    x = center[0] + window_center()[0]
    y = center[1] + window_center()[1]
    canvas.create_oval(x - r, y - r, x + r, y + r, fill=colorOf(color))

def draw_head(canvas,center,emotion):
    image_path = headImages[emotion]
    image = PhotoImage(file=image_path)  # Charger l'image
    image = image.subsample(5,5)
    image_list.append(image)  # Ajouter l'image à la liste
    canvas.create_image(window_center()[0] + center[0], window_center()[1] + center[1] - 51, anchor=tk.N, image=image)

def draw_text(canvas,position,size,txt,color):
    rx = window_center()[0] + position[0]
    ry = window_center()[1] + position[1]
    canvas.create_rectangle(rx - (size[0] * 0.5),ry - (size[1] * 0.5),rx + (size[0] * 0.5),ry + (size[1] * 0.5), fill="black")
    canvas.create_text(position[0] + window_center()[0],position[1] + window_center()[1], text=txt,fill=colorOf(color))
    
def draw_card(canvas,center,role):
    image_path = roleImages[role]
    image = PhotoImage(file=image_path)  # Charger l'image
    image = image.subsample(9,9)
    image_list.append(image)  # Ajouter l'image à la liste
    canvas.create_image(window_center()[0] + center[0], window_center()[1] + center[1] - 20, anchor=tk.N, image=image)

class PlayerDisplayer:
    def __init__(self,name,role,color,position):
        self.name = name
        self.color = color
        self.role = role
        self.color = color
        self.position = position

def setup_right(right_frame):
    # Créer un widget Texte défilant pour la conversation dans la partie droite
    global conversation
    conversation = scrolledtext.ScrolledText(right_frame, wrap=tk.WORD, state=tk.DISABLED, width=30)
    conversation.pack(fill=tk.BOTH, expand=True)
    conversation.configure(bg="#262626")
    
    conversation.tag_configure("Game Master", foreground=colorOf(gameMasterColor))
    for playerd in playerDisplayers:
        conversation.tag_configure(playerd.name, foreground=colorOf(playerd.color))


def display_game(actTime):
    
    canvas.delete("all")

    draw_gamemaster(canvas)

    for playerd in playerDisplayers:
        draw_player(canvas,playerd)

    fenetre.update()




def setup_window() :

    # Créer une fenêtre
    global fenetre
    fenetre = tk.Tk()
    fenetre.title("WolfGPT")

    # Réduire la largeur de la fenêtre avec le texte
    fenetre.geometry("1200x700")  # Largeur x Hauteur

    # Diviser la fenêtre en deux parties (gauche et droite)
    global left_frame
    left_frame = tk.Frame(fenetre)
    global right_frame
    right_frame = tk.Frame(fenetre)

    setup_right(right_frame)

    fenetre.configure(bg="grey")

    left_frame.pack(side=tk.LEFT, padx=10)
    right_frame.pack(side=tk.RIGHT, padx=10, fill=tk.BOTH, expand=True)

    # Créer un canevas pour dessiner les cercles dans la partie gauche
    global canvas
    canvas = tk.Canvas(left_frame, width=window_size[0], height=window_size[0])
    canvas.configure(bg="grey")
    canvas.pack()
    #draw_circles_with_names_and_images(canvas)

    # Démarrer la fenêtre principale
    #fenetre.mainloop()




