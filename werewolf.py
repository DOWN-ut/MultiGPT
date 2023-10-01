with open("gpt.py") as f:
    exec(f.read())
from colorama import Fore, Back, Style
from datetime import datetime
from collections import Counter
import os

print(Fore.WHITE)

#----------- GAME RULES ----------------

villagerCount = 2
seerCount = 1
werewolfCount = 2

#----------- PROMPTS DISPLAYS AND SETUPS ----------------

startPrompt = "Start of the party :"

gameMasterColor = [0,0,0]

werewolfConvLength = 3

rolesPrompt = "The roles are : "
rolesPrompt += str(villagerCount) + " villagers , "
rolesPrompt += str(seerCount) + " seers "
rolesPrompt += "and " + str(werewolfCount) + " werewolves."

gameRoles = []
gameRoles.extend(["Villager"] * villagerCount)
gameRoles.extend(["Seer"] * seerCount)
gameRoles.extend(["Werewolf"] * werewolfCount)

mainLog = ""

now = datetime.now()
dt_string = now.strftime("%d_%m_%Y_%H_%M_%S")
partyId = dt_string

players = []
playerByRole = {}
for role in gameRoles:
    playerByRole[role] = []

#Dictionary of all killed players during a night, by role ; syntaxe dict[role(string)] --> players[](Player)
nightKillInit = {}
for role in gameRoles:
    nightKillInit[role] = []
nightKills = {}
nightKillCount = 0
def resetNightKills():
    global nightKills
    nightKills = nightKillInit.copy()
    global nightKillCount
    nightKillCount = 0


def addDisplayText(text,color):
    global mainLog 
    mainLog += text + "\n_\n"
    print(text)

def contextToFile(player,context):
    text = ""
    for c in context:
        text +=  c["content"] + "\n_\n"
    return text

def initLogSaves():
    if not os.path.exists(partyId):
        os.mkdir(partyId)

def saveLogs():
    f = open(partyId + "/party.txt","x")
    f.write(mainLog)
    f.close()       

    for player in players:
        player.saveData()
    

class Player:
    def __init__(self, name, color, role,prepromtPath):
     self.name = name
     self.color = color
     self.role = role
     self.personalPrompt = "Your name is " + self.name + " and your role is " + self.role
     self.gpt = GptAgent(self.name,self.color,prepromtPath,self.personalPrompt)
     
    def saveData(self):
        f = open(partyId + "/" + self.name + ".txt","x")
        f.write(contextToFile(self,self.gpt.context))
        f.close()

    def die(self,killerRole):
        self.gpt.addContext("You were killed by " + killerRole)
        self.saveData()

def eliminatePlayer(player,killerRole):
    players.remove(player)
    playerByRole[player.role].remove(player)
    player.die(killerRole)

def createPlayer(name,color,role):
    player = Player(name,color,role,"player_prompt.txt")
    players.append(player)
    playerByRole[role].append(player)
    return player

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
        prompt = rolesPrompt
        prompt += "\nThe players are : "
        for p in players:
            if player.name != p.name:
                prompt += p.name + ","
        prompt += " and yourself"
        prompt += "\n" + startPrompt
        player.gpt.addContext(prompt)
        
def recoverPlayersFromAnswers(answers):
    res = []
    for answer in answers:
        res.extend(recoverPlayersFromAnswer(answer))
    return res

def recoverPlayersFromAnswer(text):
    res = []
    start = 0
    #while start < len(text) and text[start] != ':':
    #    start += 1

    for i in range(len(players)):
        if text.find(players[i].name,start,len(text)) != -1:
            res.append(i)

    return res            

#####------------ CONVERSATIONS ----------------------

def tellTo(prompt,playersToTalk):
    for player in playersToTalk:
        player.gpt.addContext(prompt)
        
def playerTalk(player,text):
    return playerTalkTo(player,text,players)
   
def playerTalkTo(player,text,playersToTalk):
    prompt = player.name + " : " + text
    ptt = [p for p in playersToTalk if p != player]
    tellTo(prompt,ptt)
    addDisplayText(prompt,player.color)

def gameMasterTell(text):
    gameMasterTellTo(text,players)

def gameMasterTellTo(text,playersToTalk):
    prompt = "GameMaster : " + text
    tellTo(prompt,playersToTalk) 
    addDisplayText(prompt,gameMasterColor)


#####------------ ACTIONS ----------------------


def roleKillPlayer(playerKilled,role):
    global nightKills
    nightKills[role].append(playerKilled)
    global nightKillCount
    nightKillCount += 1


#####------------ ROLES ----------------------

def playSeer():
    gameMasterTell("Seer, please tell me the name of the player you would like to know the role")
     
    answer = playerByRole["Seer"][0].gpt.talk()
    playerTalkTo(playerByRole["Seer"][0],answer,[])
     
    requested = recoverPlayersFromAnswer(answer)
    requested = requested[0]
     
    gameMasterTellTo("Their role is : " + players[requested].role,playerByRole["Seer"])
 
def playWerewolf():
    gameMasterTell("Werewolves, please choose and agree on the name of the player you want to kill tonight")

    for player in playerByRole["Werewolf"]:
        prompt = "The other werewolves are : "
        for w in playerByRole["Werewolf"]:
            if w != player:
                prompt += w.name + ","
        prompt += ". So you should not vote against them"
        player.gpt.addContext(prompt)
        player.gpt.addContextFromFile("werewolf_turn.txt")

    choices = []
    for i in range(0,werewolfConvLength):    
        choices = []
        for player in playerByRole["Werewolf"]:
            answer = player.gpt.talk()
            choices.extend(recoverPlayersFromAnswer(answer))
            playerTalkTo(player,answer,playerByRole["Werewolf"])
        if all(i == choices[0] for i in choices):
            break

    #print(choices)
    #choices = recoverPlayersFromAnswers(choices)
    #print(choices)
    choice = Counter(choices).most_common(1)[0][0]
    choice = players[choice]
    #print(choice.name)

    roleKillPlayer(choice,"Werewolf")

    gameMasterTellTo("You agreed to kill " + choice.name,playerByRole["Werewolf"])

    return choice
         
def playRole(role):
    gameMasterTell("The " + role + " wakes up.")
     
    if role == "Seer":
        playSeer()
    elif role == "Werewolf":
        global nightKill
        nightKill.append(playWerewolf())
     	
    gameMasterTell("The " + role + " fall back asleep.")


#####------------ PARTY ----------------------

def applyKills():
    for key in nightKills:
        for player in nightKills[key]:
            eliminatePlayer(player,key)

def morningAnnouncement():
    if nightKillCount <= 0:
        gameMasterTell("No body died last night !")
    else:
        for key in nightKills:
            count = len(nightKills[key])
            if count <= 0:
                #gameMasterTell(key + " didn't kill anyone last night.")
                abcd=1 #dummy instruction to make python happy
            else:
                gameMasterTell(key + " killed " + str(count) + " players last night !")
                prompt = "They killed "
                for i in range(len(nightKills[key])):
                    player = nightKills[key][i]
                    if i < len(nightKills[key])-2:
                        prompt += player.name + ", "
                    elif i == len(nightKills[key])-2:
                        prompt += player.name + " and "
                    else:
                        prompt += player.name
                gameMasterTell(prompt + ".")

def partyTurn():
    resetNightKills()

    gameMasterTell("The city fall asleep !")

    #playRole("Seer")

    #playRole("Werewolf"))
    roleKillPlayer(players[0],"Werewolf")
    roleKillPlayer(players[3],"Werewolf")

    applyKills()
    
    gameMasterTell("The city wakes up !")

    morningAnnouncement()

createPlayer("Bob",[255,50,50],getRandomRole())
createPlayer("Alice",[150,150,255],getRandomRole())
createPlayer("Adele",[255,150,150],getRandomRole())
createPlayer("Normy",[75,255,75],getRandomRole())
createPlayer("Arthur",[255,50,255],getRandomRole())

print("Party ID : " + partyId)
printPlayers()
initPlayers()
initLogSaves()

partyTurn()

saveLogs()













