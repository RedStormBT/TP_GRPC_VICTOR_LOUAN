import grpc
from concurrent import futures
import movie_pb2
import movie_pb2_grpc
import json


class MovieServicer(movie_pb2_grpc.MovieServicer):

    def __init__(self):
        with open('{}/data/movies.json'.format("."), "r") as jsf:
            self.db = json.load(jsf)["movies"]

    """
    DESCRIPTION : Retourne le film qui a pour id celui passé en paramètre de cette fonction
    ENTRÉE : MovieID
    SORTIE : MovieData
    """
    def GetMovieByID(self, request, context):
        for movie in self.db:
            if movie['id'] == request.id:
                print("Movie found!")
                return movie_pb2.MovieData(title=movie['title'], rating=float(movie['rating']),
                                           director=movie['director'],
                                           id=movie['id'])
        return movie_pb2.MovieData(title="", rating="", director="", id="")

    """
    DESCRIPTION : Retourne tous les films programmés pour une date donnée
    ENTRÉE : Director
    SORTIE : MovieData
    """
    def GetMovieByDirector(self, request, context):
        for movie in self.db:
            if movie['director'] == request.director:
                print("Movie found!")
                return movie_pb2.MovieData(title=movie['title'], rating=float(movie['rating']),
                                           director=movie['director'],
                                           id=movie['id'])
        return movie_pb2.MovieData(title="", rating="", director="", id="")

    """
    DESCRIPTION : Retourne tous les films
    SORTIE : MovieData
    """
    def GetListMovies(self, request, context):
        for movie in self.db:
            yield movie_pb2.MovieData(title=movie['title'], rating=float(movie['rating']), director=movie['director'],
                                      id=movie['id'])

    """
    DESCRIPTION : Retourne le film qui a pour titre celui passé en paramètre de cette fonction
    ENTRÉE : Director
    SORTIE : MovieData
    """
    def GetMovieByTitle(self, request, context):
        for movie in self.db:
            if movie['title'] == request.title:
                print("Movie found!")
                return movie_pb2.MovieData(title=movie['title'], rating=float(movie['rating']),
                                           director=movie['director'],
                                           id=movie['id'])
        return movie_pb2.MovieData(title="", rating="", director="", id="")

    """
    DESCRIPTION : Ajoute un film à la liste
    ENTRÉE : MovieData
    SORTIE : MovieData
    """
    def AddMovie(self, request, context):
        movie = {
            "title": request.title,
            "rating": request.rating,
            "director": request.director,
            "id": request.id,
        }
        self.db.append(movie)
        print("Movie added!")
        return movie_pb2.MovieData(title=request.title, rating=float(request.rating), director=request.director, id=request.id)

    """
    DESCRIPTION : Supprime un film
    ENTRÉE : MovieID
    SORTIE : MovieData
    """
    def DeleteMovie(self, request, context):
        for movie in self.db:
            if (movie["id"] == request.id):
                self.db.remove(movie)
                print("Movie found and deleted !")
        return movie_pb2.MovieData(title="", rating= float("0.0"), director="", id="")


def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    movie_pb2_grpc.add_MovieServicer_to_server(MovieServicer(), server)
    server.add_insecure_port('[::]:3001')
    server.start()
    server.wait_for_termination()


if __name__ == '__main__':
    serve()
