import grpc
from concurrent import futures
import showtime_pb2
import showtime_pb2_grpc
import booking_pb2
import booking_pb2_grpc
import json


class BookingServicer(booking_pb2_grpc.BookingServicer):

    def __init__(self):
        with open('{}/data/bookings.json'.format("."), "r") as jsf:
            self.db = json.load(jsf)["bookings"]

    def GetJson(self, request, context):
        return booking_pb2.JsonBooking(bookings=self.db)

    def GetBookingForUser(self, request, context):
        for booking in self.db:
            if str(booking["userid"]) == str(request.userid):
                return booking_pb2.BookingData(userid=booking["userid"], dates=booking["dates"])
        return booking_pb2.BookingData(userid="", dates=[])

    def AddBookingForUser(self, request, context):

        # 1. On regarde si le film souhaité est bien programmé ce jour là
        with grpc.insecure_channel('localhost:3002') as channel:
            stub = showtime_pb2_grpc.ShowtimeStub(channel)
            scheduled = False
            schedules = stub.GetSchedulesPerDateJson(showtime_pb2.Date(date=request.date))
            for schedule in schedules.movies:
                if schedule == request.movieid:
                    scheduled = True
            if not scheduled:
                return booking_pb2.ResponseMessage(responseMessage="The movie you try to book is not available for this date")
        channel.close()

        # 2. On regarde si l'utilisateur n'a pas déjà réservé ce film pour la date souhaitée
        for booking in self.db:
            if str(booking["userid"]) == str(request.userid):
                for userBooking in booking["dates"]:
                    if userBooking["date"] == request.date:
                        for movieBooked in userBooking["movies"]:
                            if str(movieBooked) == str(request.movieid):
                                return booking_pb2.ResponseMessage(
                                    responseMessage="You already booked this movie for this date")
                        # si le film n'est pas déjà booké pour la date demandé, on l'ajoute
                        userBooking["movies"].append(request.movieid)
                        return booking_pb2.ResponseMessage(responseMessage="Booking added")
                # si le film n'est pas déjà booké et que l'utilisateur n'a rien réservé sur cette date,
                # on ajoute un item à "dates"
                jsonToAdd = {"date": request.date, "movies": [request.movieid]}
                booking["dates"].append(jsonToAdd)
        return booking_pb2.ResponseMessage(responseMessage="Booking added")



def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    booking_pb2_grpc.add_BookingServicer_to_server(BookingServicer(), server)
    server.add_insecure_port('[::]:3003')
    server.start()
    server.wait_for_termination()


if __name__ == '__main__':
    serve()