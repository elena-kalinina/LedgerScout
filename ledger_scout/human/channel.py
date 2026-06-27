"""HumanChannel — scripted offline demo by default."""
import os


class HumanChannel:
    def ask(self, question, options=None):
        raise NotImplementedError

    def instruct(self, message):
        raise NotImplementedError


class ScriptedChannel(HumanChannel):
    def __init__(self, script):
        self.script = script
        self.transcript = []

    def ask(self, question, options=None):
        answer = next(
            (a for needle, a in self.script if needle.lower() in question.lower()),
            options[0] if options else "ok",
        )
        self.transcript.append(("ask", question, answer))
        return answer

    def instruct(self, message):
        self.transcript.append(("instruct", message, None))


def get_channel(script=None):
    return ScriptedChannel(script or [])
