def add_members_from(enum_cls):
    def decorator(cls):
        for member_name, member_value in enum_cls.__members__.items():
            setattr(cls, member_name, member_value)
        return cls
    return decorator
