import grpc

import movie_pb2
import movie_pb2_grpc
import showtime_pb2
import showtime_pb2_grpc
import booking_pb2
import booking_pb2_grpc


def get_movie_by_id(stub, id):
    movie = stub.GetMovieByID(id)
    print(movie)


def get_list_movies(stub):
    allmovies = stub.GetListMovies(movie_pb2.Empty())
    for movie in allmovies:
        print("Movie called %s" % movie.title)


def get_movie_by_title(stub, title):
    movie = stub.GetMovieByTitle(title)
    print(movie)


def get_movie_by_director(stub, director):
    movie = stub.GetMovieByDirector(director)
    print(movie)


def add_movie(stub, movie):
    movie = stub.AddMovie(movie)
    print(movie)


def delete_movie(stub, id):
    stub.DeleteMovie(id)
    print("Movie deleted")


def get_json_showtime(stub):
    json = stub.GetJson(showtime_pb2.Empty2())
    print(json)

def get_booking_json(stub):
    json = stub.GetJson(booking_pb2.Empty4())
    print(json)

def get_schedule_per_date(stub, date):
    schedules = stub.GetSchedulesPerDate(date)
    for schedule in schedules:
        print(schedule)

def get_booking_for_user(stub, id):
    booking = stub.GetBookingForUser(id)
    print(booking)

def add_booking_for_user(stub, booking):
    response = stub.AddBookingForUser(booking)
    print(response)

def run():
    # NOTE(gRPC Python Team): .close() is possible on a channel and should be
    # used in circumstances in which the with statement does not fit the needs
    # of the code.
    with grpc.insecure_channel('localhost:3001') as channel:
        stub = movie_pb2_grpc.MovieStub(channel)
        print("-------------- GetMovieById --------------")
        id = movie_pb2.MovieID(id="a8034f44-aee4-44cf-b32c-74cf452aaaae")
        get_movie_by_id(stub, id)

        print("-------------- GetMovieList --------------")
        get_list_movies(stub)

        print("-------------- GetMovieByTitle --------------")
        title = movie_pb2.Title(title="The Martian")
        get_movie_by_title(stub, title)

        print("-------------- GetMovieByDirector --------------")
        director = movie_pb2.Director(director="Jonathan Levine")
        get_movie_by_director(stub, director)

        print("-------------- AddMovie --------------")
        movie = movie_pb2.MovieData(title="Avengers 1", rating=float(7.2), director="Joss Whedon", id="id-avengers")
        add_movie(stub, movie)

        # on visionne la liste pour voir le film ajouté
        print("-------------- GetMovieList --------------")
        get_list_movies(stub)

        print("-------------- DeleteMovie --------------")
        id = movie_pb2.MovieID(id="id-avengers")
        delete_movie(stub, id)

        # on visionne la liste pour voir que le film a été supprimé
        print("-------------- GetMovieList --------------")
        get_list_movies(stub)
    channel.close()

    with grpc.insecure_channel('localhost:3002') as channel:
        stub = showtime_pb2_grpc.ShowtimeStub(channel)
        print("-------------- GetJson for Showtime--------------")
        get_json_showtime(stub)


        print("-------------- GetSchedulePerDate --------------")
        date = showtime_pb2.Date(date="20151130")
        get_schedule_per_date(stub, date)
    channel.close()

    with grpc.insecure_channel('localhost:3003') as channel:
        stub = booking_pb2_grpc.BookingStub(channel)
        print("-------------- GetJson for Booking --------------")
        get_booking_json(stub)


        print("-------------- GetBookingForUser --------------")
        id = booking_pb2.UserId(userid="chris_rivers")
        get_booking_for_user(stub, id)

        print("-------------- AddBookingForUser --------------")
        booking = booking_pb2.SingleBook(userid="chris_rivers", date="20151201", movieid="39ab85e5-5e8e-4dc5-afea-65dc368bd7ab")
        add_booking_for_user(stub, booking)

        print("-------------- GetJson for Booking --------------")
        get_booking_json(stub)

    channel.close()



if __name__ == '__main__':
    run()
