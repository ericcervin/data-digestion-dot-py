import json, sqlite3, os, re, datetime

def load_log_data():
    logs = os.listdir("./resources/magic/IN/arena_logs/")
    log_data = []
    for lg in logs:
        with open("./resources/magic/IN/arena_logs/" + lg, "r") as log_file:
            whole_file = log_file.read()
            matches = whole_file.split('[UnityCrossThreadLogger]<== Event.MatchCreated')
            #print(len(log_entries))
            for mtch in matches:
                timestamps=[]
                log_entries = mtch.split("[UnityCrossThreadLogger]")
                for ent in log_entries:    
                  if "UpdateDeckV3" in ent:
                      m = re.search(r'\"name\":"(.*)\",\"description\":\"(.*)\",\"format\"',ent)
                      if m and len(m.group(1)) < 100:
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


                  timestamp = re.findall(r'timestamp\": \"(\d\d\d\d\d\d\d\d\d\d\d\d\d\d\d\d\d\d)',ent)
                  if timestamp:
                    timestamps.append(timestamp[0])
                  
                  m = re.search(r'{ \"scope\": \"MatchScope_Game\", \"result\": \"ResultType_WinLoss\", \"winningTeamId\": (\d) }',ent)
                  if m:
                      winning_team = m.group(1)
                      if (winning_team == "1"):
                          winner_id = player1
                      else:
                          winner_id = player2

                      game_end = str(timestamps[-1])
                      game_start = str(timestamps[0])
                      game_data = {"log":lg,
                                   "opponent":opponent,
                                   "opponent_rank":opp_rank,
                                   "player_1": player1,
                                   "player_2": player2,
                                   "winner_id": winner_id,
                                   "deck_name": deck_name,
                                   "game_start_time": ticks_to_time(game_start),
                                   "game_end_time": ticks_to_time(game_end) 
                                   }
                      log_data.append(game_data)
                      # print(lg + '\t' + opponent + '\t' + opp_rank + '\t' + player1 + '\t' + player2 + '\t' + winner_id + '\t' + deck_name + '\t' + ticks_to_time(game_start) +'\t' + ticks_to_time(game_end))
    return log_data               

def ticks_to_time(tk):
    ms = int(tk)//10
    dt = datetime.datetime(1, 1, 1) + datetime.timedelta(microseconds = ms) #GMT
    et = dt - datetime.timedelta(hours = 4) #EST
    return str(et)

def main():
    with open("./resources/magic/OUT/arena_games.txt", "w") as out:
      log_data = load_log_data()
      header = ('\t').join(["log","opponent","opponent_rank","player_1","player_2","winner_id","deck_name","game_start_time","game_end_time"]) + "\n"
      out.write(header)
      for gm in log_data:
        game = ('\t').join([gm["log"],gm["opponent"],gm["opponent_rank"],gm["player_1"],gm["player_2"],gm["winner_id"],gm["deck_name"],gm["game_start_time"],gm["game_end_time"]])
        out.write(game + '\n')
main()
