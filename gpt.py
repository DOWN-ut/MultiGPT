import openai
from colorama import Fore, Back, Style
import random
import math
import time
from openai import OpenAI

max_response_tokens = 100


keyFile = open("key.txt", "r")
#openai.api_key = keyFile.read() #open key.txt

client = OpenAI(
    # This is the default and can be omitted
    api_key=keyFile.read(),
)

model = "gpt-3.5-turbo"

def gptPull(context,reasoningLvl="medium"):
    while True:
        try:
            if model.startswith("gpt-3") or model.startswith("gpt-4"):
                chat = openai.ChatCompletion.create(
                        model=model, 
                        messages=context,
                        temperature = 0.85,
                        max_tokens=max_response_tokens
                    )
                choices = chat.choices
                reply = choices[0].message.content
                context.append({"role":"assistant","content":reply})
                return context
            else:
                chat = client.responses.create(
                    model=model,
                    reasoning={"effort": reasoningLvl},
                    input=context
                    #max_output_tokens = max_response_tokens
                )
                reply = chat.output_text
                context.append({"role":"assistant","content":reply})
                return context
        except Exception as error:
            print(">>>>>>>>>  OPEN AI RATE LIMIT  <<<< WAITING 5 seconds",error)
            time.sleep(5)

    return context

def gptRequest(context,request,reasoningLvl="medium"):
    context.append(request)
    return gptPull(context,reasoningLvl)

def gptComplete(context,request,reasoningLvl="medium"):
    context.append(request)
    result = gptPull(context,reasoningLvl)
    result.pop(len(result)-2)
    result[len(result)-1]["content"] = filterAnwser(result[len(result)-1]["content"])
    return result

def displayContext(context):
    color = Fore.CYAN
    if context["role"] == "user":
        color = Fore.YELLOW
    elif context["role"] == "system" or context["role"] == "developer":
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

def makeRequest(text, role="user"):
    return {"role": role, "content": text}

def makePrePrompt(text):
    return {"role":"developer", "content":text}

def contextToStr(context):
     text = ""
     for c in context:
          text += c["role"] + " : " + c["content"] + "\n\n"
     return text

class GptAgent:
    def __init__(self, name, color,prepromtPath,additionnal="", reasoningLvl="medium"):
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
        self.reasoningLvl = reasoningLvl

    def tellFromFile(self,file):
        return self.tell(open("prompts/"+file, "r").read())

    def tell(self,request):
        self.context = gptRequest(self.context,makeRequest(request),self.reasoningLvl)
        self.lastTalked = 1
        return self.context[len(self.context)-1]["content"]

    def talk(self):
        self.context = gptComplete(self.context,makeRequest(self.name + " : ")) #gptRequest(self.context,makeRequest(self.name + " : ")) #gptPull(self.context)
        self.lastTalked = 1
        #self.context[len(self.context)-1]["content"] = self.name + " : " + self.context[len(self.context)-1]["content"]
        return self.context[len(self.context)-1]["content"]

    def addContext(self,context,role="user"):
        self.context.append(makeRequest(context))
    
    def addContextFromFile(self,file,role="user"):
        return self.addContext(open("prompts/"+file, "r").read(),role)

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

def filterAnwser(text):
    pos = text.find(":",0,15)
    if pos >= 0:
        return text[pos+1:]
    else:
        return text

def recoverInterlocutors(answer,agents, lastTalked = ""):
    res = []
    start = 0
    #while start < len(answer) and answer[start] != ':':
    #    start += 1

    for i in range(len(agents)):
        pos = start
        if agents[i].name == lastTalked:
            continue
        while True:#for pos in range(start,len(answer)):
            foundAt = answer.find(agents[i].name,pos)
            if foundAt != -1:
                ratio = float(foundAt) / float(len(answer))
                res.append((i,ratio))
                pos = foundAt + 1
            else:
                break

    #print("Recovered interlocutors : ", res)
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

def gptNextInterlocutor(handlerAgent,agents):
    result = handlerAgent.tell("Who should talk next ?")
    #print("   > Handler suggests : " + result)
    result = recoverInterlocutors(result,agents)
    #print("   > Processed interlocutors : ", result)
    if(len(result) <= 0):
        print("   > No interlocutor found, choosing random one.")
        return random.choice([i for i in range(len(agents))])
    else:
        return result[0][0]

def conversationTalk(agentId,agents,text,handlerAgent = None):
    p = agents[agentId].name + " : " + text
    for a in range(0,len(agents)):
        if a != agentId :
            agents[a].addContext(p)
    if(handlerAgent != None):
        handlerAgent.addContext(p)
    print(agents[agentId].color + p)
    print()
    return

def conversation(coherence,equality,lenght,agents,initPrompt,delay=1,handlerAgent = None):
    answers = []
    ids = [i for i in range(len(agents))]

    if(handlerAgent != None):
        handlerAgent.addContext("The participants are :" + ", ".join([agent.name for agent in agents]) + ".")

    agentId = random.choice(ids)
    answer = agents[agentId].tell(initPrompt)
    conversationTalk(agentId,agents,answer,handlerAgent)

    for i in range(lenght-1):
        time.sleep(delay)
        if(handlerAgent == None):
            print("      -  Convo turn " + str(i))
            interlocutors = recoverInterlocutors(answer,agents,agents[agentId].name) 

            interlocutors = processInterlocutors(interlocutors,ids,coherence,equality,agents)

            while interlocutors.count(agentId) > 0:
                interlocutors.remove(agentId)

            if len(interlocutors) <= 0:
                interlocutors.expend(ids)

            agentId = random.choice(ids) #random.choice(interlocutors)
        else:
            agentId = gptNextInterlocutor(handlerAgent, agents) 

        answer = agents[agentId].talk()#tell(agents[agentId].name + " : ");#talk()
        conversationTalk(agentId,agents,answer,handlerAgent)
        #displayContextOf(agents[agentId],agents[agentId].context)

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

def conversationSix(handlerAgent):
    arthur = GptAgent("Arthur",Fore.CYAN,["agent_conversation.txt","arthur_perso.txt"],"Your name is Arthur.")
    adele = GptAgent("Adele",Fore.BLUE,["agent_conversation.txt","adele_perso.txt"],"Your name is Adele.")
    baptiste = GptAgent("Baptiste",Fore.RED,["agent_conversation.txt","baptiste_perso.txt"],"Your name is Baptiste.")
    christina = GptAgent("Christina",Fore.YELLOW,["agent_conversation.txt","christina_perso.txt"],"Your name is Christina.")
    normy = GptAgent("Normy",Fore.MAGENTA,["agent_conversation.txt","normy_perso.txt"],"Your name is Normy.")
    lea = GptAgent("Lea",Fore.GREEN,["agent_conversation.txt","lea_perso.txt"],"Your name is Lea.")

    agents = [arthur,adele,baptiste,christina,normy,lea]

    conversation(3,5,10,agents,"Say hi and introduce yourself",2,handlerAgent)

#print(Fore.WHITE)
#print("----------------------------")

#conversation_requests()

model = "gpt-5-mini-2025-08-07"

#handlerAgent = GptAgent("Handler",Fore.WHITE,"agent_handler.txt","","low")
#conversationSix(handlerAgent)



#conversation(2,4,8,agents,"Say hi and introduce yourself")