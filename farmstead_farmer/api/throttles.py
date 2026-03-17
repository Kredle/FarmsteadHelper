from rest_framework.throttling import UserRateThrottle


class SendOTPThrottle(UserRateThrottle):
    rate = '10/minute'


class BasicThrottle(UserRateThrottle):
    rate = '15/minute'


class UpdateData(UserRateThrottle):
    rate = '50/minute'


class MainAPiThrottle(UserRateThrottle):
    rate = '30/minute'


class DataScraptingTrottle(UserRateThrottle):
    rate = '40/minute'
