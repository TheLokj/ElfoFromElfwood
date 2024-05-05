# -*- coding: utf-8 -*-
from bs4 import BeautifulSoup
from mastodon import Mastodon
import urllib.request, tweepy, random, datetime

# Déclaration des variables
liste_mois = ["janvier", "février", "mars", "avril", "mai", "juin", "juillet", "aout", "septembre", "octobre", "novembre", "décembre"]
liste_hashtag_jour = ["#monday", "#tuesday", "#wednesday", "#thursday", "#friday", "#saturday", "#sunday"]

#Détermination de la date
now = datetime.datetime.today()
jour, mois, annee = int(now.day), int(now.month), int(now.year)

# Authentification sur sur l'API de Twitter
auth = tweepy.OAuthHandler("", "")
auth.set_access_token("","")
api = tweepy.API(auth)

# Vérification de l'authentification Twitter
try:
    api.verify_credentials()
    print("Authentification Twitter fonctionelle")
except:
    print("Erreur d'authentification Twitter")

# Authentification sur l'API Mastodon
mast_ID = ""
mast_secret = ""
mast_token = ""
mastodon = Mastodon(
    access_token = mast_token,
    api_base_url = ''
)

print("Authentification Mastondon fonctionelle")

def scrapdicton(jour, mois):
    # Récupération du code HTML et récupération des fragments HTML contenant les dictons
    lien = 'https://fr.wikipedia.org/wiki/{0}_'.format(jour) + urllib.parse.quote(mois)
    wikipage = urllib.request.urlopen(lien)
    soup = BeautifulSoup(wikipage, 'html.parser', from_encoding="utf-8")
    liste_dictons = []
    print("#1 - Scrap réussi")
    if len(str(soup).split("<li>«"+u"\xA0")) != 1:
        clef = str(soup).split("<li>«"+u"\xA0")
    else :
        clef = str(soup).split("<p>«" + u"\xA0")
    print("split réussi")
    try :
        for i in range(len(clef)-1) : 
            dicton = clef[i+1].split("»")[0]
            # On supprime les mots entre parenthèses
            while "(" and ")" in dicton:
                p = dicton.count("(")
                if p == 1:
                    dicton = dicton.split("(")[0] + dicton.split(")")[1]
                if p == 2:
                    dicton = dicton.split("(")[0] + dicton.split(")")[1] + dicton.split("(")[1] + dicton.split(")")[2]
            while "<" and ">" in dicton:
                dictonsoup = BeautifulSoup(dicton, 'html.parser')
                dicton = dictonsoup.get_text()
            # On enlève les codes réferences :
            while "[" and "]" in dicton:
                r = dicton.count("[")
                if r == 1:
                    dicton = dicton.split("[")[0] + dicton.split("]")[1]
                if r == 2:
                    dicton = dicton.split("[")[0] + dicton.split("]")[1] + dicton.split("[")[2]
            # Correction des potentielles erreurs synthaxiques
            if "." not in dicton:
                dicton = dicton + "."
            if "\xA0." in dicton:
                dicton = dicton.replace(u"\xA0.", ".")
            if "  " in dicton:
                dicton = dicton.replace("  ", " ")
            if " ," in dicton:
                dicton = dicton.replace(" ,", ",")
            if "\xa0" in dicton:
                dicton = dicton.replace("\xa0", "")
            if " ." in dicton:
                dicton = dicton.replace(" .", ".")
            if dicton.find("Journée")+dicton.find("internationale")+dicton.find("mondiale") < -2:
                if len(dicton) > 25 :
                    liste_dictons.append(dicton)
    except :
        print("Erreur inconnue")
        liste_dictons.append("Erreur inconnue")
    return liste_dictons

def randompick(liste_dictons):
    if len(liste_dictons) == 0:
            liste_dictons.append("Aucun dicton")
    dicton_final = random.choice(liste_dictons)
    return dicton_final

def checkandpost(jour, mois, annee, dicton_final):
    e1, e2, e3, e4 = False, False, False, False
    # Vérification de la présence d'erreur et envoie du rapport par message privé
    if dicton_final.find("(")+dicton_final.find(")") != -2:
        e1 = True
        api.send_direct_message("", "[ERREUR]\nDate : {0}/{1}/{2}\nRaison : présence d'une parenthèse\n« {3} »".format(jour, mois, annee, dicton_final))
    if dicton_final.find("<")+dicton_final.find(">") != -2:
        e2 = True
        api.send_direct_message("", "[ERREUR]\nDate : {0}/{1}/{2}\nRaison : présence de code HTML\n« {3} »".format(jour, mois,annee,dicton_final))
    if dicton_final.find("Aucun dicton") != -1:
        e3 = True
        api.send_direct_message("", "[ERREUR]\nDate : {0}/{1}/{2}\nRaison : pas de dicton pour aujourd'hui\n".format(jour, mois, annee))
    if dicton_final.find("Erreur inconnue") != -1:
        e4 = True
        api.send_direct_message("", "[ERREUR]\nDate : {0}/{1}/{2}\nRaison : inconnue".format(jour, mois, annee))
    # Publication du tweet si il n'y a pas d'erreur
    if e1 is False and e2 is False and e3 is False and e4 is False:
        # Publication du tweet
        mastodon.toot(dicton_final + " " + liste_hashtag_jour[int(now.weekday())])
        try :
            api.update_status(dicton_final, place_id="Steamland")
        except :
            pass
        print("{0}/{1}/{2} ".format(jour, mois, annee) + dicton_final + " Publié")
    else :
        print("{0}/{1}/{2} ".format(jour, mois, annee) + dicton_final + " Non publié")

liste_dictons = scrapdicton(int(jour), liste_mois[mois-1])
print("Liste des dictons du jour récupérée")
dicton_final = randompick(liste_dictons)
print("Dicton du jour choisis")
checkandpost(jour, mois, annee, dicton_final)

