from __future__ import print_function
import ast

import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
SPREADSHEET_ID = '1nzlE0FmtF6EY8WbHU5wwC4sLaDbEYtnzGRy893yEhv4'
RANGE_NAME = 'Medal Hall!A3:D'
TOKEN_PATH = "token.json"

def main():
	try:
		service = build('sheets', 'v4', credentials=auth())
		sheets = service.spreadsheets()
		result = sheets.values().get(spreadsheetId=SPREADSHEET_ID,
                                    range=RANGE_NAME).execute()
		values = result.get('values', [])

		if not values:
			print('No data found.')
			return
	except HttpError as err:
		print(err)

	scores = get_scores()
	for score in scores:
		index = -1
		for i, value in enumerate(values):
			if score[0] == value[0]:
				index = i # actual row is index + 3

		values[index][2] = str(int(values[index][2]) + 1)
		if score[1] == 0:
			if len(values[index]) == 4:
				values[index][3] = str(int(values[index][3]) + 1)
			else:
				values[index].append('1')
			
	send_to_sheets(sheets, values)

def auth():
	creds = None
	# The file token.json stores the user's access and refresh tokens, and is
	# created automatically when the authorization flow completes for the first
	# time.
	if os.path.exists(TOKEN_PATH):
		creds = Credentials.from_authorized_user_file(TOKEN_PATH, SCOPES)
	# If there are no (valid) credentials available, let the user log in.
	if not creds or not creds.valid:
		if creds and creds.expired and creds.refresh_token:
			creds.refresh(Request())
		else:
			flow = InstalledAppFlow.from_client_secrets_file(
				'credentials.json', SCOPES)
			creds = flow.run_local_server(port=0)
		# Save the credentials for the next run
		with open(TOKEN_PATH, 'w') as token:
			token.write(creds.to_json())

	return creds

def get_scores():
	file = open("input.txt", "r")
	arr = file.readlines()
	arr = ast.literal_eval(arr[0])
	return arr

def send_to_sheets(sheets, values):
	rows = []
	for value in values:
		rows.append({"values": [
			{
				"userEnteredValue": {
					"stringValue": value[0]
				}
			},
			{
				"userEnteredValue": {
					"stringValue": value[1] # should always be empty
				}
			},
			{
				"userEnteredValue": {
					"stringValue": value[2]
				}
			},
			{
				"userEnteredValue": {
					"stringValue": value[3] if len(value) == 4 else ''
				}
			}
		]})

	requests = [
		{
			"updateCells": {
				"fields": "userEnteredValue",
				"rows": rows,
				"start": {
					"columnIndex": 0,
					"rowIndex": 2,
					"sheetId": 1532993005
				}
			},
		}
	]

	result = sheets.batchUpdate(
		spreadsheetId=SPREADSHEET_ID, body={ "requests": requests }
	).execute()

	# print(result) # DEBUG
	print('done')

if __name__ == '__main__':
	main()