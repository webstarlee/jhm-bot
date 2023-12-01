import re

def remove_first_emoji(text):
    emoji_pattern = r'^<:[A-Za-z0-9_]+:\d+>'
    
    text_without_starting_emoji = re.sub(emoji_pattern, '', text)
    
    return text_without_starting_emoji