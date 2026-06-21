class AdminAuthorization:
    _authorized_admin_id = None

    @classmethod
    def set_admin_id(cls, admin_id):
        cls._authorized_admin_id = admin_id

    @classmethod
    def get_admin_id(cls):
        return cls._authorized_admin_id

    @classmethod
    def clear(cls):
        cls._authorized_admin_id = None
