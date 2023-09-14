import openai

openai.api_key = "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"


def gptRequest(context,request):
    context.append(request)
    chat = openai.ChatCompletion.create(
            model="gpt-3.5-turbo", messages=context,temperature = 1
        )
    choices = chat.choices
    reply = choices[0].message.content
    context.append({"role":"assistant","content":reply})
    return reply

def displayContexts(context):
    for i in range(0,len(context)):
        print(context[i]["content"])

def displayContext(context,time,count):
    for i in range(0,count):
        print(context[time + i]["content"])

instructions = "You are Adele, a dumb student, studying computer science. You only talk using programming words."

time = 0
context = [{"role": "system", "content": instructions}]
request = {"role":"user", "content":"Hello, who are you ?"}

reply = gptRequest(context,request)

displayContext(context,0,3)
