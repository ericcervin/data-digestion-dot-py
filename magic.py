#json data files from https://mtgjson.com/downloads/all-sets/

import json, sqlite3, os

sets = ['AKH','HOU','XLN','RIX','DOM','M19','GRN','RNA','WAR','M20','ELD','THB','IKO','M21','ZNR','KHM']

def main():
    set_data = load_set_data(sets)
    deck_data = load_deck_data()
    
    create_magic_db({"sd":set_data,"dd":deck_data})

    print_set_data(set_data)
    print_deck_data()


def brief_card_map(card_json):
   return {'set_code': card_json.get('setCode',''),
           'name':  card_json.get('name',''),
           'type': card_json.get('type','').encode("ascii","ignore"),
           'types': card_json.get('types',''),
           'subtypes': card_json.get('subtypes',''),
           'supertypes': card_json.get('supertypes',''),
           'number': card_json.get('number','')[:3],
           'color_id': card_json.get('colorIdentity',''),
           'is_rakdos': isRakdos(card_json.get('colorIdentity','')),
           'is_starter': card_json.get('isStarter',''),
           'cmc': card_json.get('convertedManaCost','')
          }
    
def brief_card_text(card_map):
    return ('\t').join([
                 card_map['set_code'],
                 card_map['number'],
                 card_map['name'],
                 str(card_map['cmc']),
                 card_map['type'],
                 (',').join(card_map['color_id']),
                 #str(card_map['is_rakdos'])
                 ]) + '\n'

def create_magic_db(mp):
    sd = mp["sd"]
    dd = mp["dd"]
    #print(sd['XLN'].keys())
          
    conn = sqlite3.connect('./resources/magic/OUT/magic.db')
    
    c = conn.cursor()
    
    try:
      c.execute('''DROP TABLE card''')
    except:
      pass
    
    c.execute('''CREATE TABLE card
             (set_code text, number integer, name text, cmc real, type text, color_id text )''')
              
    conn.commit()

    for st in sd.values():
        for crd in st['distinct_cards'].values():
            c.execute('INSERT INTO card VALUES (?,?,?,?,?,?)', (crd[0]['set_code'], str(crd[0]['number']), crd[0]['name'], str(crd[0]['cmc']), crd[0]['type'], str(crd[0]['color_id'])))

    conn.commit()

    try:
      c.execute('''DROP TABLE deck_card''')
    except:
      pass
    
    c.execute('''CREATE TABLE deck_card
             (deck text, deck_or_side text, count integer , set_code text, name text, num integer)''')
              
    conn.commit()
    
    for st in dd:
        c.execute('INSERT INTO deck_card VALUES (?,?,?,?,?,?)', (st['deck'], st['deck_or_side'], st['count'], st['set_code'], st['name'], st['num']))

    conn.commit()

    
    conn.close()


def distinct_card_maps(cards):
    brief_card_maps = map(brief_card_map, cards)
    distinct_cards = {}
    for c in brief_card_maps:
                if distinct_cards.has_key(c['name']):
                    distinct_cards[c['name']].append(c)
                else:
                    distinct_cards[c['name']] = [c]
    return distinct_cards

def isRakdos(color_id):
    return (not (('U' in color_id) or ('W' in color_id) or ('G' in color_id)) )



def load_deck_data():
    old_decks = os.listdir("./resources/magic/IN/old_arena_decks/")
    deck_data = []
    for od in old_decks:
        with open("./resources/magic/IN/old_arena_decks/" + od, "r") as deck_file:
            for ln in deck_file.readlines():
                split_ln = ln.split()
                if len(split_ln) > 0:
                  if ((split_ln[0] == "Deck") or (split_ln[0] == "Sideboard")):
                      deck_or_side = split_ln[0]
                  if len(split_ln) > 1:
                    count = split_ln[0]
                    set_code = split_ln[-2].replace('(','').replace(')','')
                    name = (" ").join(split_ln[1:-2])
                    num = split_ln[-1].strip()
                    item_map = {"deck": od, "deck_or_side": deck_or_side, "count": count , "set_code": set_code, "name": name, "num": num} 
                    deck_data.append(item_map)
    return deck_data
    
    
def load_set_data(sets):
    set_data = {}
    for card_set in sets:
        with open("./resources/magic/IN/mtg_json/" + card_set + ".json", "r") as read_file:
            data = json.load(read_file)
            set_data[card_set] = {'raw_data' : data,
                                  'name' : data['data']['name'],
                                  'total_set_size' : data['data']['totalSetSize'],
                                  'base_set_size' : data['data']['baseSetSize'],
                                  'distinct_cards' : distinct_card_maps(data['data']['cards'])
                                  } 
    return set_data

def print_card_tsv(file_name,card_map):   
    sorted_cards = sorted(card_map.items(), key=lambda x: x[1][0]['name'])
    with open("./resources/magic/OUT/set_card_lists/" + file_name, "w") as card_file:
             for c in sorted_cards:
               #print(c[0] + '\t' + str(len(c[1])))
               text = brief_card_text(c[1][0]).encode('utf-8')
               card_file.write(text)

def print_deck_data():
    conn = sqlite3.connect('./resources/magic/OUT/magic.db')
    
    c = conn.cursor()

    all_decks = []
    for row in c.execute('SELECT DISTINCT deck FROM deck_card'):
       all_decks.append(row[0])    
    
    for dk in all_decks:
        with open("./resources/magic/OUT/old_deck_lists/" + dk, "w") as deck_file:
          #print(dk)
          query = 'SELECT dc.* FROM deck_card dc join card cd on dc.set_code = cd.set_code and dc.num = cd.number where dc.deck = \"' + dk + '\"'
          header = ('\t').join(["deck", "deck_or_side", "count", "set_code", "name", "num"])
          deck_file.write(header + '\n')                               
          for crd in c.execute(query):
            output = crd[0] + '\t' + crd[1] + '\t' + str(crd[2]) + '\t' + crd[3] + '\t' + crd[4] + '\t' + str(crd[5]) + '\n'
            #(deck text, deck_or_side text, count integer , set_code text, name text, num integer)
            deck_file.write(output)

    conn.close()

def print_set_data(set_data):
      #print set_data.keys()
    print "set_id\tset_name\tset_size\tbase_set_size\tdistinct_cards\trakdos_cards"
    for k in sets:
        set_id = k
        name = set_data[k]['name']
        total_set_size = set_data[k]['total_set_size']
        base_set_size = set_data[k]['base_set_size']
        distinct_card_count = len(set_data[k]['distinct_cards'])

        set_data[k]['subtype_counts'] = subtype_counts(set_data[k]['distinct_cards'])

        distinct_rakdos_cards = {key:value for (key,value) in set_data[k]['distinct_cards'].items() if value[0]['is_rakdos'] }
        distinct_rakdos_card_count = len(distinct_rakdos_cards)

        print("{}\t{}\t{}\t{}\t{}\t{}".format(set_id,name,total_set_size,base_set_size,distinct_card_count,distinct_rakdos_card_count))

        file_name = "all_cards_" +  set_id + ".txt"
        print_card_tsv(file_name,set_data[k]['distinct_cards'])

        file_name = "rakdos_cards_" + set_id + ".txt"
        print_card_tsv(file_name,distinct_rakdos_cards)

    sub_counts = {}
    for k in sets:
       for st in set_data[k]['subtype_counts'].items():
           sub_type = st[0]
           sub_counts[sub_type] = sub_counts.get(sub_type,0) + st[1]
    
    with open("./resources/magic/OUT/subtype_pivot_table.txt", "w") as card_file:    
         header = "subtype\t" + ('\t').join(sets) + '\ttotal\n'
         card_file.write(header)
         for st in sorted(sub_counts.keys()):
             card_file.write(st)
             for s in sets:
                 card_file.write('\t')
                 card_file.write(str(set_data[s]['subtype_counts'].get(st,'')))
             card_file.write('\t')
             card_file.write(str(sub_counts[st]))    
             card_file.write('\n')
             
         
    with open("./resources/magic/OUT/subtype_set_counts.txt", "w") as card_file:
             card_file.write('set\tsubtype\tcount\n')
             for k in sets:
               for st in set_data[k]['subtype_counts'].items():
                 card_file.write(k + '\t' + st[0] + '\t'+ str(st[1]) + '\n')
                 
def subtype_counts(card_map):
  subtype_counts = {}
  for c in card_map.values():
    for st in c[0]['subtypes']:
            subtype_counts[st] = subtype_counts.get(st,0) + 1
  return subtype_counts
               
main()    
