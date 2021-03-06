#!/usr/bin/env python
# -*- coding: utf-8 -*-
###############################################################################
## Scryfall Voice Assistant
## Description: This application takes the name of a Magic Card as voice
##              Input and returns an image of the named card.
###############################################################################
## Author: Matthew Lamont
## Copyright: Copyright 2021 Matthew Lamont
## Credits: Zhang, Anthony. 2017. Speech Recognition (version 3.8).
##          Scott, Nanda. 2018. Scrython (version 1.10.1)
##          
## License: Copyright (C) <year> <name of author>
##          This program is free software; you can redistribute it and/or 
##          modify it under the terms of the GNU General Public License as 
##          published by the Free Software Foundation; either version 2 of 
##          the License, or (at your option) any later version.
##
##          This program is distributed in the hope that it will be useful, 
##          but WITHOUT ANY WARRANTY; without even the implied warranty of 
##          MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU 
##          General Public License for more details.
##
##          You should have received a copy of the GNU General Public License 
##          along with this program; if not, write to the Free Software 
##          Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307 
##          USA
## Version: 1.0.0
###############################################################################
from PIL import Image
from time import sleep
from urllib.request import Request, urlopen

import speech_recognition as sr
import scrython

CARD_DISPLAY_TIME = 10

def main():
        # create recognizer and mic instances
        recognizer = sr.Recognizer()
        microphone = sr.Microphone()
        
        # main loop
        while True:
                # Loop till the speech recognition API returns a result. 
                while True:
                        print("Speak!")
                        speech_results = recognize_speech_from_mic(recognizer, microphone)
                        if speech_results["transcription"]:
                                break
                        if not speech_results["success"]:
                                break
                        print("I didn't catch that. What did you say?\n")

                # if there was an error, stop the program
                if speech_results["error"]:
                        print("ERROR: {}".format(speech_results["error"]))
                        break

                # show the user the transcription
                print("You said: {}".format(speech_results["transcription"]))

                # close the application at the users request
                # TODO - Clean all images generated by app.
                if(speech_results["transcription"]=="exit"):
                        exit()

                # Sends data transcription to ScryFall for processing
                scryfall_query(speech_results)


        
def scryfall_query(speech_results):
        ## Query the Scryfall API for the card from the voice transcription 
        ## and saves the card image to root directory
        try:
                card = scrython.cards.Named(fuzzy=speech_results["transcription"])

                card_image = card.image_uris()
                        
                print(card_image['small'])

                req = Request(card_image['png'])
                resource = urlopen(req)
                output = open("img.png","wb")
                output.write(resource.read())
                output.close()

                show_image()
        except scrython.foundation.ScryfallError:
                print("Too many results")

def show_image():
        img = Image.open("img.png")
        img.show()

def recognize_speech_from_mic(recognizer, microphone):
        ## Gets user input and returns it to main function

        # check that recognizer and microphone arguments are appropriate type
        if not isinstance(recognizer, sr.Recognizer):
                raise TypeError("`recognizer` must be `Recognizer` instance")

        if not isinstance(microphone, sr.Microphone):
                raise TypeError("`microphone` must be `Microphone` instance")

        # adjust the recognizer sensitivity to ambient noise and record audio
        # from the microphone
        with microphone as source:
                recognizer.adjust_for_ambient_noise(source)
                audio = recognizer.listen(source)
        # set up the response object
        response = {
                "success": True,
                "error": None,
                "transcription": None
        }

        # try recognizing the speech in the recording
        # if a RequestError or UnknownValueError exception is caught,
        # update the response object accordingly
        try:
                response["transcription"] = recognizer.recognize_google(audio)
        except sr.RequestError:
                # API was unreachable or unresponsive
                response["success"] = False
                response["error"] = "API unavailable"
        except sr.UnknownValueError:
                # speech was unintelligible
                response["error"] = "Unable to recognize speech"

        return response


if __name__ == "__main__":
        main()