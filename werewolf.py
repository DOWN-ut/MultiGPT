with open("gpt.py") as f:
    exec(f.read())
with open("pygame_main2.py") as f:
    exec(f.read())
with open("tts.py") as f:
    exec(f.read())
from colorama import Fore, Back, Style
from datetime import datetime
from collections import Counter
import os
import time
import sys 

print(Fore.WHITE)

#----------- GAME RULES ----------------

villagerCount = 2
seerCount = 1
werewolfCount = 2
witchCount = 1

#----------- PROMPTS DISPLAYS AND SETUPS ----------------

startPrompt = "Start of the party :"

werewolfConvLength = 3
debatLengthPerPlayer = 1.5 #mutliplied by the number of remaining players
dayVoteLength = 1

rolesPrompt = "*The roles are : "
rolesPrompt += str(villagerCount) + " villagers , "
rolesPrompt += str(seerCount) + " seers "
rolesPrompt += "and " + str(werewolfCount) + " werewolves."

allGameRoles = ["Village","Werewolf","Seer","Witch"]

gameRoles = []
gameRoles.extend(["Villager"] * villagerCount)
gameRoles.extend(["Seer"] * seerCount)
gameRoles.extend(["Werewolf"] * werewolfCount)
gameRoles.extend(["Witch"] * witchCount)

mainLog = ""

now = datetime.now()
dt_string = now.strftime("%d_%m_%Y_%H_%M_%S")
partyId = dt_string

players = []
playerByRole = {}
for role in gameRoles:
    playerByRole[role] = []

#Dictionnary of the role's powers and their usage
rolePowers = {}
rolePowers["Witch"] = {}
rolePowers["Witch"]["Life"] = True
rolePowers["Witch"]["Death"] = True
 
#Dictionary of all killed players during a night, by role ; syntaxe dict[role(string)] --> players[](Player)
nightKills = {}
nightKillCount = 0

enable_audio = False
audioCount = 0
voices = {}
voices["GameMaster"] = "en-US-News-N"

speedRun = False

replaying = False
partyData = []
replayIndex = 0
replayAudioIndex = 0
replayPlayersRoles = []

def resetNightKills():
    global nightKills
    nightKills = {}
    for role in allGameRoles:
        nightKills[role] = []
    global nightKillCount
    nightKillCount = 0

def updateGame(delay = -1):
    display_game()
    if delay == -1:
        if not enable_audio :
            time.sleep(2)
        else:
            time.sleep(0)
    else:
        time.sleep(delay)

def replayAudio(index):
    path = partyId + "/" + str(index) + ".wav"
    if os.path.isfile(path):
        playsound(path)
        return True
    else:
        return False

def speak(player,text):
    if not enable_audio:
        return
    global audioCount
    global replayAudioIndex
    path = f"./{partyId}/{audioCount}.wav"
    audioCount += 1
    if isinstance(player,str):
        if replaying:
            if not replayAudio(replayAudioIndex):
                makeSpeech(voices[player],text,path)
        else:
            makeSpeech(voices[player],text,path)
    else:
        if replaying:
            if not replayAudio(replayAudioIndex):
                makeSpeech(player.voice,text,path)
        else:
            makeSpeech(player.voice,text,path)
    replayAudioIndex += 1


def conversationTalk(playerId,agents,text):
    #addDisplayPlayerText(players[playerId],text)
    playerTalk(players[playerId],text)

def addDisplayPlayerText(player,text):
    addDisplayText(player.name + " : " + text)
    addAMessage(player.name,text)
    speak(player,text)

def addDisplayerGMText(text):
    addDisplayText("GameMaster : " + text)
    addAMessage("GameMaster",text)
    speak("GameMaster",text)

def addDisplayText(text):
    global mainLog 
    mainLog += text + "\n_\n"
    print(text)

def contextToFile(player,context):
    text = ""
    for c in context:
        if len(c["content"]) > 0:
            if c["content"][0] != "*":
                text +=  c["content"] + "\n_\n"
    return text

def initLogSaves():
    if not os.path.exists(partyId):
        os.mkdir(partyId)

def initMainLog():
    global mainLog
    for player in players:
        mainLog += player.role + " "
    mainLog += "\n_\n"

def saveLogs():
    f = open(partyId + "/party.txt","x")
    f.write(mainLog)
    f.close()       

    for player in players:
        player.saveData()
    
def loadParty(path):
    global partyData
    global replayIndex
    global replayPlayersRoles
    partyData = open(path, "r").read().split('_')
    replayPlayersRoles = partyData[0].split(" ")
    for i in range(len(replayPlayersRoles)):
        replayPlayersRoles[i] = replayPlayersRoles[i].replace("\n","")
    replayIndex = 1

def readPartyLine(index):
    if index >= len(partyData):
        return False

    line = partyData[index]
    line = line[1:-1]
    if len(line) <= 0:
        return False

    if line[0] == '>':
        action = line.split(" ")[1]
        target = line.split(" ")[2].replace("\n","")
        print("Action : " + action + "  " + target)
        if action == "damocles":
            getPlayerByName(target).setDamocles(True)
        elif action == "undamocles":
            getPlayerByName(target).setDamocles(False)
        elif action == "kill":
            getPlayerByName(target).die("Werewolf")
        elif action == "sleep":
            if target == "all":
                sleepAll()
            else:
                sleep(getPlayerByName(target))
        elif action == "wake":
            if target == "all":
                wakeAll()
            else:
                wake(getPlayerByName(target))
    else:
        interlo = line.split(":",1)[0].replace(" ","")
        text = line.split(":",1)[1]
        if interlo == "GameMaster":
            addDisplayerGMText(text)
        else:
            addDisplayPlayerText(getPlayerByName(interlo),text)


    return True

class Player:
    def __init__(self, name, color,voice,perso, role,prepromtPath):
     self.name = name
     self.color = color
     self.voice = voice
     self.role = role
     self.state = "Neutral"
     self.perso = perso
     self.damocles = False
     self.personalPrompt = "Your name is " + self.name + " and your role is " + self.role + "\n"
     self.personalPrompt += open("prompts/"+self.perso, "r").read()
     self.gpt = GptAgent(self.name,self.color,prepromtPath,self.personalPrompt)
     self.displayer = PlayerDisplayer(name,role,color,0)
     
    def setState(self,state):
        self.state = state
        self.displayer.setState(state) 
    
    def setDamocles(self,v):
        self.damocles = v
        self.displayer.damocles = v

    def place(self,id):
        self.displayer.position = id * (360.0 / len(players))

    def saveData(self):
        f = open(partyId + "/" + self.name + ".txt","x")
        f.write(contextToFile(self,self.gpt.context))
        f.close()

    def die(self,killerRole):
        self.gpt.addContext("You were killed by " + killerRole)
        self.displayer.setDead(True)
        if not replaying :
            self.saveData()

def eliminatePlayer(player,killerRole):
    print("Removing " + player.name + " from ")
    #print(players)
    if player in players:
        players.remove(player)
    if player in playerByRole[player.role]:
        playerByRole[player.role].remove(player)
    player.die(killerRole)
    global mainLog
    mainLog += "> kill " + player.name + "\n_\n"

def createPlayer(name,color,voice,perso,role):
    player = Player(name,color,voice,perso,role,"player_prompt.txt")
    players.append(player)
    playerByRole[role].append(player)
    return player

def getPlayerByName(name):
    for player in players:
        if player.name == name:
            return player
    return None

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
    text = filterAnwser(text)
    prompt = player.name + " : " + text
    ptt = [p for p in playersToTalk if p != player]
    tellTo(prompt,ptt)
    addDisplayPlayerText(player,text)

def gameMasterTell(text):
    gameMasterTellTo(text,players)

def gameMasterTellTo(text,playersToTalk):
    prompt = "GameMaster : " + text
    tellTo(prompt,playersToTalk) 
    addDisplayerGMText(text)

def voteConversation(playersVoting,convLength):
    choices = []
    for i in range(0,convLength):    
        choices = []
        for player in playersVoting:
            answer = player.gpt.tell("*"+player.name + " : ")#talk()
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
    playerKilled.setDamocles(True)
    global nightKillCount
    nightKillCount += 1
    global mainLog
    mainLog += "> damocles " + playerKilled.name + "\n_\n"

def removeKillFromRole(playerKilled,role):
    global nightKills
    nightKills[role].remove(playerKilled)
    playerKilled.setDamocles(False)
    global nightKillCount
    nightKillCount -= 1
    global mainLog
    mainLog += "> undamocles " + playerKilled.name + "\n_\n"

def sleep(player):
    player.setState("Sleep")
    global mainLog
    mainLog += "> sleep " + player.name + "\n_\n"

def sleepSome(playerToSleep):
    for player in playerToSleep:
        sleep(player)
    
def sleepAll():
    sleepSome(players)

def wake(player):
    if player.state == "Sleep":
        player.setState("Neutral")
        global mainLog
        mainLog += "> wake " + player.name + "\n_\n"

def wakeSome(playerToWake):
    for player in playerToWake:
        wake(player)

def wakeAll():
    wakeSome(players)

#####------------ ROLES ----------------------

def playWitch():
    if len(playerByRole["Witch"]) <= 0:
        return
    
    gameMasterTell("Witch, the victim is: " + nightKills.get("Werewolf")[-1].name)
    updateGame()
    gameMasterTell("Do you wish to : let it die, save it or kill someone else ?")
    updateGame()

    # add prompt to give more explanations
    if rolePowers["Witch"]["Life"] and rolePowers["Witch"]["Death"]:
        print(">                           Witch both")
        playerByRole["Witch"][0].gpt.addContextFromFile("witch_turn_both.txt")
    elif rolePowers["Witch"]["Life"]:
        print(">                           Witch life")
        playerByRole["Witch"][0].gpt.addContextFromFile("witch_turn_life.txt")
    elif rolePowers["Witch"]["Death"]:
        print(">                           Witch death")
        playerByRole["Witch"][0].gpt.addContextFromFile("witch_turn_death.txt")

    answer = playerByRole["Witch"][0].gpt.talk()
    playerTalkTo(playerByRole["Witch"][0], answer, [])
    updateGame()

    requested = recoverPlayersFromAnswer(answer)
    if 0 < len(requested):
        requested = requested[0]
        if "kill" in answer and rolePowers["Witch"]["Death"]:
            #nightKills["Witch"].append(players[requested[0]])
            rolePowers["Witch"]["Death"] = False
            roleKillPlayer(players[requested],"Witch")
        elif "save" in answer and rolePowers["Witch"]["Life"]:
            #nightKills["Werewolf"].pop()
            rolePowers["Witch"]["Life"] = False
            removeKillFromRole(players[requested],"Werewolf")
    updateGame()

    #print(nightKills)

def playSeer():
    if len(playerByRole["Seer"]) <= 0:
        return
    
    gameMasterTell("Seer, please tell me the name of the player you would like to know the role")
    updateGame()

    answer = playerByRole["Seer"][0].gpt.talk()
    playerTalkTo(playerByRole["Seer"][0],answer,[])  
    requested = recoverPlayersFromAnswer(answer)
    if len(requested) > 0:
        requested = requested[0]
        updateGame()
        gameMasterTellTo("Their role is : " + players[requested].role,playerByRole["Seer"])

    updateGame()
 
def playWerewolf():
    if len(playerByRole["Werewolf"]) <= 0:
        return
    
    gameMasterTell("Werewolves, please choose and agree on the name of the player you want to kill tonight")
    updateGame()

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

    updateGame()
    gameMasterTellTo("You agreed to kill " + choice.name,playerByRole["Werewolf"])

    updateGame()
    return choice
         
def playRole(role):
    gameMasterTell("The " + role + " wakes up.")
    wakeSome(playerByRole[role])
    updateGame()

    if role == "Seer":
        playSeer()
    elif role == "Werewolf":
        playWerewolf()
    elif role == "Witch":
        playWitch()
     	
    gameMasterTell("The " + role + " fall(s) back asleep.")
    sleepSome(playerByRole[role])
    updateGame()

#####------------ PARTY ----------------------

def villageWin():
    addDisplayerGMText("The village wins !")

def werewolvesWin():
    addDisplayerGMText("The werewolves wins !")

def applyKills():
    print(players)
    for key in nightKills:
        for player in nightKills[key]:
            eliminatePlayer(player,key)

def morningAnnouncement():
    if nightKillCount <= 0:
        gameMasterTell("No body died last night !")
    else:
        gameMasterTell(str(nightKillCount) + " players died last night :")
        allDeath = ""
        for key in nightKills:
            if len(nightKills[key]) > 0:
                for p in nightKills[key]:
                    allDeath += p.name + "  "
        gameMasterTell(allDeath)
        '''for key in nightKills:
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
                gameMasterTell(prompt + ".")'''
    updateGame()

def dayDebate():
    gpts = [player.gpt for player in players]

    for player in players:
        player.gpt.addContextFromFile("debate_turn.txt")

    dl = max(5,int(debatLengthPerPlayer * len(players) * 1.5)) 
    print("We are running " + str(dl) + " convo turns : " + str(debatLengthPerPlayer) + " for each " + str(len(players)))
    conversation(2,5,dl,gpts,"*Start the debate and give your opinion",1)

    updateGame(1)

    gameMasterTell("Now is time to vote ! Designate the player you want to eliminate.")
    updateGame()

    for player in players:
        player.gpt.addContextFromFile("vote_turn.txt")

    choice = voteConversation(players,dayVoteLength)
    choice = players[choice]

    updateGame()
    gameMasterTell("You agreed to eliminate " + choice.name + ", who was a " + choice.role)
    eliminatePlayer(choice,"Everyone")
    updateGame()


def partyTurn(turn):
    resetNightKills()
    updateGame(1)

    gameMasterTell("The city falls asleep !")
    sleepAll()
    updateGame()
    
    '''roleKillPlayer(players[0],"Werewolf")
    roleKillPlayer(players[1],"Werewolf")
    roleKillPlayer(players[2],"Werewolf")
    roleKillPlayer(players[3],"Werewolf")
    applyKills()'''
    
    #roleKillPlayer(players[0],"Werewolf")

    if len(playerByRole["Seer"]) > 0:
        playRole("Seer")

    playRole("Werewolf")

    if rolePowers["Witch"]["Life"] or rolePowers["Witch"]["Death"]:
        if len(playerByRole["Witch"]) > 0:
            playRole("Witch")

    applyKills()
    
    gameMasterTell("The city wakes up ! This is the " + str(turn+1) + "th day.")
    wakeAll()
    updateGame()

    morningAnnouncement()

    if winConditionV(): 
        return
    elif winConditionW(): 
        return
    elif winConditionW2():
        return

    gameMasterTell("Now is time to debate before voting for someone to kill.")
    updateGame()

    dayDebate()

def replayParty():
    global replayIndex
    updateGame()
    while readPartyLine(replayIndex):
        updateGame()
        replayIndex += 1

def winConditionW2():
    if len(players) == 2 and len(playerByRole["Werewolf"]) == 1:
        return True
    elif len(players) == 3 and len(playerByRole["Werewolf"]) == 2:
        return True
def winConditionW():
    return len(playerByRole["Werewolf"]) == len(players)
def winConditionV():
    return len(playerByRole["Werewolf"]) <= 0

enable_audio = int(sys.argv[1])
replaying = len(sys.argv) >= 3

if replaying:    
    partyId = sys.argv[2]
    print("Loading party : " +  partyId)
    loadParty(partyId + "/party.txt")
    #print(partyData)

createPlayer("Baptiste",[255,50,50],"en-US-Neural2-A","baptiste_perso.txt",replayPlayersRoles[0] if len(replayPlayersRoles) > 0 else getRandomRole())
createPlayer("Christina",[255,255,50],"en-US-Neural2-C","christina_perso.txt",replayPlayersRoles[1] if len(replayPlayersRoles) > 0 else getRandomRole())
createPlayer("Adele",[75,255,75],"en-US-Neural2-E","adele_perso.txt",replayPlayersRoles[2] if len(replayPlayersRoles) > 0 else getRandomRole())
createPlayer("Normy",[255,50,255],"en-US-Neural2-D","normy_perso.txt",replayPlayersRoles[3] if len(replayPlayersRoles) > 0 else getRandomRole())
createPlayer("Arthur",[50,255,255],"en-US-Neural2-I","arthur_perso.txt",replayPlayersRoles[4] if len(replayPlayersRoles) > 0 else getRandomRole())
createPlayer("Lea",[50,150,50],"en-US-Neural2-H","lea_perso.txt",replayPlayersRoles[5] if len(replayPlayersRoles) > 0 else getRandomRole())
    
print("Party ID : " + partyId)

initPlayers()
if not replaying:
    initMainLog()
    initLogSaves()
    

printPlayers()
#agents = [player.gpt for player in players]
#txt = "Adele : I think Arthur is a werewolf. What's your opinion Normy ? Are you suspicious Normy ?? Also, i heard Arthur move... What the fuck were you doing Arthur ??"
#ints = recoverInterlocutors(txt,agents)
#displayRawInterlocutors(ints,agents)
#ints = processInterlocutors(ints,[i for i in range(len(agents))],3)
#displayInterlocutors(ints,agents)

setup_window()

for i in range(50):
    updateGame(0.1)

if not replaying:
    for i in range(10): 
        partyTurn(i)
        if winConditionV(): #If there is no werewolf left, the village wins
            villageWin()
            break
        elif winConditionW(): #If there is as many werewolf as players, then only the werewolves are left and they won
            werewolvesWin()
            break
        elif winConditionW2():
            werewolvesWin()
            break
else:
    replayParty()
#a = input()

#for actTime in range(500):
#    display_game(actTime / 500.0)
#    time.sleep(0.01)
#    actTime += 1
#    if actTime % 100 == 0:
#        i = actTime / 100
#        addDisplayPlayerText(players[int(i)],"Hello everyone !")

if not replaying:
    saveLogs()

a = input()













