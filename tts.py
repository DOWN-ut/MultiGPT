import os
os.environ["GOOGLE_APPLICATION_CREDENTIALS"]="wolfgpt-4a2c849c9aac.json"

import google.cloud.texttospeech as tts
import io
from playsound import playsound

def list_voices(language_code=None):
    client = tts.TextToSpeechClient()
    response = client.list_voices(language_code=language_code)
    voices = sorted(response.voices, key=lambda voice: voice.name)

    print(f" Voices: {len(voices)} ".center(60, "-"))
    for voice in voices:
        languages = ", ".join(voice.language_codes)
        name = voice.name
        gender = tts.SsmlVoiceGender(voice.ssml_gender).name
        rate = voice.natural_sample_rate_hertz
        print(f"{languages:<8} | {name:<24} | {gender:<8} | {rate:,} Hz")

def makeSpeech(voice_name:str,text:str,path:str):
    language_code = "-".join(voice_name.split("-")[:2])
    text_input = tts.SynthesisInput(text=text)
    voice_params = tts.VoiceSelectionParams(
        language_code=language_code, name=voice_name
    )
    audio_config = tts.AudioConfig(audio_encoding=tts.AudioEncoding.LINEAR16)

    client = tts.TextToSpeechClient()
    response = client.synthesize_speech(
        input=text_input,
        voice=voice_params,
        audio_config=audio_config,
    )

    filename = f"{path}"
    with open(filename, "wb") as out:
        out.write(response.audio_content)
        #print(f'Generated speech saved to "{filename}"')

    playsound(filename)


print(list_voices("en-US"))
#makeSpeech("en-US-News-N","Hello everyone","./audiotests/test1.wav")