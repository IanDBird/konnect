import requests
import const

from device import KonnectDevice
from bearerauth import BearerAuth
from warrant.aws_srp import AWSSRP

class KonnectClient:
    email = None
    username = None
    password = None

    token = None
    tokenType = None
    tokenExpiresIn = None
    refreshToken = None

    def __init__(self, email, password):
        self.email = email
        self.password = password

    def authenticate_user(self):
        # Before we can sign in, we need to determine the username. This is done
        # by making a request that for a given email, it will return the username
        # (if it exists.)
        self.username = self.__fetchUsername()

        try:
            aws_srp = AWSSRP(
                username = self.username,
                password = self.password,
                pool_id = 'eu-west-1_t5HV3bFjl',
                pool_region = 'eu-west-1',
                client_id = '23s0olnnniu5472ons0d9uoqt9')
            aws_response = aws_srp.authenticate_user()

            aws_result = aws_response['AuthenticationResult']
            self.token = aws_result['IdToken']
            self.tokenType = aws_result['TokenType']
            self.tokenExpiresIn = aws_result['ExpiresIn']
            self.refreshToken = aws_result['RefreshToken']
        except:
            raise Exception('Failed to sign in')

    def getDevices(self):
        self.__checkToken()
        devices = []

        url = const.API_DEVICES_URL
        response = requests.get(url, auth = BearerAuth(self.token))
        if (response.status_code != 200):
            print('Status Code: ' + str(response.status_code))
            return devices

        #{"devices":[{"addressCountry":"GB","cfgCTConfig":1,"currency":"GBP","evseFwVersion":"5.8","friendlyName":"Home","id":"e00fce6891a6d30340b9aaab","name":"2202212993","sysFwVersion":287,"userLock":false}]}
        response_body = response.json()
        
        # Log Devices
        print(response_body)

        for device in response_body['devices']:
            devices.append(KonnectDevice(
                api = self,
                device_id = device['id'],
                friendly_name = device['friendlyName'],
                user_lock = device['userLock']))

        return devices

    def __fetchUsername(self):
        url = const.GRAPHQL_USER_MAP_URL
        body = { 'email': self.email }
        response = requests.post(url, json = body)

        if (response.status_code != 200):
            raise Exception('Incorrect email address')

        # {'error': 'Pending user with email "x" not found'}
        # {'username': 'xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx:x'}
        response_body = response.json()
        if ('username' not in response_body):
            raise Exception('Incorrect email address')

        return response_body['username']

    def __checkToken(self):
        if self.token == None:
            raise Exception('Not signed in')