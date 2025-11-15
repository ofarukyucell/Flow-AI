"""
Türkçe çekim varyantlarını kapsayan ek kalıplar 
Bu dosya regex motoruna doğal dil esnekliği kazandırır.
"""

VERB_SUFFIXES=[
    r"(ttım|ttim|ttum|ttüm)",          
    r"(tım|tim|tum|tüm)",
    r"(tın|tin|tun|tün)",
    r"(tı|ti|tu|tü)",

    r"(dım|dim|dum|düm)",
    r"(dın|din|dun|dün)",
    r"(dı|di|du|dü)",

    r"(tıktan|tikten|tuktan|tükten)",
    r"(tıktan sonra|tikten sonra|tuktan sonra|tükten sonra)",
    r"(dıktan|dikten|duktan|dükten)",
    r"(dıktan sonda|dikten sonra|duktan sonra|dükten sonra)",


    r"(ıyor|iyor|uyor|üyor)",

    r"(ın|in|un|ün)",

    r"(ıp|ip|up|üp)",

    r"(ınca|ince|unca|ünce)",
]

VERB_SUFFIX_PATTERN=r"(?:%s)?" % "|".join(VERB_SUFFIXES)
