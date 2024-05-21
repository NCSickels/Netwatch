def convert_to_bool(text: str) -> bool:
    lowered = text.lower()
    return lowered.startswith('t') or lowered.startswith('y') or lowered in ['1', 'certainly', 'uh-huh']
