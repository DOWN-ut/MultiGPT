import openai
from colorama import Fore, Back, Style

max_response_tokens = 100


keyFile = open("key.txt", "r")
openai.api_key = keyFile.read() #open key.txt


def gptRequest(context,request):
    context.append(request)
    chat = openai.ChatCompletion.create(
            model="gpt-3.5-turbo", 
            messages=context,
            temperature = 1,
            max_tokens=max_response_tokens
        )
    choices = chat.choices
    reply = choices[0].message.content
    context.append({"role":"assistant","content":reply})
    return context

def displayContext(context):
    color = Fore.CYAN
    if context["role"] == "user":
        color = Fore.YELLOW
    elif context["role"] == "system":
        color = Fore.GREEN
    print(color + "> " + context["content"])

def displayContexts(context,time,count):
    for i in range(0,count):
        displayContext(context[time + i])
        print("   ")
    print(Fore.WHITE)

def makeRequest(text):
    return {"role":"user", "content":text}

def makePrePrompt(text):
    return {"role":"system", "content":text}

class GptAgent:
    def __init__(self, name,prepromtPath):
        self.name = name
        self.prepromt = makePrePrompt(open(prepromtPath, "r").read())
        self.context = [self.prepromt]

    def tell(self,request):
        self.context = gptRequest(self.context,makeRequest(request))
        return self.context

print("----------------------------")

adele = GptAgent("Adele","agent_preprompt.txt")
adeleContext = adele.tell("Hello, who are you ?")
displayContexts(adeleContext,0,3)

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
