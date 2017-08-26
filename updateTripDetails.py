import sys
import os
import gspread
import googlemaps
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage
from datetime import datetime

GMAPS_API_KEY_FILE='gmaps_api.key'
SCOPES = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
CLIENT_SECRET_FILE = 'client_secret.json'
APPLICATION_NAME = 'RoadTrip'

def get_credentials():
  """Gets valid user credentials from storage.
  If nothing has been stored, or if the stored credentials are invalid,
  the OAuth2 flow is completed to obtain the new credentials.
  Returns:
      Credentials, the obtained credential.
  """
  home_dir = os.path.expanduser('~')
  credential_dir = os.path.join(home_dir, '.credentials')
  if not os.path.exists(credential_dir):
      os.makedirs(credential_dir)
  credential_path = os.path.join(credential_dir,
          'sheets.googleapis.roadtrip.json')

  store = Storage(credential_path)
  credentials = store.get()
  if not credentials or credentials.invalid:
      flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
      flow.user_agent = APPLICATION_NAME
      credentials = tools.run_flow(flow, store)
  return credentials


def getSpreadsheet(wbName, shName):
  creds = get_credentials()
  clientAuth = gspread.authorize(creds)
  wb = clientAuth.open(wbName)
  return wb.worksheet(shName)

def getTripDetails(gmaps,A,B):
  directions_result = gmaps.directions(A,B,departure_time=datetime.now())
  duration=0
  distance=0
  for leg in directions_result[0]['legs']:
    duration += leg['duration']['value']
    distance += leg['distance']['value']
  return duration,distance

def main(argv):
  fo = open(GMAPS_API_KEY_FILE)
  gkey = fo.readline()
  gkey = gkey.split("\n")[0]
  gmaps = googlemaps.Client(key=gkey)
  sh = getSpreadsheet('West Coast Trip Days', 'Trip');
  records = sh.get_all_records()
  origin = None
  row=3
  for rec in records:
    if(origin != None):
      segmentTime, segmentDistance = getTripDetails(gmaps,origin,rec['Address'])
      m, s = divmod(segmentTime, 60)
      h, m = divmod(m, 60)
      formattedTime = "%d hours, %02d minutes" % (h, m) 
      formattedDist = "%d" % int(round(segmentDistance*0.00062137119223733)) 
      print "%s => %s" % (formattedTime, rec['Address']) 
      sh.update_cell(row, 4, formattedTime) 
      sh.update_cell(row, 5, formattedDist) 
      row += 1
    origin=rec['Address']

if __name__ == "__main__":
  main(sys.argv[1:])
