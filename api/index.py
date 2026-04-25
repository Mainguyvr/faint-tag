from datetime import datetime, timedelta
import requests
from flask import Flask, jsonify, request

app = Flask(__name__)

class GameInfo:
    def __init__(self):
        self.TitleId = "486AF"
        self.SecretKey = "99C3F4WAHESE6XCCGQ5HGUIR53RXC6GXJXI9IYXGHO91B5DEQZ"
        self.ApiKey = "OC|8806050836164414|b7841a799ddae2e7af7721a4409dc83e"

    def get_auth_headers(self):
        return {
            "Content-Type": "application/json",
            "X-SecretKey": self.SecretKey
        }

settings = GameInfo()

ACTIVE_SESSIONS = {}
SESSION_LIFETIME = timedelta(hours=8)

@app.route("/", methods=["GET", "POST"])
def main():
    return """
    <html>
        <head>
            <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;700&display=swap" rel="stylesheet">
        </head>
        <body style="font-family: 'Inter', sans-serif;">
            <h1 style="color: blue; font-size: 30px;">
                @kuda dosent skid
            </h1>
        </body>
    </html>
    """

@app.route("/api/TitleData", methods=["GET", "POST"])
def titledata():
    return jsonify({
        "AutoMuteCheckedHours": {"hours": 169},
        "AutoName_Adverbs": [
            "Cool","Fine","Bald","Bold","Half","Only","Calm","Fab",
            "Ice","Mad","Rad","Big","New","Old","Shy"
        ],
        "AutoName_Nouns": [
            "Gorilla","Chicken","Darling","Sloth","King","Queen",
            "Royal","Major","Actor","Agent","Elder","Honey",
            "Nurse","Doctor","Rebel","Shape","Ally","Driver","Deputy"
        ],
        "CreditsData": [
            {
                "Title": "<color=blue>UPDATE MAKERS/PLAYFAB MANAGERS</color>",
                "Entries": [
                    "KUDA",
                    "z",
                    "67"
                ]
            },
            {
                "Title": "<color=yellow>CREDITS TO</color>",
                "Entries": ["KUDA"]
            }
        ],
        "BundleBoardSign": "<color=#ff4141>https://discord.gg/4DV8HrPKHE</color>",
        "BundleKioskButton": "<color=#ff4141>https://discord.gg/4DV8HrPKHE</color>",
        "BundleKioskSign": "<color=#ff4141>https://discord.gg/4DV8HrPKHE</color>",
        "BundleLargeSign": "<color=#ff4141>https://discord.gg/4DV8HrPKHE</color>",
        "EnableCustomAuthentication": True,
        "LatestPrivacyPolicyVersion": "2024.09.20",
        "LatestTOSVersion": "2024.09.20",
        "MY CUTE FEMBOY ZEN": (
    
            "<color=#bb29ff>[ WELCOME TO VOLTAGE TAGGERS ]</color>\n"
            "<color=#07dde8>HALL 24!</color>\n"
            "<color=#ffff00>CREATOR/FOUNDER : ZENOX</color>\n"
            "<color=#969696>CREDITS TO: ZENOX!</color>\n"
            "<color=#ff8800>discord.gg/4DV8HrPKHE</color>\n"
            "<color=#000000>CHANGE YOUR NAME FROM GORILLA#### AS IT'S BANNABLE!</color>\n\n"
            "<color=#ffff00>YOUR PLAYFAB ID IS: " + currentPlayerId + "</color>"
        ),
        "UseLegacyIAP": False
    })

@app.route("/api/CachePlayFabId", methods=["POST"])
def cache_playfab_id():
    return jsonify({"Message": "Success"}), 200

@app.route("/api/PlayFabAuthentication", methods=["POST"])
def playfab_authentication():
    rjson = request.get_json() or {}

    required = ["Nonce", "AppId", "Platform", "OculusId"]
    missing = [x for x in required if not rjson.get(x)]

    if missing:
        return jsonify({
            "Message": f"Missing parameter(s): {', '.join(missing)}",
            "Error": "BadRequest"
        }), 400

    if rjson["AppId"] != settings.TitleId:
        return jsonify({
            "Message": "Wrong App ID",
            "Error": "AppIdMismatch"
        }), 400

    login = requests.post(
        f"https://{settings.TitleId}.playfabapi.com/Server/LoginWithServerCustomId",
        headers=settings.get_auth_headers(),
        json={
            "ServerCustomId": "OCULUS" + rjson["OculusId"],
            "CreateAccount": True
        }
    )

    if login.status_code != 200:
        return jsonify({
            "Error": "PlayFab Error",
            "Message": login.text
        }), login.status_code

    data = login.json()["data"]

    playfab_id = data["PlayFabId"]
    session_ticket = data["SessionTicket"]
    entity_token = data["EntityToken"]["EntityToken"]

    ACTIVE_SESSIONS[playfab_id] = {
        "SessionTicket": session_ticket,
        "EntityToken": entity_token,
        "Expires": datetime.utcnow() + SESSION_LIFETIME
    }

    return jsonify({
        "PlayFabId": playfab_id,
        "SessionTicket": session_ticket,
        "EntityToken": entity_token
    })

@app.route("/api/photon", methods=["POST"])
def photon_auth():
    data = request.get_json() or {}

    ticket = data.get("Ticket")
    nickname = data.get("username")

    if not ticket:
        return jsonify({
            "resultCode": 2,
            "message": "Invalid token"
        })

    playfab_id = ticket.split("-")[0]
    session = ACTIVE_SESSIONS.get(playfab_id)

    if not session or session["Expires"] < datetime.utcnow():
        ACTIVE_SESSIONS.pop(playfab_id, None)
        return jsonify({
            "resultCode": 2,
            "message": "Invalid or expired token"
        })

    return jsonify({
        "resultCode": 1,
        "message": "Success",
        "userId": playfab_id,
        "nickname": nickname
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=9080)
