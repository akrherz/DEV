"""When RER was vectorized, I did not fill back the channels nor twitter subs

 select distinct source, pil from products where substr(pil, 1, 3) = 'RER';
"""
o = open('insert.sql', 'w')

for line in open('rer.txt'):
    (source, pil) = line.strip().split("|")
    source = source.strip()
    pil = pil.strip()
    if len(source) != 4 or len(pil) != 6:
        continue
    o.write("""
    INSERT into iembot_room_subscriptions(roomname, channel)
    VALUES ('%schat', '%s');
    """ % (source[1:].lower(), pil))
    o.write("""
    INSERT into iembot_twitter_subs(screen_name, channel)
    VALUES ('iembot_%s', '%s');
    """ % (source[1:].lower(), pil))
o.close()
