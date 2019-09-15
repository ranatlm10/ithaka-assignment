from serializers import GetPlanRequestSerializer
from cache import cache


class IthakaService:

    @staticmethod
    @cache.memoize(timeout=3600)
    def get_preferred_route(data):
        request_data = GetPlanRequestSerializer().load(data)
        # ScheduleQuickSortService.sort(request_data['schedules'])
        route_map = IthakaService.create_route_map(request_data['schedules'])
        best_route = IthakaService.get_best_route(request_data['trip_plan']['start_city'],
                                                  request_data['preferred_time'],
                                                  request_data['trip_plan']['end_city'], route_map, set(), {})

        return {"flight_plan": best_route}

    @staticmethod
    def get_best_route(current_city, current_timestamp, destination_city, route_map, visited_cities, route_history):
        """
        Fetch best route based on parameters
        :param current_city: Current city
        :param current_timestamp: Timestamp in current city
        :param destination_city: Destination city
        :param route_map: Map for city-wise flight schedules
        :param visited_cities: set of visited cities in current route
        :param route_history: historic data for route
        :return: list of flights for reaching destination from current city at current timestamp (best scenario)
        """
        route_key = IthakaService.get_route_key(current_city, destination_city, current_timestamp)

        # Return historic data if present
        if route_key in route_history:
            return route_history[route_key]

        # Reached destination
        if current_city == destination_city:
            return [{"city": current_city, "timestamp": current_timestamp}]

        # Handling cycles
        if current_city in visited_cities:
            return None

        best_route = None

        # Iterate through all flights from current city
        for flight in route_map[current_city]:
            # Ignore flight if before current timestamp
            if flight['timestamp'] < current_timestamp:
                continue

            route = IthakaService.get_best_route(flight['destination']['city'],
                                                 flight['destination']['timestamp'], destination_city,
                                                 route_map, visited_cities | {current_city}, route_history)

            if route:
                if best_route is None or route[len(route) - 1]['timestamp'] < best_route[len(best_route) - 1]['timestamp']:
                    best_route = [{"city": current_city, "timestamp": flight['timestamp']}] + route

        # Save historic data for route
        route_history[route_key] = best_route

        return best_route

    @staticmethod
    def create_route_map(schedules):
        """
        Creates a map of flight schedule based on departure city
        :param schedules: List of flight schedules
        :return: Hashmap containing city-wise flight schedules
        """
        route_map = {}

        for schedule in schedules:
            from_city = schedule['departure']['city']
            from_timestamp = schedule['departure']['timestamp']
            to = schedule['arrival']

            if from_city not in route_map:
                route_map[from_city] = []

            route_map[from_city].append({"timestamp": from_timestamp, "destination": to})

        return route_map

    @staticmethod
    def get_route_key(from_city, to_city, timestamp):
        """
        Define route key string to store best route history
        :param from_city: From city
        :param to_city: To city
        :param timestamp: Timestamp
        :return: Route key
        """
        return "%s|%s|%d" % (from_city, to_city, timestamp)


class ScheduleQuickSortService:
    """
    Service to sort flight schedules based on departure timestamp
    """

    @staticmethod
    def sort(schedules):
        ScheduleQuickSortService.quick_sort(schedules, 0, len(schedules) - 1)

    @staticmethod
    def quick_sort(schedules, low, high):
        if low < high:
            pi = ScheduleQuickSortService.partition(schedules, low, high)

            ScheduleQuickSortService.quick_sort(schedules, low, pi - 1)
            ScheduleQuickSortService.quick_sort(schedules, pi + 1, high)

    @staticmethod
    def partition(schedules, low, high):
        """
        Partition method
        :param schedules: List of flight schedules
        :param low: Lowest index
        :param high: Highest index
        :return:
        """
        i = (low - 1)
        pivot = schedules[high]['departure']['timestamp']

        for j in range(low, high):

            if schedules[j]['departure']['timestamp'] <= pivot:
                i = i + 1
                schedules[i], schedules[j] = schedules[j], schedules[i]

        schedules[i + 1], schedules[high] = schedules[high], schedules[i + 1]
        return i + 1
