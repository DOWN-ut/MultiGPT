import openai
from colorama import Fore, Back, Style
import random

max_response_tokens = 100


keyFile = open("key.txt", "r")
openai.api_key = keyFile.read() #open key.txt


def gptPull(context):
    chat = openai.ChatCompletion.create(
            model="gpt-3.5-turbo", 
            messages=context,
            temperature = 0.5,
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
        
    def tellFromFile(self,file):
        return self.tell(open("prompts/"+file, "r").read())

    def tell(self,request):
        self.context = gptRequest(self.context,makeRequest(request))
        return self.context[len(self.context)-1]["content"]

    def talk(self):
        self.context = gptPull(self.context)
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
        if answer.find(agents[i].name,start,len(answer)) != -1:
            res.append(i)

    return res

def displayInterlocutors(ids,agents):
    str = "    [ "
    for i in ids:
        str += agents[i].name + " "
    print(str + " ]")

def processInterlocutors(ids,allIds,coherence):
    lis = []
    for i in range(0,coherence):
        for id in ids:
            lis.append(id)
    for id in allIds:
        lis.append(id)
    return lis

def conversation(coherence):

    bob = GptAgent("Bob",Fore.YELLOW,"agent_conversation.txt","Your name is Bob.")
    alice = GptAgent("Alice",Fore.GREEN,"agent_conversation.txt","Your name is Alice.")
    adele = GptAgent("Adele",Fore.RED,"agent_conversation.txt","Your name is Adele.")
    arthur = GptAgent("Arthur",Fore.CYAN,"agent_conversation.txt","Your name is Arthur.")

    agents = [bob,alice,adele,arthur]
    answers = []
    ids = [0,1,2,3]

    agentId = random.choice(ids)
    answer = agents[agentId].tell("Say hi and introduce yourself")
    print(agents[agentId].color + answer)

    for i in range(0,5):

        answers.clear()

        interlocutors = recoverInterlocutors(answer,agents) 
        interlocutors = processInterlocutors(interlocutors,ids,coherence)
        
        while interlocutors.count(agentId) > 0:
            interlocutors.remove(agentId)

        #displayInterlocutors(interlocutors,agents)

        if len(interlocutors) <= 0:
            interlocutors.append(ids)

        agentId = random.choice(interlocutors)

        answer = agents[agentId].tell(answer)

        for a in range(0,len(agents)):
            if a != agentId :
                agents[a].addContext(answer)

        print(agents[agentId].color + answer)
        print()

    #for agent in agents:
    #    displayContexts(agent.context,1)

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
#conversation(3)
