import json, sqlite3, os, re

def load_log_data():
    logs = os.listdir("./resources/magic/IN/arena_logs/")
    #log_data = []
    for lg in logs:
        print(lg)
        with open("./resources/magic/IN/arena_logs/" + lg, "r") as log_file:
            whole_file = log_file.read()
            log_entries = whole_file.split('[UnityCrossThreadLogger]<== Event.MatchCreated')
            print(len(log_entries))
            for ent in log_entries:
                m = re.search(r'opponentScreenName(.*)opponentIsWotc',ent)
                if m:
                    opponent = m.group(1)[3:-3]
                    #print(opponent)

                m = re.search(r'opponentRankingClass(.*)opponentRankingTier',ent)
                if m:
                    opp_rank = m.group(1)[3:-3]
                    #print(opponent + '\t' + opp_rank)
                m = re.search(r'playerName(.*)systemSeatId\": 1, \"teamId\"',ent)
                if m:
                    player1 = m.group(1)[4:-4]
                    print(opponent + '\t' + opp_rank + '\t' + player1)

                    
#playerName": "Enrico Suave#82067", "systemSeatId": 2
#playerName": "Enrico Suave#82067", "systemSeatId": 2

def main():
    load_log_data()

main()
