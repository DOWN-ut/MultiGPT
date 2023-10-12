import openai
from colorama import Fore, Back, Style
import random
import math

max_response_tokens = 100


keyFile = open("key.txt", "r")
openai.api_key = keyFile.read() #open key.txt


def gptPull(context):
    chat = openai.ChatCompletion.create(
            model="gpt-3.5-turbo", 
            messages=context,
            temperature = 0.75,
            max_tokens=max_response_tokens
        )
    choices = chat.choices
    reply = choices[0].message.content
    context.append({"role":"assistant","content":reply})
    return context

def gptRequest(context,request):
    context.append(request)
    return gptPull(context)

def displayContext(context):
    color = Fore.CYAN
    if context["role"] == "user":
        color = Fore.YELLOW
    elif context["role"] == "system":
        color = Fore.GREEN
    print(color + "> " + context["content"])

def displayContexts(context,time,count=10000):
    for i in range(0,count):
        if (time + i) >= len(context):
            break
        displayContext(context[time + i])
        print("   ")
    print(Fore.WHITE)

def displayContextOf(agent,context):
    print("CONTEXT OF " + agent.name)
    displayContexts(context,1)

def makeRequest(text):
    return {"role":"user", "content":text}

def makePrePrompt(text):
    return {"role":"system", "content":text}

def contextToStr(context):
     text = ""
     for c in context:
          text += c["role"] + " : " + c["content"] + "\n\n"
     return text

class GptAgent:
    def __init__(self, name, color,prepromtPath,additionnal=""):
        self.name = name
        self.color = color
        if isinstance(prepromtPath,list):
            pp = ""
            for p in prepromtPath:
                pp += open("prompts/"+p, "r").read()
            self.prepromt = makePrePrompt(pp +"\n" + additionnal)
        else:
            self.prepromt = makePrePrompt(open("prompts/"+prepromtPath, "r").read() + "\n" + additionnal)
        self.context = [self.prepromt]
        self.lastTalked = 1
        
    def tellFromFile(self,file):
        return self.tell(open("prompts/"+file, "r").read())

    def tell(self,request):
        self.context = gptRequest(self.context,makeRequest(request))
        self.lastTalked = 1
        return self.context[len(self.context)-1]["content"]

    def talk(self):
        self.context = gptPull(self.context)
        self.lastTalked = 1
        return self.context[len(self.context)-1]["content"]

    def addContext(self,context):
        self.context.append(makeRequest(context))
    
    def addContextFromFile(self,file):
        return self.addContext(open("prompts/"+file, "r").read())

    def removeLastContext(self):
        self.context.pop()
        return

    def removeContext(self,id):
        self.context.pop(id)
        return

def readAnwsers(answers):
    requests = []
    for i in range(0, len(answers)):
        print("       < ",answers[i])
        if answers[i].find("requests",0,10):
            requests.append(i)
    return requests

def recoverInterlocutors(answer,agents):
    res = []
    start = 0
    while start < len(answer) and answer[start] != ':':
        start += 1

    for i in range(len(agents)):
        pos = start
        while True:#for pos in range(start,len(answer)):
            foundAt = answer.find(agents[i].name,pos)
            if foundAt != -1:
                ratio = float(foundAt) / float(len(answer))
                res.append((i,ratio))
                pos = foundAt + 1
            else:
                break

    return res

def displayInterlocutors(ids,agents):
    ss = "    [ "
    for id in ids:
        ss += agents[id].name + " "
    print(ss + " ]")

def displayRawInterlocutors(ids,agents):
    ss = "    [ "
    for id in ids:
        i = id[0]
        r = id[1]
        ss += agents[i].name + "(" +str(r)+") "
    print(ss + " ]")

def interlocutorProbability(positionRatio,baseProbability):
    x = positionRatio
    a = baseProbability
    y = (x*2)-1
    y *= y #((x*2)-1)²
    y /= (a+1)*(a+1)
    y += a
    return y


def processInterlocutors(ids,allIds,coherence,equality,agents):
    lis = []

    for id in ids:
        intp = interlocutorProbability(id[1],1.0/float(coherence))
        count = math.ceil(intp * coherence * (1 + (agents[id[0]].lastTalked * equality)))
        #print(str(id[0]) + " ("+str(id[1])+") " + str(intp) + " > " + str(count) )
        for i in range(count):
            lis.append(id[0])

    for id in allIds:
        lis.append(id)
    return lis

def conversationTalk(agentId,agents,text):
    for a in range(0,len(agents)):
        if a != agentId :
            agents[a].addContext(answer)
    print(agents[agentId].color + text)
    print()
    return

def conversation(coherence,equality,lenght,agents,initPrompt):
    answers = []
    ids = [i for i in range(len(agents))]

    agentId = random.choice(ids)
    answer = agents[agentId].tell(initPrompt)
    conversationTalk(agentId,agents,answer)

    for i in range(lenght-1):
        time.sleep(1)
        #print("      -  Convo turn " + str(i))
        interlocutors = recoverInterlocutors(answer,agents) 

        interlocutors = processInterlocutors(interlocutors,ids,coherence,equality,agents)

        while interlocutors.count(agentId) > 0:
            interlocutors.remove(agentId)

        if len(interlocutors) <= 0:
            interlocutors.expend(ids)

        agentId = random.choice(interlocutors)

        answer = agents[agentId].tell("*"+agents[agentId].name + " : ");#talk()
        conversationTalk(agentId,agents,answer)

        for ai in range(len(agents)):
            if ai != agentId:
                agents[ai].lastTalked += 1

        #inp = input()
        #if inp == "STOP":          
        #    for agent in agents:
        #        displayContextOf(agent,agent.context)
        #    return

def conversation_requests():

    bob = GptAgent("Bob",Fore.YELLOW,"agent_conversation_request.txt","Your name is Bob.")
    alice = GptAgent("Alice",Fore.BLUE,"agent_conversation_request.txt","Your name is Alice.")
    adele = GptAgent("Adele",Fore.RED,"agent_conversation_request.txt","Your name is Adele.")
    arthur = GptAgent("Arthur",Fore.CYAN,"agent_conversation_request.txt","Your name is Arthur.")

    agents = [bob,alice,adele,arthur]
    answers = []
    requests = []

    for agent in agents:
        awsner = agent.tell("Make a request to be allowed to talk and start the conversation.")
        answers.append(awsner)

    requests = readAnwsers(answers)

    for i in range(0,4):
        allowed = random.choice(requests)
        answers.clear()
        print("       < " , allowed)
        answer = agents[allowed].tell(agents[allowed].name + " talks.")
        print(answer)
        for a in range(0,len(agents)):
            if a != allowed :
                answers.append(agents[a].tell(answer))
            else:
                answers.append(">>")
        
        requests = readAnwsers(answers)

    for agent in agents:
        displayContexts(agent.context,1)

def passwordKeeper():
    keeper = GptAgent("Keeper",Fore.YELLOW,"password_keeper.txt")
    guesser = GptAgent("Guesser",Fore.CYAN,"password_guesser.txt")

    displayContexts(keeper.context,0,1)
    displayContexts(guesser.context,0,1)

    guesserAnswer = guesser.tell("Say hi to the keeper.")
    for i in range(0,10):
        print(guesser.color + "> " + guesserAnswer)
        print()
        keeperAnswer = keeper.tell(guesserAnswer)
        print(keeper.color + "> " + keeperAnswer)
        print()
        guesserAnswer = guesser.tell(keeperAnswer)
        if(keeperAnswer.find("ENTER")):
            break

def adeleAndArthur():
    adeleAdd = "Your name is Adele."
    adele = GptAgent("Adele",Fore.YELLOW,"agent_preprompt.txt",adeleAdd)

    arthurAdd = "Your name is Arthur.\nStart of the conversation :"
    arthur = GptAgent("Arthur",Fore.CYAN,"agent_preprompt.txt",arthurAdd)

    displayContexts(adele.context,0,1)
    displayContexts(arthur.context,0,1)

    adeleAnswer = adele.tell("Start the conversation.")
    for i in range(0,5):
        print(adele.color + "> " + adeleAnswer)
        arthurAnswer = arthur.tell(adeleAnswer)
        print(arthur.color + "> " + arthurAnswer)
        adeleAnswer = adele.tell(arthurAnswer)

    displayContexts(adele.context,0)
    displayContexts(arthur.context,0)

def test():
    time = 0
    context = [{"role": "system", "content": instructions}]

    request = makeRequest("Hello, who are you ?")
    reply = gptRequest(context,request)
    displayContexts(context,0,3)

    request = makeRequest("No you are not.")
    reply = gptRequest(context,request)
    displayContexts(context,3,2)

    print(Fore.WHITE)

#print(Fore.WHITE)
#print("----------------------------")

#conversation_requests()
bob = GptAgent("Bob",Fore.YELLOW,"agent_conversation.txt","Your name is Bob.")
alice = GptAgent("Alice",Fore.GREEN,"agent_conversation.txt","Your name is Alice.")
adele = GptAgent("Adele",Fore.RED,"agent_conversation.txt","Your name is Adele.")
arthur = GptAgent("Arthur",Fore.CYAN,"agent_conversation.txt","Your name is Arthur.")
agents = [bob,alice,adele,arthur]
#conversation(3,10,agents,"Say hi and introduce yourself")
