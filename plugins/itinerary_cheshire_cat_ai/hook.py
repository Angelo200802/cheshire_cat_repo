from cat.mad_hatter.decorators import hook

@hook
def agent_prompt_prefix(prefix,cat):
    settings = cat.mad_hatter.get_plugin().load_settings()
    prefix = settings['prefix']
    return prefix

