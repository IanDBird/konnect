import requests
import const

from bearerauth import BearerAuth

class KonnectDevice:
    api = None
    device_id = None
    friendly_name = None
    user_lock = False

    def __init__(self, api, device_id, friendly_name, user_lock):
        self.api = api
        self.device_id = device_id
        self.friendly_name = friendly_name
        self.user_lock = user_lock

    def enable(self):
        if self.__runCommand('userUnlock'):
            self.user_lock = True

    def disable(self):
        if self.__runCommand('userLock'):
            self.user_lock = False

    def __runCommand(self, function):
        url = const.GRAPHQL_URL
        body = {
            'operationName': 'runAEVCommand',
            'variables': { 'deviceId': self.device_id, 'functionName': function },
            'query': const.GRAPHQL_RUN_COMMAND_QUERY
        }

        response = requests.post(url, json = body, auth = BearerAuth(self.api.token))
        return response.status_code == 200

    def getLastCharge(self):
        url = const.GRAPHQL_URL
        body = {
            'operationName': 'getDeviceCalculatedChargeLogs',
            'variables': { 'id': self.device_id, 'offset': 0, 'limit': 1, 'minEnergy': 0.5 },
            'query': const.GRAPHQL_DEVICE_CHARGE_LOGS_QUERY
        }

        response = requests.post(url, json = body, auth = BearerAuth(self.api.token))
        if response.status_code != 200:
            return None

        response_body = response.json()
        device_logs = response_body['data']['getDevice']['deviceCalculatedChargeLogs']
        if len(device_logs) == 0:
            return None

        latest_log = device_logs[0]
        return {
            'duration': latest_log['duration'],
            'chargeCostTotal': latest_log['chargeCostTotal'],
            'chargeEnergyTotal': latest_log['chargeEnergyTotal'],
            'gridCostTotal': latest_log['gridCostTotal'],
            'gridEnergyTotal': latest_log['gridEnergyTotal'],
            'solarEnergyTotal': latest_log['solarEnergyTotal'],
            'solarCostTotal': latest_log['solarCostTotal'],
            'surplusUsedCostTotal': latest_log['surplusUsedCostTotal'],
            'surplusUsedEnergyTotal': latest_log['surplusUsedEnergyTotal']
        }