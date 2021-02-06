import json

def main():
    #files from https://mtgjson.com/
    sets = ['KHM','M21','ZNR','IKO','THB','ELD']
    for card_set in sets:
        with open("./resources/magic/IN/" + card_set + ".json", "r") as read_file:
            data = json.load(read_file)
            set_name = data['data']['name']
            total_set_size = data['data']['totalSetSize']
            base_set_size = data['data']['baseSetSize']
            brief_card_maps = map(brief_card_map, data['data']['cards'])
            distinct_cards = {}
            distinct_rakdos_cards = {}
            for c in brief_card_maps:
                if distinct_cards.has_key(c['name']):
                    distinct_cards[c['name']].append(c)
                else:
                    distinct_cards[c['name']] = [c]
                if c['is_rakdos']:
                  if distinct_rakdos_cards.has_key(c['name']):
                      distinct_rakdos_cards[c['name']].append(c)
                  else:
                      distinct_rakdos_cards[c['name']] = [c]
            with open("./resources/magic/OUT/all_cards_" +  card_set + ".txt", "w") as all_card_file:
                 for dc in distinct_cards.keys():
                     text = brief_card_text(distinct_cards[dc][0])
                     all_card_file.write(text)
            with open("./resources/magic/OUT/rakdos_cards_" + card_set + ".txt", "w") as rakdos_card_file:
                 for dc in distinct_cards.keys():                     
                     if distinct_cards[dc][0]['is_rakdos']:
                        text = brief_card_text(distinct_cards[dc][0])
                        rakdos_card_file.write(text)
            rakdos_card_count = len(distinct_rakdos_cards)
            print(set_name + '\t' + str(total_set_size) + '\t' + str(base_set_size) + '\t' + str(rakdos_card_count))

def isRakdos(color_id):
    return (not (('U' in color_id) or ('W' in color_id) or ('G' in color_id)) )

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

main()    
