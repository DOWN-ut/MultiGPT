import tkinter as tk
from tkinter import scrolledtext
from tkinter import PhotoImage
import math
import random
import time

# Données de la conversationPannel
messagesList = []

gameMasterColor = [220,220,220]

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
headImages["Dead"] = "images/grave.png"

playerDisplayers = []

window_size = (800,700)
right_frame = ""
left_frame = ""
conversationPannel = ""
canvas = ""
fenetre = ""

def addAMessage(playerName, message):
    conversationPannel.config(state=tk.NORMAL)  # Activer l'édition
    conversationPannel.insert(tk.END, f"{playerName} : {message}\n", playerName)
    conversationPannel.config(state=tk.DISABLED)  # Désactiver l'édition
    conversationPannel.yview(tk.END) # Faire défiler vers le bas
    #messagesList.append({"name": player, "text": message})
    fenetre.update()

def colorOf(rgb):
    return "#{:02X}{:02X}{:02X}".format(rgb[0],rgb[1],rgb[2])

sleepColor = [0,0,0]

player_circle_distance = 300
player_card_distance = 225
player_name_distance = 375
player_death_distance = 340


# Créez une liste pour stocker les objets PhotoImage
image_list = []

def mul(v1,f):
    return (v1[0] * f, v1[1] * f)

def window_center():
    return (window_size[0] * 0.5, window_size[1] * 0.5)

def draw_gamemaster(canvas):
    draw_circle(canvas,(0,0),75,gameMasterColor)
    draw_text(canvas,(0,0),"Game Master",[50,50,50])

def draw_player(canvas,player):
    direction = (math.cos(math.radians(player.position)),math.sin(math.radians(player.position)))
    circle_position = mul(direction,player_circle_distance)
    card_position = mul(direction,player_card_distance)
    name_position = mul(direction,player_name_distance)
    death_position = mul(direction,player_death_distance)

    if player.dead:
        draw_head(canvas,circle_position,"Dead")
    else:
        if player.state == "Sleep":
            draw_circle(canvas,circle_position,55,sleepColor)
        draw_head(canvas,circle_position,player.state)     
        

    draw_text_rect(canvas,name_position,(len(player.name)*10,15))
    draw_text(canvas,name_position,player.name,player.color)
    draw_card(canvas,card_position,player.role)

    if player.damocles and not player.dead:
        draw_damocles(canvas,death_position)

    #draw_talkBubble(canvas,player)

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

def draw_text(canvas,position,txt,color): 
    canvas.create_text(position[0] + window_center()[0],position[1] + window_center()[1], text=txt,fill=colorOf(color))

def draw_text_rect(canvas,position,size):
    rx = window_center()[0] + position[0]
    ry = window_center()[1] + position[1]
    canvas.create_rectangle(rx - (size[0] * 0.5),ry - (size[1] * 0.5),rx + (size[0] * 0.5),ry + (size[1] * 0.5), fill="black")

def draw_card(canvas,center,role):
    image_path = roleImages[role]
    image = PhotoImage(file=image_path)  # Charger l'image
    image = image.subsample(9,9)
    image_list.append(image)  # Ajouter l'image à la liste
    canvas.create_image(window_center()[0] + center[0], window_center()[1] + center[1] - 20, anchor=tk.N, image=image)

def draw_damocles(canvas,center):
    image_path = "images/death.png"
    image = PhotoImage(file=image_path)  # Charger l'image
    image = image.subsample(16,16)
    image_list.append(image)  # Ajouter l'image à la liste
    canvas.create_image(window_center()[0] + center[0], window_center()[1] + center[1] - 10, anchor=tk.N, image=image)

def draw_talkBubble(canvas,player):
    direction = (math.cos(math.radians(player.position)),math.sin(math.radians(player.position)))
    position = mul(direction,player_bubble_distance)



class PlayerDisplayer:
    def __init__(self,name,role,color,position):
        self.name = name
        self.color = color
        self.role = role
        self.color = color
        self.position = position
        self.state = "Neutral"
        self.damocles = False
        self.dead = False
        playerDisplayers.append(self)

    def setDead(self,d):
        self.dead = d

    def setState(self,s):
        self.state = s
    

def setup_right(right_frame):
    # Créer un widget Texte défilant pour la conversationPannel dans la partie droite
    global conversationPannel
    conversationPannel = scrolledtext.ScrolledText(right_frame, wrap=tk.WORD, state=tk.DISABLED, width=30)
    conversationPannel.pack(fill=tk.BOTH, expand=True)
    conversationPannel.configure(bg="#262626")

    conversationPannel.tag_configure("GameMaster", foreground=colorOf(gameMasterColor), spacing1=10, spacing2=5, lmargin1=10)
    for playerd in playerDisplayers:
        conversationPannel.tag_configure(playerd.name, foreground=colorOf(playerd.color), spacing1=10, spacing2=5, lmargin1=10)


def display_game():
    
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
    fenetre.geometry("1500x700")  # Largeur x Hauteur

    # Diviser la fenêtre en deux parties (gauche et droite)
    global left_frame
    left_frame = tk.Frame(fenetre,relief="flat", borderwidth=0, highlightthickness=0)
    global right_frame
    right_frame = tk.Frame(fenetre,relief="flat", borderwidth=0, highlightthickness=0)

    setup_right(right_frame)

    fenetre.configure(bg="#262626")

    left_frame.pack(side=tk.LEFT, padx=5)
    right_frame.pack(side=tk.RIGHT, padx=10, fill=tk.BOTH, expand=True)

    # Créer un canevas pour dessiner les cercles dans la partie gauche
    global canvas
    canvas = tk.Canvas(left_frame, width=window_size[0], height=window_size[0])
    canvas.configure(bg="grey")
    canvas.pack()
    #draw_circles_with_names_and_images(canvas)

    # Démarrer la fenêtre principale
    #fenetre.mainloop()
