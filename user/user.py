from flask import Flask, render_template, request, jsonify, make_response
import requests
import json
import grpc
import booking_pb2
import booking_pb2_grpc
import movie_pb2
import movie_pb2_grpc
from google.protobuf.json_format import MessageToJson

app = Flask(__name__)

PORT = 3004
HOST = '0.0.0.0'

with open('{}/data/users.json'.format("."), "r") as jsf:
   users = json.load(jsf)["users"]

"""
DESCRIPTION : Retourne le détail des films réservés par un utilisateur
ENTRÉE : Un userid 
SORTIE : Une liste de type Bookings
"""
@app.route("/user/booking/details/<userid>", methods=['GET'])
def get_user_bookings_infos(userid):
    for user in users:
        if str(user["id"]) == str(userid):  # On récupère le bon utilisateur
            with grpc.insecure_channel('localhost:3003') as channel:
                stub = booking_pb2_grpc.BookingStub(channel)
                bookingsUser = stub.GetBookingForUser(booking_pb2.UserId(userid=userid))
                allMovieList = []
                with grpc.insecure_channel('localhost:3001') as channel:
                    stub = movie_pb2_grpc.MovieStub(channel)
                    for date in bookingsUser.dates:
                        # pour chaque date dans lequel l'utilisateur à au moins une réservation, on récupère le détail de ces films
                        movieListDetailed = []
                        for movie in date.movies:
                            movieDetailed = stub.GetMovieByID(movie_pb2.MovieID(id=movie))
                            movieDetailedJson = {"title": movieDetailed.title, "rating": movieDetailed.rating, "director": movieDetailed.director, "id": movieDetailed.id}
                            movieListDetailed.append(movieDetailedJson)
                        allMovieList.append({"movies": movieListDetailed, "date": date.date})
                    bookingsUser = allMovieList # une fois tout le parcours effectué, on remplace la liste des dates par la
                    # version actualisée contenant le détail de chaque film
                channel.close()
                return make_response(jsonify(bookingsUser), 200)
            channel.close()
    return make_response(jsonify({"error": "incorrect userid"}), 400)

"""
DESCRIPTION : Retourne les réservations d'un utilisateur
ENTRÉE : Un username ou userid en argument de la requête
SORTIE : Une liste de type Bookings
"""
@app.route("/user/bookings", methods=['GET'])
def get_booking_from_username_or_userid():
    bookings = ""
    if request.args:
        req = request.args
        found = False
        with grpc.insecure_channel('localhost:3003') as channel:
            stub = booking_pb2_grpc.BookingStub(channel)
            for user in users:
                if ("id" in req and str(user["id"]) == str(req["id"])) or ("name" in req and str(user["name"]) == str(req["name"])):
                    # cette condition permet de rechercher l'utilisateur en fonction de son nom et de son id
                    # on peut passer le nom ou l'id en argument de la requête
                    found = True
                    bookings = stub.GetBookingForUser(booking_pb2.UserId(userid=str(user["id"])))
        channel.close()
        if not found:
            res = make_response(jsonify({"error": "User not found"}), 400)
        else:
            res = MessageToJson(bookings)
    else:
        res = make_response(jsonify({"error": "No argument passed"}), 400)
    return res

if __name__ == "__main__":
   print("Server running in port %s"%(PORT))
   app.run(host=HOST, port=PORT)
