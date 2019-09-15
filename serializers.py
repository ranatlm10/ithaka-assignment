from marshmallow import Schema, fields


class CityTimestamp(Schema):
    city = fields.String(required=True)
    timestamp = fields.Integer(required=True)


class ScheduleRequest(Schema):
    departure = fields.Nested(CityTimestamp, required=True)
    arrival = fields.Nested(CityTimestamp, required=True)


class TripPlanRequest(Schema):
    start_city = fields.String(required=True)
    end_city = fields.String(required=True)


class GetPlanRequestSerializer(Schema):
    schedules = fields.Nested(ScheduleRequest, required=True, many=True)
    trip_plan = fields.Nested(TripPlanRequest, required=True)
    preferred_time = fields.Integer(required=True)
