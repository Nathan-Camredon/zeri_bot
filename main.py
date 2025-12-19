#-------------------------------------------
#           Import
# ------------------------------------------
import sqlite3

#-------------------------------------------
#           Sqlite table definitions
# ------------------------------------------

sql_creation_joueurs = """
CREATE TABLE joueurs (
    discord_id INTEGER,
    pseudo TEXT
);
"""

sql_creation_disponibilite = """
CREATE TABLE disponibilite (
    discord_id INTEGER,
    jour INTEGER,
    heure_debut REAL,
    heure_fin REAL
);"""

#-------------------------------------------
#       SQL utilisation
#-------------------------------------------
# --- Création de la BDD ---

conn = sqlite3.connect("database.db")
cursor = conn.cursor()

#cursor.execute("INSERT INTO joueurs VALUES (123456789, 'PlayerOne');") # <-- On active !
#conn.commit()  # <-- On active la sauvegarde !

cursor.execute("SELECT * FROM joueurs;")
resultat = cursor.fetchall()
print("Voici les joueurs trouvés :")
print(resultat)

conn.close()
print("Connexion fermée.")
#-------------------------------------------
#           Import
# ------------------------------------------
import sqlite3

#-------------------------------------------
#           Sqlite table definitions
# ------------------------------------------

sql_creation_joueurs = """
CREATE TABLE joueurs (
    discord_id INTEGER,
    pseudo TEXT
);
"""

sql_creation_disponibilite = """
CREATE TABLE disponibilite (
    discord_id INTEGER,
    jour INTEGER,
    heure_debut REAL,
    heure_fin REAL
);"""

#-------------------------------------------
#       SQL utilisation
#-------------------------------------------
# --- Création de la BDD ---

conn = sqlite3.connect("database.db")
cursor = conn.cursor()

#cursor.execute("INSERT INTO joueurs VALUES (123456789, 'PlayerOne');") # <-- On active !
#conn.commit()  # <-- On active la sauvegarde !

cursor.execute("SELECT * FROM joueurs;")
resultat = cursor.fetchall()
print("Voici les joueurs trouvés :")
print(resultat)

conn.close()
print("Connexion fermée.")