#json data files from https://mtgjson.com/downloads/all-sets/

import json, sqlite3

sets = ['AKH','HOU','XLN','RIX','DOM','M19','GRN','RNA','WAR','M20','ELD','THB','IKO','M21','ZNR','KHM']

def main():
    #files from https://mtgjson.com/

    set_data = load_set_data(sets)
    export_magic_db()
    
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
    

    #for st in sorted(sub_counts.keys()):
    #    print(st + "\t" + str(sub_counts[st]))
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

def brief_card_map(card_json):
   return {'set_code': card_json.get('setCode',''),
           'name':  card_json.get('name',''),
           'type': card_json.get('type',''),
           'types': card_json.get('types',''),
           'subtypes': card_json.get('subtypes',''),
           'supertypes': card_json.get('supertypes',''),
           'number': card_json.get('number',''),
           'color_id': card_json.get('colorIdentity',''),
           'is_rakdos': isRakdos(card_json.get('colorIdentity','')),
           'is_starter': card_json.get('isStarter',''),
           'cmc': card_json.get('convertedManaCost','')
          }
    
def brief_card_text(card_map):
    return ('\t').join([
                 card_map['set_code'],
                 card_map['number'].replace('\u2605',''),
                 card_map['name'],
                 str(card_map['cmc']),
                 card_map['type'].encode("ascii","ignore"),
                 (',').join(card_map['color_id']),
                 #str(card_map['is_rakdos'])
                 ]) + '\n'

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


def export_magic_db():
    conn = sqlite3.connect('./resources/magic/OUT/magic.db')
    
    c = conn.cursor()
    
    try:
      c.execute('''DROP TABLE cards''')
    except:
      pass
    
    c.execute('''CREATE TABLE cards
             (set_code text, number integer, name text, cmc real, type text, color_id text )''')
              
    conn.commit()

    conn.close()
    
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
    with open("./resources/magic/OUT/" + file_name, "w") as card_file:
             for c in sorted_cards:
               #print(c[0] + '\t' + str(len(c[1])))
               text = brief_card_text(c[1][0]).encode('utf-8')
               card_file.write(text)

def subtype_counts(card_map):
  subtype_counts = {}
  for c in card_map.values():
    for st in c[0]['subtypes']:
            subtype_counts[st] = subtype_counts.get(st,0) + 1
  return subtype_counts
               
main()    
