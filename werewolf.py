with open("gpt.py") as f:
    exec(f.read())
from colorama import Fore, Back, Style
from datetime import datetime
import os

print(Fore.WHITE)

gameRoles = []
gameRoles.extend(["Villager"] * 2)
gameRoles.extend(["Seer"] * 1)
gameRoles.extend(["Werewolf"] * 1)

now = datetime.now()
dt_string = now.strftime("%d_%m_%Y_%H_%M_%S")
partyId = dt_string

players = []
playerByRole = {}
for role in gameRoles:
    playerByRole[role] = []


def addDisplayText(text):
    print(text)


class Player:
    def __init__(self, name, color, role,prepromtPath):
     self.name = name
     self.color = color
     self.role = role
     self.personalPrompt = "Your name is " + self.name + " and your role is " + self.role
     self.gpt = GptAgent(self.name,self.color,prepromtPath,self.personalPrompt)
     
    def saveData(self):
        if not os.path.exists(partyId):
            os.mkdir(partyId)
        f = open(partyId + "/" + self.name + ".txt","x")
        f.write(contextToStr(self.gpt.context))
        f.close()

def createPlayer(name,color,role):
    player = Player(name,color,role,"player_prompt.txt")
    players.append(player)
    playerByRole[role].append(player)
    return player
     
   
def playerTalk(player,text):
     addDisplayText(player.name + " : " + text)
     
def getRandomRole():
     roleId = random.randint(0,len(gameRoles)-1)
     return gameRoles.pop(roleId)

def printPlayers():
     for key in playerByRole:
         print(key + " :")
         for player in playerByRole[key]:
             print(" > " + player.name)

def initPlayers():
     for player in players:
          prompt = "The players are : "
          for p in players:
               if player.name != p.name:
                    prompt += p.name + ","
          prompt += " and yourself"
          player.gpt.addContext(prompt)
        
def recoverPlayers(text):
    res = []
    start = 0
    #while start < len(text) and text[start] != ':':
    #    start += 1

    for i in range(len(players)):
        if text.find(players[i].name,start,len(text)) != -1:
            res.append(i)

    return res            

def gameMasterTell(text):
     gameMasterTellTo(text,players)

def gameMasterTellTo(text,playersToTalk):
     prompt = "GameMaster : " + text
     addDisplayText(prompt)
     #prompt = makeRequest(prompt)
     for player in playersToTalk:
          player.gpt.addContext(prompt)

def playSeer():
     gameMasterTell("Seer, please tell me the name of the player you would like to know the role")
     
     answer = playerByRole["Seer"][0].gpt.talk()
     playerTalk(playerByRole["Seer"][0],answer)
     
     requested = recoverPlayers(answer)
     requested = requested[0]
     
     gameMasterTellTo("Their role is : " + players[requested].role,playerByRole["Seer"])
 
def playWerewolf():
    return
         
def playRole(role):
     gameMasterTell("The " + role + " wakes up.")
     
     if role == "Seer":
     	playSeer()
     elif role == "Werewolf":
     	playWerewolf()
     	
     gameMasterTell("The " + role + " fall back asleep.")

createPlayer("Bob",[255,50,50],getRandomRole())
createPlayer("Alice",[150,150,255],getRandomRole())
createPlayer("Adele",[255,150,150],getRandomRole())
createPlayer("Normy",[75,255,75],getRandomRole())

print("Party ID : " + partyId)
printPlayers()
initPlayers()

gameMasterTell("The city fall asleep !")
playRole("Seer")


for player in players:
     player.saveData()













