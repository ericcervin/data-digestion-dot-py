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
                if "UpdateDeckV3" in ent:
                    m = re.search(r'\"name\":"(.*)\",\"description\":\"(.*)\",\"format\"',ent)
                    if m:
                       deck_name = m.group(1)
                       #print(deck_name)
                
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
                    #print(opponent + '\t' + opp_rank + '\t' + player1)
                m = re.search(r'systemSeatId\": 1(.*)playerName(.*)systemSeatId\": 2, \"teamId\"',ent)
                if m:
                    player2 = m.group(2)[4:-4]
                    #print(opponent + '\t' + opp_rank + '\t' + player1 + '\t' + player2)

                m = re.search(r'{ \"scope\": \"MatchScope_Game\", \"result\": \"ResultType_WinLoss\", \"winningTeamId\": (\d) }',ent)
                if m:
                    winning_team = m.group(1)
                    if (winning_team == "1"):
                        winner_id = player1
                    else:
                        winner_id = player2
                    print(opponent + '\t' + opp_rank + '\t' + player1 + '\t' + player2 + '\t' + winner_id + '\t' + deck_name)

                    
{ "scope": "MatchScope_Game", "result": "ResultType_WinLoss", "winningTeamId": 1 }

def main():
    load_log_data()

main()
