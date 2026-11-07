"""Member validation schemas using marshmallow."""

from marshmallow import Schema, fields, validate, validates, ValidationError


class MemberCreateSchema(Schema):
    """Validate member creation input."""
    full_name = fields.String(
        required=True,
        validate=validate.Length(min=2, max=100,
                                 error='Họ tên phải từ 2 đến 100 ký tự.')
    )
    gender = fields.String(
        required=True,
        validate=validate.OneOf(['MALE', 'FEMALE', 'OTHER'],
                                error='Giới tính không hợp lệ.')
    )
    birth_year = fields.Integer(
        required=True,
        validate=validate.Range(min=1940, max=2015,
                                error='Năm sinh không hợp lệ.')
    )
    phone = fields.String(
        required=True,
        validate=validate.Regexp(
            r'^0\d{9}$',
            error='SĐT phải gồm 10 chữ số, bắt đầu bằng 0.'
        )
    )
    email = fields.Email(load_default=None, error_messages={
        'invalid': 'Email không hợp lệ.'
    })
    trainer_id = fields.Integer(load_default=None)


class MemberUpdateSchema(Schema):
    """Validate member update input (partial)."""
    full_name = fields.String(
        validate=validate.Length(min=2, max=100)
    )
    gender = fields.String(
        validate=validate.OneOf(['MALE', 'FEMALE', 'OTHER'])
    )
    birth_year = fields.Integer(
        validate=validate.Range(min=1940, max=2015)
    )
    email = fields.Email(load_default=None)
    trainer_id = fields.Integer(load_default=None, allow_none=True)
