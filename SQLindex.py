#Import moduler
from importlib import import_module
from multiprocessing import connection
from User import User
from Post import Post
import sqlite3

#Sjekker databasetilkobling
def chk_conn(conn):
    try:
        conn.cursor()
        return True
    except Exception as ex:
        return False

#Kobler til databasen
connection = sqlite3.connect('coffee.db')
cursor = connection.cursor()
print(f"Connection: {chk_conn(connection)}")

#Registerer bruker
def insert_user(user):
    with connection:
        cursor.execute("INSERT INTO User VALUES (:mail, :password, :firstName, :lastName)", {
                       'mail': user.mail, 'password': user.password, 'firstName': user.firstName, 'lastName': user.lastName})

#Lage en post
def insert_post(post):
    with connection:
        cursor.execute("INSERT INTO Post (mail, coffeeID, note, score, date) VALUES (:mail, :coffeeID, :note, :score, :date)", {
            'mail': post.mail[0], 'coffeeID': post.coffeeID[0], 'note': post.note[0], 'score': post.score[0], 'date': post.date})

#Hente passord for validering
def get_password(mail):
    cursor.execute(
        "SELECT password FROM User WHERE mail=:mail", {'mail': mail})
    return cursor.fetchone()

#Hente kaffeID
def getCoffeeID(Cname, Rname):
    cursor.execute(
        "SELECT coffeeID From Coffee WHERE coffeeName = :Cname AND roasteryID = (SELECT roasteryID from CoffeeRoastery WHERE name = :name)", {'Cname': Cname, 'name': Rname})
    return cursor.fetchone()

#Hente liste over bruker som har smakt flest unike kaffer
def get_mostcoffee():
    cursor.execute(
        "SELECT User.firstName, COUNT(DISTINCT Post.coffeeID) AS total from Post Inner join User on Post.mail = User.mail WHERE Post.date like '%2022%' group by User.firstName ORDER BY total DESC;")
    return cursor.fetchall()

#Hente liste over kaffe som gir mest for pengene
def get_mostvalue():
    cursor.execute(
        "SELECT CoffeeRoastery.name, Coffee.coffeeName, Coffee.priceKG, AVG(Post.score), Coffee.priceKG/AVG(Post.score) AS prisperpoeng from Post INNER JOIN Coffee ON Coffee.coffeeID = Post.coffeeID INNER JOIN CoffeeRoastery ON CoffeeRoastery.roasteryID = Coffee.roasteryID GROUP BY Coffee.coffeeName ORDER BY prisperpoeng;")
    return cursor.fetchall()

#Søke i beskrivelse
def get_search(search):
    cursor.execute(
        "SELECT DISTINCT Coffee.coffeeName, CoffeeRoastery.name FROM Coffee INNER JOIN CoffeeRoastery ON Coffee.roasteryID = CoffeeRoastery.roasteryID INNER JOIN Post ON Post.coffeeID = Coffee.coffeeID WHERE Post.note LIKE :search OR Coffee.description LIKE :search", {'search': '%'+search+'%'})
    return cursor.fetchall()

#Søk etter land
def get_search_not_washed(country):
    cursor.execute(
        "SELECT DISTINCT Coffee.coffeeName, CoffeeRoastery.name FROM Coffee INNER JOIN CoffeeRoastery ON Coffee.roasteryID = CoffeeRoastery.roasteryID INNER Join Batch on Coffee.batchID = Batch.batchID INNER JOIN Farm on Batch.farmID = Farm.farmID INNER Join ProcessingMethod on Batch.methodID = ProcessingMethod.methodID WHERE ProcessingMethod.name LIKE '%tørket%' AND Farm.country LIKE :country OR Farm.country LIKE :country", {'country': '%'+country+'%'})
    return cursor.fetchall()
