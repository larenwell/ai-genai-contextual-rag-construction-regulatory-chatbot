from translate import Translator

def translate_text(text: str, target_lang: str = "en") -> str:
    translator = Translator(from_lang="es", to_lang=target_lang)
    translation = translator.translate(text)
    return translation
    