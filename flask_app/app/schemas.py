"""Marshmallow schemas for request/response validation"""

from marshmallow import Schema, fields, validate


class ItemCreateSchema(Schema):
    """Schema for creating item"""
    name = fields.String(required=True, validate=validate.Length(min=1, max=200))
    description = fields.String(allow_none=True)
    price = fields.Float(required=True, validate=validate.Range(min=0.01))
    in_stock = fields.Boolean(missing=True)
    category = fields.String(allow_none=True, validate=validate.Length(max=100))


class ItemUpdateSchema(Schema):
    """Schema for updating item"""
    name = fields.String(validate=validate.Length(min=1, max=200))
    description = fields.String(allow_none=True)
    price = fields.Float(validate=validate.Range(min=0.01))
    in_stock = fields.Boolean()
    category = fields.String(validate=validate.Length(max=100))


class ItemResponseSchema(Schema):
    """Schema for item response"""
    id = fields.Int()
    name = fields.String()
    description = fields.String(allow_none=True)
    price = fields.Float()
    in_stock = fields.Boolean()
    category = fields.String(allow_none=True)
    created_at = fields.DateTime()
    updated_at = fields.DateTime(allow_none=True)