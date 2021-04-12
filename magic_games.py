import json, sqlite3, os, re, datetime
#imports Player.log files created by Magic Arena
#enable Detailed Logs in Arena

def load_log_data():
    logs = os.listdir("./resources/magic/IN/arena_logs/")
    log_data = []
    for lg in logs:
        with open("./resources/magic/IN/arena_logs/" + lg, "r") as log_file:
            whole_file = log_file.read()
            matches = whole_file.split('[UnityCrossThreadLogger]<== Event.MatchCreated')
            for mtch in matches:
                timestamps=[]
                log_entries = mtch.split("[UnityCrossThreadLogger]")
                for ent in log_entries:    
                  if "UpdateDeckV3" in ent:
                      m = re.search(r'\"name\":"(.*)\",\"description\":\"(.*)\",\"format\"',ent)
                      if m and len(m.group(1)) < 100:
                         deck_name = m.group(1)
                         
                  m = re.search(r'opponentScreenName(.*)opponentIsWotc',ent)
                  if m:
                      opponent = m.group(1)[3:-3]

                  m = re.search(r'matchId(.*)opponentRankingClass',ent)
                  if m:
                      matchID = m.group(1)[3:-3]

                  m = re.search(r'opponentRankingClass(.*)opponentRankingTier',ent)
                  if m:
                      opp_rank = m.group(1)[3:-3]
                      
                  m = re.search(r'playerName(.*)systemSeatId\": 1, \"teamId\"',ent)
                  if m:
                      player1 = m.group(1)[4:-4]
                      
                  m = re.search(r'systemSeatId\": 1(.*)playerName(.*)systemSeatId\": 2, \"teamId\"',ent)
                  if m:
                      player2 = m.group(2)[4:-4]


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
                      end_time = ticks_to_time(game_end)
                      start_time = ticks_to_time(game_start)
                      game_date = "{}{:02d}{:02d}".format(start_time.year,start_time.month,start_time.day)
                      game_data = {"log":lg,
                                   "opponent":opponent,
                                   "opponent_rank":opp_rank,
                                   "player_1": player1,
                                   "player_2": player2,
                                   "winner_id": winner_id,
                                   "deck_name": deck_name,
                                   "game_start_time": str(start_time),
                                   "game_end_time": str(end_time),
                                   "date": game_date,
                                   "game_length": str(ticks_to_seconds_dur(game_start,game_end)/60),
                                   "match_id": matchID 
                                   }
                      log_data.append(game_data)        
    return log_data               

def arena_games_report(log_data):
    with open("./resources/magic/OUT/arena_games.txt", "w") as out:
        header = ('\t').join(["log","date","opponent","opponent_rank","player_1","player_2","winner_id","deck_name","game_start_time","game_end_time","game_duration_mins","match_id"]) + "\n"
        out.write(header)
        for gm in log_data:
          game = ('\t').join([gm["log"],gm["date"],gm["opponent"],gm["opponent_rank"],gm["player_1"],gm["player_2"],gm["winner_id"],gm["deck_name"],gm["game_start_time"],gm["game_end_time"],gm["game_length"],gm["match_id"]])
          out.write(game + '\n')

def games_per_day_report():
    conn = sqlite3.connect('./resources/magic/OUT/magic.db')
    conn.text_factory = str
    
    c = conn.cursor()

    with open("./resources/magic/OUT/arena_games_per_day_count.txt", "w") as out:
        out.write("date\tcount\n")
        for row in c.execute('SELECT date, count(date) FROM game group by date'):
             out.write(row[0] + '\t' + str(row[1]) + '\n')
    
    conn.close()
    

def recreate_game_db(log_data):
    conn = sqlite3.connect('./resources/magic/OUT/magic.db')
    conn.text_factory = str
    
    c = conn.cursor()
    
    
    try:
      c.execute('''DROP TABLE game''')
    except:
      pass
    
    c.execute('''CREATE TABLE game
             (log text, date text, opponent text, opponent_rank text, player_1 text, player_2 text, winner_id text, deck_name text, game_start_time text, game_end_time text, game_length real, match_id text)''')  
    conn.commit()

    for gm in log_data:
        c.execute('INSERT INTO game VALUES (?,?,?,?,?,?,?,?,?,?,?,?)', (gm["log"],gm["date"],gm["opponent"],gm["opponent_rank"],gm["player_1"],gm["player_2"],gm["winner_id"],gm["deck_name"],gm["game_start_time"],gm["game_end_time"],gm["game_length"],gm["match_id"]))

    conn.commit()

    #for row in c.execute('SELECT * FROM game'):
    #   print(row)    

    conn.close()
    
def ticks_to_time(tk):
    ms = int(tk)//10
    dt = datetime.datetime(1, 1, 1) + datetime.timedelta(microseconds = ms) #GMT
    et = dt - datetime.timedelta(hours = 4) #EST
    return et

def ticks_to_seconds_dur(tk1,tk2):
    nano_sec_dur = int(tk2) - int(tk1)
    micro_sec_dur = nano_sec_dur//10
    dt = datetime.timedelta(microseconds = micro_sec_dur)
    return dt.total_seconds()

def main():  
      log_data = load_log_data()
      arena_games_report(log_data)
      recreate_game_db(log_data)
      games_per_day_report()

main()
