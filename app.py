import openai
from elevenlabslib import *

import speech_recognition as sr
from pydub import AudioSegment
from pydub.playback import play

import streamlit as st

openai.api_key = "YOUR_OPENAI_API"
user = ElevenLabsUser("YOUR_ELEVENLABS_API")

WAKE_WORD = "sam" # or any wake word of your choosing

recognizer = sr.Recognizer()
mic = sr.Microphone()


def wake(source):
    audio = recognizer.listen(source)
    message = recognizer.recognize_google(audio)
    return message

def transcribe(source):
    audio = recognizer.listen(source)
    message = recognizer.recognize_google(audio)
    print(f"You said: {message.capitalize()}")
    st.write(f"You said: {message.capitalize()}")
    return message

def generate(message):
    global chat_history
    chat_history.append({"role": "user", "content": message})
    completion = openai.ChatCompletion.create(
        model = "gpt-3.5-turbo",
        messages = chat_history,
        temperature=0.3,
    )
    response = completion.choices[0].message.content
    print(f"ChatGPT: {response}")
    st.write(f"ChatGPT: {response}")
    chat_history.append({"role": "assistant", "content": response})
    return response

def speak_text(response):
    voice = user.get_voices_by_name("Adam")[0] # or any voice of your choosing
    voice.generate_and_play_audio(response, playInBackground=False)

def main():
    while True:
        with mic as source:
            recognizer.adjust_for_ambient_noise(source)
            print("Waiting for wake word 'Hey Sam'")
            st.write("Waiting for wake word 'Hey Sam'")
            
            while True:
                try:
                    word = wake(source)
                    if WAKE_WORD in word.lower():
                        sound = AudioSegment.from_wav("Start.wav")
                        play(sound)
                        print("Ask question!")
                        st.write("Ask question!")
                        break
                    else:
                        print("Try Again!")
                
                except Exception:
                    print("Error Transcribing Audio!")

            while True:
                try:
                    message = transcribe(source)
                    if message == "thanks":
                        sound = AudioSegment.from_wav("End.wav")
                        play(sound)
                        break
                    else:
                        response = generate(message)
                        speak_text(response)

                except Exception:
                    print("Error Transcribing Audio!")

        break


if __name__ == "__main__":
    chat_history = []
    st.title("ChatGPT Voice Assistant")
    st.write("Say 'Thanks' to stop recording")

    start, stop = st.columns(2)

    if start.button("Start listening"):
        main()
    if stop.button("Refresh"):
        st.experimental_rerun()
