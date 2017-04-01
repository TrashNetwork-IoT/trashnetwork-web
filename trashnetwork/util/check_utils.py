from geopy.distance import vincenty


def check_location(longitude: float, latitude: float):
    if -180.0 <= longitude <= 180 and -90.0 <= latitude <= 90:
        return True
    return False


def check_distance(p1_longitude: float, p1_latitude: float, p2_longitude: float, p2_latitude: float, distance_limit: float):
    p1 = (p1_latitude, p1_longitude)
    p2 = (p2_latitude, p2_longitude)
    return float(vincenty(p1, p2).meters) <= distance_limit
