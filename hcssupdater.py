import httplib2
import time

from apiclient import discovery
from datetime import datetime
from oauth2client.service_account import ServiceAccountCredentials

SCOPES = 'https://www.googleapis.com/auth/spreadsheets'
CLIENT_SECRET_FILE = 'client_secret.json'
APPLICATION_NAME = 'Healthy Challenge Updater'


class HCSSUpdater(object):
    def __init__(self, spreadsheet_id, sheet_name="Sheet1"):
        self.spreadsheet_id = spreadsheet_id
        self.sheet_name = sheet_name
        self.credentials = self.get_credentials()
        http = self.credentials.authorize(httplib2.Http())
        discovery_url = 'https://sheets.googleapis.com/$discovery/rest?version=v4'
        self.service = discovery.build('sheets', 'v4', http=http, discoveryServiceUrl=discovery_url)

    def get_credentials(self):
        scopes = [SCOPES]

        credentials = ServiceAccountCredentials.from_json_keyfile_name(
            CLIENT_SECRET_FILE, scopes=scopes)

        return credentials

    def idxtocol(self, idx):
        return chr(idx + ord('A'))

    def timestamp_to_date(self, timestamp):
        return datetime.fromtimestamp(int(timestamp)).replace(hour=0, minute=0, second=0, microsecond=0)

    def row_from_date(self, date, cols):
        end_col = self.idxtocol(cols)
        range_name = '%s!A2:%s' % (self.sheet_name, end_col)
        result = self.service.spreadsheets().values().get(
            spreadsheetId=self.spreadsheet_id, range=range_name).execute()
        values = result.get('values', [])
        end_date = datetime.strptime(values[-1][0], "%m/%d/%Y")
        # print('end_date', end_date, date, bool(date == end_date))
        # print('date values', values)
        if values:
            if date == end_date:
                row_idx = len(values) + 1
                row = values[-1]
            else:
                row_idx = len(values) + 2
                row = [date.strftime('%m/%d/%y')]
            row.extend(['' for _ in range(cols - len(row))])
            # print('row is ', row_idx, row)
            return row_idx, row

    def get_names(self):
        range_name = '%s!B1:1' % self.sheet_name
        result = self.service.spreadsheets().values().get(spreadsheetId=self.spreadsheet_id, range=range_name).execute()
        values = result.get('values', [])
        return values[0]

    def update_score(self, name, value, timestamp):
        date = self.timestamp_to_date(timestamp)
        # print('date', date)

        names = self.get_names()
        # print('names', names)

        end_col = len(names) + 1
        row_idx, row = self.row_from_date(date, end_col)
        name_idx = names.index(name) + 1
        row[name_idx] = value
        # print('updatedRow', row)

        range_name = '%s!A%s:%s%s' % (self.sheet_name, row_idx, end_col, row_idx)
        # print('rangeName', range_name)

        body = {
            'values': [row]
        }
        result = self.service.spreadsheets().values().update(spreadsheetId=self.spreadsheet_id, range=range_name,
                                                             valueInputOption="USER_ENTERED", body=body).execute()
        # print('result', result)


def test_main():
    spreadsheetid = '1U-wAQAXaDFYZ2uQvPtxL5kSDOss8kMPRRpyb6OgRbKs'
    ssupdator = HCSSUpdater(spreadsheetid)
    ssupdator.update_score('Doug Applegate', str(3), str(int(time.time())))
    ssupdator.update_score('Derek Haderlie', str(3), str(int(time.time())))
    ssupdator.update_score('Chad Ruger', str(3), str(int(time.time())))


if __name__ == '__main__':
    test_main()
