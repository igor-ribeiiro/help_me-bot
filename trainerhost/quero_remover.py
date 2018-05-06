import time
from trainerhost.constants import Constants
from db.operations import *
from IA.stringMatching import stringMatch


class QueroRemover:
    RTM_READ_DELAY = Constants.RTM_READ_DELAY

    def __init__(self, slack_client, parser):
        self.slack_client = slack_client
        self.parser = parser

    def run(self, string_array, channel):
        print("Got IA values")
        string_to_match = self.call_strings_from_db()  # call from db
        print("Call from db")
        string_array = [string_array[0]]

        for key_str in string_array:
            best_string = stringMatch(key_str, list(string_to_match))  # function(key_str, string_to_match)
            if best_string.lower() == key_str.lower() or best_string == "":
                response_str = key_str
            else:
                self.slack_client.api_call(
                    "chat.postMessage",
                    channel=channel,
                    text="Pode ser remover " + best_string + "? [Y/n]"
                )
                while True:
                    command, channel = self.parser.parse_bot_commands(self.slack_client.rtm_read())
                    if command:
                        response_str = self.loop_to_quero_remover(command.lower(), key_str,
                                                                  best_string)
                        break
                    time.sleep(Constants.RTM_READ_DELAY)

            response = "Removeu " + response_str + " com sucesso!"
            self.slack_client.api_call(
                "chat.postMessage",
                channel=channel,
                text=response
            )
            self.remove_string_from_db(response_str)
            print("Removed values to db")

    def call_strings_from_db(self):
        return get_unique_offered_trainings()

    def remove_string_from_db(self, deleted_str):
        remove_string_from_db(deleted_str)

    def loop_to_quero_remover(self, command, key_str, best_string):
        if command == "y":
            response = best_string
        else:
            response = key_str

        return response