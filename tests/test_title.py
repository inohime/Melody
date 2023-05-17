import re

# not an actual test

song_list = [
    (
        '美波', 
        '美波「グッドラッカー』MV(Ep23)'
    ),
    (
        'Ayase / YOASOBI', 
        'YOASOBI「アンコール」Official Music Video'
    ),
    (
        'Ayase / YOASOBI', 
        'YOASOBI「ハルカ」Official Music Video'
    ),
    (
        '凛として時雨 Official Channel', 
        "TK from 凛として時雨 『unravel』 Music Video(Full Size)"
    ),
    (
        'amazarashi Official YouTube Channel', 
        'amazarashi 『季節は次々死んでいく』 ”Seasons die one after another” “東京喰種トーキョーグール√A”ED'
    ),
    (
        'Sony Music (Japan)', 
        'Cö shu Nie – asphyxia (Official Video) / “東京喰種トーキョーグール:re” OP'
    ),
    (
        'Pandora Heaven', 
        'Tokyo Ghoul - Glassy Sky (東京喰種 -トーキョーグール-)'
    ),
    (
        '美波', 
        '美波「カワキヲアメク」MV'
    ),
    (
        'ずっと真夜中でいいのに。ZUTOMAYO', 
        'ずっと真夜中でいいのに。『秒針を噛む』」MV'
    ),
    (
        'Daoko', 
        'DAOKO × 米津玄師『打上花火』MUSIC VIDEO'
    ),
    (
        'Ayase / YOASOBI', 
        'YOASOBI「群青」Official Music Video'
    ),
    (
        '酸欠少女 さユり(Sanketsu-girl Sayuri)', 
        '酸欠少女さユり『平行線』MV(フルver)アニメ「クズの本懐」EDテーマ'
    ),
    (
        '50 Cent', 
        '50 Cent - In Da Club (Official Music Video)'
    ),
    (
        'BadMeetsEvilVEVO', 
        "Bad Meets Evil - Fast Lane ft. Eminem, Royce Da 5'9"
    ),
    (
        'EVNTYD', 
        'EVNTYD - Boredom (Official Audio)'
    ),
    (
        '稲葉曇',
        '稲葉曇『フロートプレイ』Vo. 歌愛ユキ'
    ),
    (
        'Minami',
        'Minami「 RUDE LOSE DANCE」（Anime「Record of RagnarokⅡ」Opening song）'
    ),
    (
        'ChrisBrownVEVO',
        'Chris Brown - Kiss Kiss (Feat. T-Pain) (Official HD Video) ft. T-Pain'
    ),
    (
        'SouljaBoyTellemVEVO',
        "Soulja Boy Tell'em - Crank That (Soulja Boy) (Official Music Video)"
    ),
    (
        'EllieGouldingVEVO',
        "Ellie Goulding, Juice WLRD - Hate Me"
    ),
    (
        'benny blanco',
        "benny blanco, Halsey & Khalid – Eastside (official video)"
    ),
    (
        'Patrik Pietschmann',
        'Hans Zimmer - Interstellar - Main Theme (Piano Version) + Sheet Music'
    ),
    (
        '緑黄色社会',
        '緑黄色社会 『Shout Baby』Music Video（TVアニメ『僕のヒーローアカデミア』4期「文化祭編」EDテーマ / MY HERO ACADEMIA ENDING'
    ),
    (
        'ヨルシカ / n-buna Official',
        'ヨルシカ - テレパス'
    ),
    (
        'ヰ世界情緒 -Isekaijoucho-',
        '【歌ってみた】アンノウン・マザーグース/ covered by ヰ世界情緒'
    ),
    # one of the few cases that can be fixed (split from '/' and check for artist name) but won't be 
    (
        'Ryu Matsuyama',
        'Ryu Matsuyama / Under the Sea feat. Max Jenmana【Lyric Video】'
    ),
    # fails on the space? todo: fix me
    (
        "Biteki びてき",
        "heylog - i love you (lyrics)"
    )
]

def test_songs():
    for x in song_list:
        print(title_test5(x[1], x[0]))

# title parser: iteration 1
def get_title_test1(title: str, name: str):
    char_cmp_list = ["『", "』", "「", "」"]
    matched = False
    for s in re.finditer(r"[^\w\d\s:]", title):
        char = s.group()
        # right here, we only want the first match
        if char_cmp_list[0::2]:
            if title[:s.start() - 1].lower() in name.lower():
                title = title[s.end():]
                matched = True
        else:
            title = title[s.end() - 1:]
        
        # we want to find the character pos in the updated string (this is not updated at all)
        if char in char_cmp_list[1::2]:
            print(title.index(char), char)
            if not matched:
                # print("not matched", title[:title.index(char) + 1])
                title = title[:title.index(char) + 1]
            else:
                title = title[:title.index(char)]

    print(title)

# title parser: iteration 2
def get_title_test2(title: str, name: str):
    # # strip the "official audio" and the "artist name + non-alphanumeric character" # #
    # strips the "official .."
    # x = re.search(r"Official.*", title)
    # if x:
    #     title = title[0:x.start() - 2]
    
    # note: find a list of non-alphanumeric unicode paranthesis chars 
    char_cmp_list = ["『", "』", "「", "」"]
    first_char_matched = False

    # strips the special character
    for s in re.finditer(r"[^\w\d\s:]", title):
        char = s.group()

        if char in char_cmp_list[0::2]:
            print(char)
            # for when the channel name is in the title
            # break this into chunks and check if (per space) the channel name is in the title
            title_chunks = title.split(' ')
            print(title_chunks)
            for x in title_chunks:
                if x[0 : s.start() - 1].lower() in name.lower():
                    if title[s.start() + 1 : s.end() + 1] in char_cmp_list[0::len(char_cmp_list)]:
                        # remove everything up until the name of the song
                        title = title[s.end() + 1:]
                    else:
                        # remove it from the title
                        title = title[s.end():]

                    first_char_matched = True
                    break

            # now strip the end
        if char in char_cmp_list[1::2]:
            print("yup")
            char_pos = title.find(char)
            if char_pos == -1:
                continue

            title = title[:char_pos + 1] if not first_char_matched else title[:char_pos]

        # parse normal titles for song artist name (where they have a dash)
        if char not in char_cmp_list and char == '-':
            if title[0 : s.start() - 1].lower() in name.lower():
                title = title[s.end():]

        # check for when artists put a space in their channel name or title so we can remove it from the title
        # remove all spaces in both and compare


    print(title)

# title parser: iteration 3
def get_title_test3(title: str, name: str):
    title_bucket, name_bucket = ''.join(title.split(' ')), ''.join(name.split(' '))

    # # strip the "official audio" and the "artist name + non-alphanumeric character" # #
    # strips the "official .."
    x = re.search(r"Official.*", title)
    if x:
        title = title[0:x.start() - 1]
    
    # note: find a list of non-alphanumeric unicode paranthesis chars 
    char_cmp_list = ["『", "』", "「", "」"]
    first_char_matched = False

    # strips the special character
    for s in re.finditer(r"[^\w\d\s:]", title):
        char = s.group()

        if char in char_cmp_list[0::2]:
            # for when the channel name is in the title
            # break this into chunks and check if (per space) the channel name is in the title
            title_chunks = title.split(' ')
            for x in title_chunks:
                this_chunk = x[0 : s.start() - 1].lower()
                this_tb_chunk = title_bucket[0:title_bucket.find(char)].lower()

                if this_chunk in name.lower() or this_tb_chunk in name_bucket.lower():
                    if title[s.end() : s.end() + 1] in char_cmp_list[0::len(char_cmp_list)]:
                        # remove everything up until the name of the song
                        title = title[s.end() + 1:]
                    else:
                        # remove it from the title
                        title = title[s.end():]

                    first_char_matched = True
                    break

        # now strip the end
        if char in char_cmp_list[1::2]:
            char_pos = title.find(char)
            if char_pos == -1:
                continue

            title = title[:char_pos + 1] if not first_char_matched else title[:char_pos]

        # parse normal titles for song artist name (where they have a dash)
        if char not in char_cmp_list and char == '-':
            tb_char_pos = title_bucket.find(char)
            if tb_char_pos == -1:
                continue
            
            name_in_title = title[0 : s.start() - 1].lower()
            name_in_tb = title_bucket[0 : tb_char_pos].lower()

            if name_in_title in name.lower() or name_in_tb in name_bucket.lower():
                title = title[s.end() + 1:]

    return title if len(title) >= 2 else title + ' '                  

# title parser: iteration 4
def old_title_test4(title: str, name: str):
            # remove "Official" and any following words after
        x = re.search(r"official.*", title.lower())
        if x:
            # if there is a space before the official, remove it
            if title[x.start() - 2 : x.start() - 1] == " ":
                title = title[0:x.start() - 2]
            else:
                title = title[0:x.start() - 1]

        name_bucket = ''.join(name.split(' '))
        title_bucket = ''.join(title.split(' '))
        title_chunks = title.split(' ')

        en_dash = '\u2013' 
        char_cmp_list = ["『", "』", "「", "」"]
        first_char_matched = False
        name_found = False

        # strip non-alphanumeric characters from the title
        for na_char in re.finditer(r"[^\w\d\s:]", title):
            char = na_char.group()

            # beginning bracket
            if char in char_cmp_list[0::2]:
                # for when the channel name is in the title
                # break this into chunks and check if (per space) the channel name is in the title
                for chunk in title_chunks:
                    if first_char_matched:
                        break

                    this_chunk = chunk[0 : na_char.start()].lower()
                    this_tb_chunk = title_bucket[0 : na_char.start()].lower()

                    if this_chunk in name.lower() or this_tb_chunk in name_bucket.lower():
                        # check if there are two adjacent non-alphanumeric chars 
                        # and remove everything up until the name of the song
                        if title[na_char.end() : na_char.end() + 1] in char_cmp_list[0::len(char_cmp_list)]:
                            # non-alphanumeric char may have two, so we have to capture both 
                            title = title[na_char.end() + 1:]
                        else:
                            title = title[na_char.end():] 
                        
                        first_char_matched = True
                        break
            
            if char in char_cmp_list[1::2]:
                char_pos = title.find(char)
                if char_pos == -1:
                    continue
                
                # if the bracket was matched, remove the end bracket
                title = title[:char_pos + 1] if not first_char_matched else title[:char_pos]

            # parse normal titles for song artist name (where they have a dash)
            elif char not in char_cmp_list:
                if char == '-' or char == en_dash:
                    for chunk in title_chunks:
                        if name_found:
                            break

                        tb_char_pos = title_bucket.find(char)
                        if tb_char_pos == -1:
                            continue
                        
                        name_in_title = chunk[0 : tb_char_pos].lower()
                        name_in_tb = title_bucket[0 : tb_char_pos].lower()
                        
                        if name_in_title in name.lower() or name_in_tb in name_bucket.lower():
                            name_found = True
                            title = title[na_char.end() + 1:]

        return title if len(title) >= 2 else title + ' ' 

# title parser: iteration 5
def title_test4(title: str, name: str) -> str:
    # remove "Official" and any following words after
    x = re.search(r"official.*", title.lower())
    if x:
        # if there is a space before the official, remove it
        if title[x.start() - 2 : x.start() - 1] == " ":
            title = title[0:x.start() - 2]
        else:
            title = title[0:x.start() - 1]

    name_bucket = ''.join(name.split(' '))
    title_bucket = ''.join(title.split(' '))
    title_chunks = title.split(' ')

    en_dash = '\u2013' 
    char_cmp_list = ["『", "』", "「", "」"]
    first_char_matched = False
    name_found = False

    # strip non-alphanumeric characters from the title
    for na_char in re.finditer(r"[^\w\d\s:]", title):
        char = na_char.group()

        # beginning bracket
        if char in char_cmp_list[0::2]:
            # for when the channel name is in the title
            # break this into chunks and check if (per space) the channel name is in the title
            for chunk in title_chunks:
                if first_char_matched:
                    break

                tb_char_pos = title_bucket.find(char)
                if tb_char_pos == -1:
                    continue

                this_chunk = chunk.lower()
                this_tb_chunk = title_bucket[0 : tb_char_pos].lower()

                if this_chunk in name.lower() or this_tb_chunk in name_bucket.lower():
                    # check if there are two adjacent non-alphanumeric chars 
                    # and remove everything up until the name of the song
                    if title[na_char.end() : na_char.end() + 1] in char_cmp_list[0::len(char_cmp_list)]:
                        # non-alphanumeric char may have two, so we have to capture both 
                        title = title[na_char.end() + 1:]
                    else:
                        title = title[na_char.end():] 
                    
                    first_char_matched = True
                    break
        
        if char in char_cmp_list[1::2]:
            char_pos = title.find(char)
            if char_pos == -1:
                continue
            
            # if the bracket was matched, remove the end bracket
            title = title[:char_pos + 1] if not first_char_matched else title[:char_pos]

        # parse normal titles for song artist name (where they have a dash)
        elif char not in char_cmp_list:
            if char == '-' or char == en_dash:
                for chunk in title_chunks:
                    if name_found:
                        break

                    tb_char_pos = title_bucket.find(char)
                    if tb_char_pos == -1:
                        continue
                    
                    name_in_title = chunk.lower()
                    name_in_tb = title_bucket[0 : tb_char_pos].lower()
                    
                    if name_in_title in name.lower() or name_in_tb in name_bucket.lower():
                        title = title[na_char.end() + 1:]
                        name_found = True

    return title if len(title) >= 2 else title + ' ' 

# title parser: iteration 6
def title_test5(title: str, name: str) -> str:
     # remove "Official" and any following words after
        x = re.search(r"official.*", title.lower())
        if x:
            # if there is a space before the official, strip it
            if title[x.start() - 2 : x.start() - 1] == " ":
                title = title[0:x.start() - 2]
            else:
                title = title[0:x.start() - 1]

        name_bucket = ''.join(name.split(' '))
        title_bucket = ''.join(title.split(' '))
        title_chunks = title.split(' ')

        en_dash = '\u2013' 
        char_cmp_list = ["『", "』", "「", "」"]
        first_char_matched = False
        name_found = False

        # strip non-alphanumeric characters from the title
        for na_char in re.finditer(r"[^\w\d\s:]", title):
            char = na_char.group()

            # beginning bracket
            if char in char_cmp_list[0::2]:
                # for when the channel name is in the title
                # break this into chunks and check if (per space) the channel name is in the title
                for chunk in title_chunks:
                    if first_char_matched:
                        break

                    tb_char_pos = title_bucket.find(char)
                    if tb_char_pos == -1:
                        continue

                    this_chunk = chunk.lower()
                    this_tb_chunk = title_bucket[0 : tb_char_pos].lower()

                    if this_chunk in name.lower() or this_tb_chunk in name_bucket.lower():
                        # check if there are two adjacent non-alphanumeric chars 
                        # and remove everything up until the name of the song
                        if title[na_char.end() : na_char.end() + 1] in char_cmp_list[0::len(char_cmp_list)]:
                            # non-alphanumeric char may have two, so we have to capture both 
                            title = title[na_char.end() + 1:]
                        else:
                            title = title[na_char.end():] 
                        
                        first_char_matched = True
                        break
            
            if char in char_cmp_list[1::2]:
                char_pos = title.find(char)
                if char_pos == -1:
                    continue
                
                # if the bracket was matched, remove the end bracket
                title = title[:char_pos + 1] if not first_char_matched else title[:char_pos]

            # parse normal titles for song artist name (where they have a dash)
            elif char not in char_cmp_list:
                if char == '-' or char == en_dash:
                    for chunk in title_chunks:
                        if name_found:
                            break

                        tb_char_pos = title_bucket.find(char)
                        if tb_char_pos == -1:
                            continue
                        
                        name_in_title = chunk.lower()
                        name_in_tb = title_bucket[0 : tb_char_pos].lower()
                        
                        if name_in_title in name.lower() or name_in_tb in name_bucket.lower():
                            title = title[na_char.end() + 1:]
                            name_found = True

        if len(title) >= 2:
            return title

        elif len(title) <= 0 or title == " ":
            print("Something went wrong, rejecting parsed title!")
            return ' '.join([x for x in title_chunks])

        else:
            return title + ' '

test_songs()

# individual test cases
# title = song_list[len(song_list) - 1][1]
# name = song_list[len(song_list) - 1][0]
# print(title_test4(title, name))

# for our last two test cases (minami and inabakumori), they seem to not work with the current implementation, but it works with the one below
# ✅ already fixed
'''
import re
# name = 'Minami'
# title = "Minami「 RUDE LOSE DANCE」（Anime「Record of RagnarokⅡ」Opening song）"
name = '稲葉曇'
title = '稲葉曇『フロートプレイ』Vo. 歌愛ユキ'

name_bucket = ''.join(name.split(' '))
title_bucket = ''.join(title.split(' '))

char_cmp_list = ["『", "』", "「", "」"]

for s in re.finditer(r"[^\w\d\s:]", title):
    char = s.group()
    
    if char in char_cmp_list[0::2]:
        if title_bucket[0:s.start()].lower() in name_bucket.lower():
            title = title[s.end():]
            
    if char in char_cmp_list[1::2]:
        char_pos = title.find(char)
        if char_pos == -1:
            continue
        title = title[:char_pos]
            
print (title)
'''