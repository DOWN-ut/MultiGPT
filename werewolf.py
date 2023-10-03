with open("gpt.py") as f:
    exec(f.read())
with open("pygame_main2.py") as f:
    exec(f.read())
from colorama import Fore, Back, Style
from datetime import datetime
from collections import Counter
import os
import time

print(Fore.WHITE)

#----------- GAME RULES ----------------

villagerCount = 3
seerCount = 1
werewolfCount = 2

#----------- PROMPTS DISPLAYS AND SETUPS ----------------

startPrompt = "Start of the party :"

gameMasterColor = [0,0,0]

werewolfConvLength = 3
debatLengthPerPlayer = 3 #mutliplied by the number of remaining players
dayVoteLength = 1

rolesPrompt = "*The roles are : "
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


def conversationTalk(playerId,agents,text):
    #addDisplayPlayerText(players[playerId],text)
    playerTalk(players[playerId],text)

def addDisplayPlayerText(player,text):
    text = player.name + " : " + text
    addDisplayText(text,player.color)
    addAMessage(player.name,text)

def addDisplayerGMText(text):
    addDisplayText(text,gameMasterColor)
    addAMessage("Game Master",text)

def addDisplayText(text,color):
    global mainLog 
    mainLog += text + "\n_\n"
    print(text)

def contextToFile(player,context):
    text = ""
    for c in context:
        if c["content"][0] != "*":
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
     self.displayer = PlayerDisplayer(name,role,color,0)
     playerDisplayers.append(self.displayer)
     
    def place(self,id):
        self.displayer.position = id * (360.0 / len(players))

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
    i = 0
    for player in players:
        prompt = rolesPrompt
        prompt += "\nThe players are : "
        for p in players:
            if player.name != p.name:
                prompt += p.name + ","
        prompt += " and yourself"
        prompt += "\n" + startPrompt
        player.gpt.addContext(prompt)

        player.place(i)
        i += 1
        
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
    addDisplayerGMText(prompt)

def voteConversation(playersVoting,convLength):
    choices = []
    for i in range(0,convLength):    
        choices = []
        for player in playersVoting:
            answer = player.gpt.talk()
            choices.extend(recoverPlayersFromAnswer(answer))
            playerTalkTo(player,answer,playersVoting)
        if all(i == choices[0] for i in choices):
            break

    choice = Counter(choices).most_common(1)[0][0]
    return choice

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
    
    time.sleep(1)
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

    choice = voteConversation(playerByRole["Werewolf"],werewolfConvLength)
    choice = players[choice]

    roleKillPlayer(choice,"Werewolf")

    time.sleep(1)
    gameMasterTellTo("You agreed to kill " + choice.name,playerByRole["Werewolf"])

    return choice
         
def playRole(role):
    gameMasterTell("The " + role + " wakes up.")
     
    if role == "Seer":
        playSeer()
    elif role == "Werewolf":
        playWerewolf()
     	
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

def dayDebate():
    gpts = [player.gpt for player in players]

    for player in players:
        player.gpt.addContextFromFile("debate_turn.txt")

    dl = debatLengthPerPlayer * len(players) 
    conversation(3,dl,gpts,"*Start the debate and give your opinion")

    time.sleep(1)
    gameMasterTell("Now is time to vote ! Designate the player you want to eliminate.")
    for player in players:
        player.gpt.addContextFromFile("vote_turn.txt")

    choice = voteConversation(players,dayVoteLength)
    choice = players[choice]

    time.sleep(1)
    gameMasterTell("You agreed to eliminate " + choice.name)


def partyTurn(turn):
    resetNightKills()

    gameMasterTell("The city fall asleep !")

    time.sleep(1)
    playRole("Seer")

    time.sleep(1)
    playRole("Werewolf")
    #roleKillPlayer(players[0],"Werewolf")
    #roleKillPlayer(players[3],"Werewolf")

    applyKills()

    time.sleep(1)
    gameMasterTell("The city wakes up ! This is the " + str(turn) + "th day.")

    time.sleep(1)
    morningAnnouncement()

    time.sleep(1)
    gameMasterTell("Now is time to debate before voting for someone to kill.")

    time.sleep(1)
    dayDebate()

createPlayer("Bob",[255,50,50],getRandomRole())
createPlayer("Alice",[255,255,50],getRandomRole())
createPlayer("Adele",[75,255,75],getRandomRole())
createPlayer("Normy",[255,50,255],getRandomRole())
createPlayer("Arthur",[50,255,255],getRandomRole())
createPlayer("Lea",[50,150,50],getRandomRole())

print("Party ID : " + partyId)
printPlayers()
initPlayers()
initLogSaves()

#agents = [player.gpt for player in players]
#txt = "Adele : I think Arthur is a werewolf. What's your opinion Normy ? Are you suspicious Normy ?? Also, i heard Arthur move... What the fuck were you doing Arthur ??"
#ints = recoverInterlocutors(txt,agents)
#displayRawInterlocutors(ints,agents)
#ints = processInterlocutors(ints,[i for i in range(len(agents))],3)
#displayInterlocutors(ints,agents)

#partyTurn(1)

setup_window()

for actTime in range(500):
    display_game(actTime / 500.0)
    time.sleep(0.01)
    actTime += 1
    if actTime % 100 == 0:
        i = actTime / 100
        addDisplayPlayerText(players[int(i)],"Hello everyone !")


#saveLogs()













