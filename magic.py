import json

#files from https://mtgjson.com/
set_files = ['KHM.json']
for set_json in set_files:
    with open("./resources/magic/IN/" + set_json, "r") as read_file:
        data = json.load(read_file)

        #print(type(data))
        #print(data.keys())
        #print(data['data'].keys())
        set_name = data['data']['name']
        #print(type(data['data']))
        #print(data['data'].keys())
        #print(type(data['data']['cards']))
        total_set_size = data['data']['totalSetSize']
        print(set_name + '\t' + str(total_set_size))
        #print(data['data']['cards'][0].keys())
        #print(data['data']['cards'][0])
        #print(data['data']['cards'][0]['text'].encode("utf-8"))
        with open("./resources/magic/OUT/allcards.txt", "w") as allcard_file:
          for i in data['data']['cards']:
              card_name = i.get('name','')
              card_number = i.get('number','')
              card_color_id = i.get('colorIdentity','')
              allcard_file.write(card_number.encode("utf-8") + '\t' + card_name.encode("utf-8") + '\t' + (' ').join(card_color_id) + '\n')
