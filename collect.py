import requests
import urllib
import json
import os

AUTH_KEY = os.environ.get("auth_key")
SERVER_ID = os.environ.get("server_id")

logFlags = [
  "disconnected",
  ") placed ",
  "connected",
  "hit by",
  "regained consciousne",
  "is unconscious",
  "killed by",
  ")Built ",
	"folded Fence",
  ")Player SurvivorBase",
  ") died.",
  ") committed suicide",
  ")Dismantled",
  ") bled"
]
players = {}
players['players'] = []


# Download Raw Logs off Nitrado
def getRawLogs():
  data = requests.get(
          f"https://api.nitrado.net/services/{SERVER_ID}/gameservers/file_server/download",
          headers={
            "Authorization": AUTH_KEY
          }, json={
            "file": "/games/ni5350965_2/noftp/dayzxb/config/DayZServer_X1_x64.ADM"
          }).json()

  url = data['data']['token']['url']
  urllib.request.urlretrieve(url, "logs.ADM")


# Convert Raw Logs into cleaned logs (only positional data logs)
def cleanLogs():
  with open("logs.ADM", "r") as logs:
    lines = logs.readlines()
  # Isolate Player logs (Removes Connect, Disconnect, place, hit)
  with open("clean.txt", "w") as logs:
    for line in lines:
      if not any(flag in line for flag in logFlags) and "| Player" in line.strip("\n"):
        logs.write(line)


# Generate Lost of player names and id's
def collectPlayerData():
  # Get player name
  with open("clean.txt", "r") as logs:
    cleanLines = logs.readlines()
    for line in cleanLines:
      beginPlayer = 19 # Player names always start here
      endPlayer = line.strip("\n").find('(')-2
      playerName = line.strip("\n")[beginPlayer:endPlayer]
      
      # Get player ID
      beginID = line.strip("\n").find('(id=')+4
      endID = line.strip("\n").find("pos=<")-1
      playerID = line.strip("\n")[beginID:endID]
      
      # Get current player pos
      beginPos = line.strip("\n").find("pos=<")+5
      endPos = len(line.strip("\n"))-2
      playerPos = line.strip("\n")[beginPos:endPos].split(", ")
      for n in range(len(playerPos)): playerPos[n] = float(playerPos[n])

      # Get Log Time
      logTime = line.strip("\n")[0:8]+" EST"

      query = {
        "gamertag": playerName,
        "playerID": playerID,
        "time": logTime,
        "pos": playerPos,
        "posHistory": []
      }

      if len(players['players'])==0:
        players['players'].append(query)
      else:
        for i in range(len(players['players'])):
          if players['players'][i]['gamertag']==playerName:
            # Updates Existing player data
            for j in range(len(players["players"][i]["posHistory"])):
              query["posHistory"].append({
                "time": players['players'][i]['posHistory'][j]['time'],
                "pos":  players['players'][i]['posHistory'][j]['pos']
              })
            query["posHistory"].append({
              "time": players['players'][i]['time'],
              "pos":  players['players'][i]['pos']
            })

            players['players'].remove(players['players'][i])
            break

        # Logs new player data
        players['players'].append(query)

  with open("players.json", "w") as playerJSON:
    json.dump(players, playerJSON, ensure_ascii=False, indent=2)


if __name__ == '__main__':
  getRawLogs()
  cleanLogs()
  collectPlayerData()
