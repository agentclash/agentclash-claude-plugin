"""Scripted sample revision 2: preserve the first refund. Not a user's agent."""
from agentclash_eval.reference_targets import correct


def invoke(prompt, tools):
    return correct(prompt, tools)
