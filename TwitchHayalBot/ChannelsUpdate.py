import time
import mysql.connector
import json

def LoadApi():
    db = mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="hayalbot"
    )

    while True:
        db.connect()
        conn = db.cursor()
        conn.execute("SELECT * FROM hayalbotStreamers")

        result = conn.fetchall()
        veri = {}
        for x in result:

            valorantjson = json.loads(x[1].decode("utf-8")) if x[1] is not None else ""
            valorant = valorantjson

            loljson = json.loads(x[2]) if x[2] is not None else ""
            lol = loljson

            csgojson = json.loads(x[3].decode("utf-8")) if x[3] is not None else ""
            csgo = csgojson


            veri[x[0]] = {"Valorant":valorant,
                        "LOL":lol,
                        "CSGO":csgo}


        print(veri)


        folder = open("Channels.json", "w")
        folder.write(json.dumps(veri))
        folder.close()
        time.sleep(5)
LoadApi()