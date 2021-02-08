#data files from https://mtgjson.com/

import json

sets = ['KHM','M21','ZNR','IKO','THB','ELD']

def main():
    #files from https://mtgjson.com/

    set_data = load_set_data(sets)
    #print set_data.keys()
    for k in set_data.keys():
        set_id = k
        name = set_data[k]['name']
        total_set_size = set_data[k]['total_set_size']
        base_set_size = set_data[k]['base_set_size']
        distinct_card_count = len(set_data[k]['distinct_cards'])

        distinct_rakdos_cards = {key:value for (key,value) in set_data[k]['distinct_cards'].items() if value[0]['is_rakdos'] }
        distinct_rakdos_card_count = len(distinct_rakdos_cards)

        print("{}\t{}\t{}\t{}\t{}\t{}".format(set_id,name,total_set_size,base_set_size,distinct_card_count,distinct_rakdos_card_count))

        file_name = "all_cards_" +  set_id + ".txt"
        print_card_tsv(file_name,set_data[k]['distinct_cards'])

        file_name = "rakdos_cards_" + set_id + ".txt"
        print_card_tsv(file_name,distinct_rakdos_cards)






            

def brief_card_map(card_json):
   return {'set_code': card_json.get('setCode',''),
           'name':  card_json.get('name',''),
           'type': card_json.get('type',''),
           'number': card_json.get('number',''),
           'color_id': card_json.get('colorIdentity',''),
           'is_rakdos': isRakdos(card_json.get('colorIdentity','')),
           'is_starter': card_json.get('isStarter','')
          }
    
def brief_card_text(card_map):
    return ('\t').join([
                 card_map['set_code'],
                 card_map['number'],
                 card_map['name'],
                 #card_map['type'].encode("ascii","ignore"),
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

def load_set_data(sets):
    set_data = {}
    for card_set in sets:
        with open("./resources/magic/IN/" + card_set + ".json", "r") as read_file:
            data = json.load(read_file)
            set_data[card_set] = {'raw_data' : data,
                                  'name' : data['data']['name'],
                                  'total_set_size' : data['data']['totalSetSize'],
                                  'base_set_size' : data['data']['baseSetSize'],
                                  'distinct_cards' : distinct_card_maps(data['data']['cards'])
                                  } 
    return set_data


def print_card_tsv(file_name,card_map):
    with open("./resources/magic/OUT/" + file_name, "w") as card_file:
             for k in card_map.keys():                     
               text = brief_card_text(card_map[k][0])
               card_file.write(text)
main()    
