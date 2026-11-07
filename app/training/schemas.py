"""Training validation schemas using marshmallow."""

from marshmallow import Schema, fields, validate


class ExerciseSchema(Schema):
    """Validate exercise creation/update."""
    name = fields.String(
        required=True,
        validate=validate.Length(min=2, max=100,
                                 error='Tên bài tập phải từ 2 đến 100 ký tự.')
    )


class WorkoutPlanItemSchema(Schema):
    """Validate a single workout plan item."""
    exercise_id = fields.Integer(required=True)
    sets = fields.Integer(
        required=True,
        validate=validate.Range(min=1, max=20,
                                error='Số hiệp phải từ 1 đến 20.')
    )
    reps_per_set = fields.Integer(
        required=True,
        validate=validate.Range(min=1, max=100,
                                error='Số lần/hiệp phải từ 1 đến 100.')
    )
    weekdays = fields.String(
        required=True,
        validate=validate.Length(min=1,
                                 error='Phải chọn ít nhất 1 ngày tập.')
    )


class WorkoutPlanSchema(Schema):
    """Validate workout plan creation."""
    member_id = fields.Integer(required=True)
    items = fields.List(
        fields.Nested(WorkoutPlanItemSchema),
        required=True,
        validate=validate.Length(min=1,
                                 error='Kế hoạch phải có ít nhất 1 bài tập.')
    )
