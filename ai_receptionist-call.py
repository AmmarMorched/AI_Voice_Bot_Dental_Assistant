import assemblyai as aai
from elevenlabs import generate, stream
from openai import OpenAI


class AI_Assistant:
    def __init__(self):
        aai.settings.api_key= "84e03c5d3db34590a0dd28cae2b62c70"
        self.openai_client = OpenAI(api_key="API-KEY")
        self.elevenlabs_api_key= "sk_5910e396c738ad86027b7fd2099bee8e54d96e657e9306ac"

        #empty transcribe object
        self.transcribe = None

        #List containt everything we say and the ai assistant say
        #before the conv starts , we want full_transcript to only include the prompt we give to open ai
        
        self.full_transcript = [
            {"role":"system", "content":"You are a receptionist at a dental clinic. Be resourcefull and efficient."},
        ]

    def start_transcription(self):
        self.transcriber = aai.RealtimeTranscriber(
            sample_rate=16000,
            on_data=self.on_data,
            on_error=self.on_error,
            on_open=self.on_open,
            on_close=self.on_close,
            end_utterance_silence_threshold=1000  #the time tha ai will wait before he determin that you have ended a sentance when you are talking in real time 
    )


    #Connect microphone and stream data to assembly ai API
        self.transcriber.connect()
        microphone_stream = aai.extras.MicrophoneStream(sample_rate=16000)
        self.transcriber.stream(microphone_stream)



    def stop_transcription(self):
        if self.transcriber:
            self.transcriber.close()
            self.transcriber = None



    def on_open(self, session_opened: aai.RealtimeSessionOpened):
        #print("Session ID:", session_opened.session_id)
        return


    #in here we are definning what we gonna do with the transcrip comming from assembly ai
    def on_data(self, transcript: aai.RealtimeTranscript):
        if not transcript.text:
            return

        if isinstance(transcript, aai.RealtimeFinalTranscript):
            #print(transcript.text, end="\r\n") this will print what i says
            self.generate_ai_response(transcript)
        else:
             print(transcript.text, end="\r")


    def on_error(self, error: aai.RealtimeError):
        #print("An error occured:", error)
        return


    def on_close(self):
        #print("Closing Session")
        return



######### Step 3: Pass real_time transcript to Open_AI ###########


    def generate_ai_response(self, transcipt):
        #pause the real_time trans stream while we passing and communicating with open_ai API
        self.stop_transcription() 

        #Add real_time transcript to full_transcriptlist
        self.full_transcript.append({"role":"user", "content": transcipt.text})
        #print what user sad
        print(f"\nPatient: {transcipt.text}", end="\r\n")

        #now we pass transcript directly to openAI api
        response = self.openai_client.chat.completions.create(
            model = "gpt-3.5-turbo",
            messages = self.full_transcript
        )

        #retrieve the response from open ai api and store into AI response
        ai_response = response.choices[0].message.content 


    ###### Now we can go ahead and generate audio

        self.generate_audio(ai_response)

        #once we have generated audio we can restart real time transcription
        #so we can continue the converstion
        self.start_transcription()


############ Step 4 : Generate audio with ElevenLabs #############

    def generate_audio(self, text):
        # the text param is the responde from ai and we add that to full transcript
        self.full_transcript.append({"role":"assistant", "content": text})
        print(f"\nAI Receptionist: {text}")

        #sending request to elevenlabs APi 
        audio_stream = generate(
            api_key=self.elevenlabs_api_key,
            text=text,
            voice = "Rachel",
            stream= True
        )
        stream(audio_stream)


############# Step 2: Real_Time Transcription with AssemblyAI ############





greeting = "Thank you for calling our clinic. My name is Rachell, how can i help you ?"
ai_assistant = AI_Assistant()
ai_assistant.generate_audio(greeting)
ai_assistant.start_transcription()




    













