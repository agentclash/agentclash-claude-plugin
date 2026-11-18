"""Scripted sample revision 1: intentionally refund twice. Not a user's agent."""
from agentclash_eval.reference_targets import faulty_double


def invoke(prompt, tools):
    return faulty_double(prompt, tools)
