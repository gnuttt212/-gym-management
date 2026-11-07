"""Subscription schemas for marshmallow validation."""

from marshmallow import Schema, fields, validate


class RegistrationSchema(Schema):
    """Validate online member registration input."""
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
    password = fields.String(
        required=True,
        validate=validate.Length(min=6, error='Mật khẩu phải ít nhất 6 ký tự.')
    )
    plan_id = fields.Integer(required=True)


class WalkInRegistrationSchema(Schema):
    """Validate walk-in registration by receptionist (no password)."""
    full_name = fields.String(
        required=True,
        validate=validate.Length(min=2, max=100)
    )
    gender = fields.String(
        required=True,
        validate=validate.OneOf(['MALE', 'FEMALE', 'OTHER'])
    )
    birth_year = fields.Integer(
        required=True,
        validate=validate.Range(min=1940, max=2015)
    )
    phone = fields.String(
        required=True,
        validate=validate.Regexp(r'^0\d{9}$')
    )
    email = fields.Email(load_default=None)
    plan_id = fields.Integer(required=True)
