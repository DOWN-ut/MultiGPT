with open("gpt.py") as f:
    exec(f.read())
from colorama import Fore, Back, Style

print(Fore.WHITE)

gameRoles = []
gameRoles.extend(["Villager"] * 2)
gameRoles.extend(["Seer"] * 1)
gameRoles.extend(["Werewolf"] * 1)

players = []

class Player:
    def __init__(self, name, color, role,prepromtPath):
     self.name = name
     self.color = color
     self.role = role
     self.personalPrompt = "Your name is " + self.name + " and your role is " + self.role
     self.gpt = GptAgent(self.name,self.color,prepromtPath,self.personalPrompt)

def getRandomRole():
     roleId = random.randint(0,len(gameRoles)-1)
     return gameRoles.pop(roleId)

def printPlayers():
     for player in players:
          print(player.name + " is " + player.role)

def gameMasterTell(text):
     prompt = "GameMaster : " + text
     prompt = makeRequest(prompt)
     for player in players:
          player.gpt.addContext(prompt)

def playRole(role):
     gameMasterTell("The " + role + " wake ups.")

     gameMasterTell("The " + role + " fall back asleep.")

players.append(Player("Bob",[255,50,50],getRandomRole(),"player_prompt.txt"))
players.append(Player("Alice",[150,150,255],getRandomRole(),"player_prompt.txt"))
players.append(Player("Adele",[255,150,150],getRandomRole(),"player_prompt.txt"))
players.append(Player("Normy",[75,255,75],getRandomRole(),"player_prompt.txt"))

#printPlayers()


gameMasterTell("The city fall asleep !")
playRole("Seer")