from cat.mad_hatter.decorators import tool
import json

def tell_event(mex_json,cat) : 
    data = mex_json['data']
    mex = mex_json['mex']
    prompt = f"""Genera una risposta a :"{mex}". Gli eventi sono i seguenti in formato json : {data}.
    """
    return cat.llm(prompt)

action = {
    "event" : "get_event"
}
action_label = {
    "event" : ["Quali eventi si terranno","Aggiornami sugli ultimi eventi"] #far ritornare la città come parametro
}
method = {
    'event' : { 'tell_event' : tell_event }

}
method_label = {
    'tell_event' : ["Quali eventi si terranno","Aggiornami sugli ultimi eventi"]
}

@tool(return_direct = True, examples = ['{ "mex" : "messaggio", "type" : "tipo", "data" : { } }'])
def response_json(tool_input,cat):
    """Utile per rispondere a tutti i messaggi in formato json, i campi possono essere :
    mex,type e data
    Tool_input è l'intero messaggio in formato json"""
    print(f"input = {cat.working_memory.user_message_json.text}")
    mex_json = json.loads(cat.working_memory.user_message_json.text)
    if 'mex' in mex_json and 'type' in mex_json and mex_json['type'] == 'chat':
        label = cat.classify(mex_json['mex'],labels = action_label)
        if label in action:
            return f"""{{ "action" : "{action[label]}", "type" : "{label}"}}"""
    if "data" in mex_json:
        label = cat.classify(mex_json['mex'], labels = method_label)
        print(f"label = {label}, {method[mex_json['type']]}")
        if label in method[mex_json['type']]:
            msg = method[mex_json['type']][label](mex_json,cat)
            return f"""{{ "mex" : "{msg}", "status" : "successfull"}}"""
    return f"{mex_json}"
