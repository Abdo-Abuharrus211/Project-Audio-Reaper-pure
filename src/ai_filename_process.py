"""
This file is mainly used to process the file name of songs without
metadata and is often convulted and messy. So AI will be used to extract
info from the file name and then search for it on Spotify.

"""
import os

from dotenv import load_dotenv
from openai import OpenAI
import json

# this authenticates by auto retrieving the API key
load_dotenv()
client = OpenAI(
    api_key=os.getenv('OPENAI_API_KEY'),
)


def invoke_prompt_to_ai(file_names):
    """
        This function will invoke a prompt to the AI to extract the song's metadata from the filenames.

        :param: file_names: a list of strings representing the filenames of songs
        :precondition: file_names is a valid none-empty list of strings
        :return:
        """

    # TODO: implement failsafe and contingency for when rate limit is reached
    ai_responses = []
    if len(file_names) > 0:
        for name in file_names:
            prompt = f"Given the filename '{name}', provide the metadata in plain text, separating Title, Artist," \
                     f" and Album with commas, and leave blank if not specified. Don't label fields" \
                     f" and Say nothing else."
            response = client.chat.completions.create(
                model="gpt-4-0125-preview",
                messages=[
                    {"role": "system", "content": "You are a metadata extractor assistant."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=60,
            )

            response_text = response.choices[0].message.content.strip()
            ai_responses.append(response_text)
            # print(response_text)

    return ai_responses


def process_prompt_result(prompt_results):
    """
        This function will process the result from the prompt and format the result.
        :return:
        """
    metadata = []
    for res in prompt_results:
        segmented_text = res.split(",")
        song_dict = {"Title": segmented_text[0], "Artist": segmented_text[1], "Album": segmented_text[2]}
        metadata.append(song_dict)
    return metadata

# # Sample list of song filenames to test the function
# dummy_file_names = ["ACDC - It's A Long Way To The Top (If You Wanna Rock 'n' Roll).mp3",
#                     "AudioSlave - Like a Stone - AudioSlave.mp3",
#                     "Led Zeppelin - Led Zeppelin IV Stairway to Heaven.mp3"]
#
# example = invoke_prompt_to_ai(dummy_file_names)
# stuff = process_prompt_result(example)
#
# for som in stuff:
#     print(som)
