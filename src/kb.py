import os

with open('docs/kb_from_grok/cm.markdown', 'r') as file:
    cm = file.read()#.replace('\n', '')
with open('docs/kb_from_grok/dp.markdown', 'r') as file:
    dp = file.read()#.replace('\n', '')
with open('docs/kb_from_grok/inv.markdown', 'r') as file:
    inv = file.read()#.replace('\n', '')

knowledge_base = {
    "CM": cm,
    "DiffPair": dp,
    "Inverter": inv
}


def get_knowledge_base():
    """
    Returns the knowledge base for functional building block identification.
    """
    return knowledge_base

if __name__ == "__main__":
    # Example usage
    kb = get_knowledge_base()
    print("Knowledge Base:")
    for key, value in kb.items():
        print(f"{key}:\n{value}\n")
        print ("---------------------")