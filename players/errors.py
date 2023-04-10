
class UserError(Exception):
    """Base Class for exceptions in players.players"""
    def __init__(self, message=""):
        self.message = message
        super().__init__(self.message)


class InvalidConnectCode(UserError):

    def __init__(self, cc, message="Invalid connect code"):
        self.cc = cc
        self.message = message
        super().__init__(self.message)


class FailedToGetLocalUserData(UserError):

    def __init__(self, unique_user_info, message="Failed to receive local data"):
        self.unique_user_info = unique_user_info
        self.message = message
        super().__init__(self.message)


class FailedToGetSlippiUserData(UserError):

    def __init__(self, unique_user_info, message="Failed to receive player data from slippi"):
        self.unique_user_info = unique_user_info
        self.message = message
        super().__init__(self.message)
