# -*- coding: utf-8 -*-

# Sample Python code for youtube.liveBroadcasts.insert
# See instructions for running these code samples locally:
# https://developers.google.com/explorer-help/code-samples#python

import os

import google_auth_oauthlib.flow
import googleapiclient.discovery
import googleapiclient.errors

scopes = ["https://www.googleapis.com/auth/youtube.force-ssl"]

from datetime import datetime,timedelta

# get current datetime
today = datetime.now()- timedelta(hours=1, minutes=30)

print('Today Datetime:', today)

# Get current ISO 8601 datetime in string format
iso_date = today.isoformat()
print('ISO DateTime:', iso_date)

def main():
  # Disable OAuthlib's HTTPS verification when running locally.
  # *DO NOT* leave this option enabled in production.
  os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "0"

  api_service_name = "youtube"
  api_version = "v3"
  client_secrets_file = "code.json"

  # Get credentials and create an API client
  flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(
      client_secrets_file, scopes)
  credentials = flow.run_local_server()
  youtube = googleapiclient.discovery.build(
      api_service_name, api_version, credentials=credentials)
  
  request = youtube.liveBroadcasts().insert(
      part="snippet,contentDetails,status",
      body={
        "contentDetails": {
          "enableClosedCaptions": True,
          "enableContentEncryption": True,
          "enableDvr": True,
          "enableEmbed": True,
          "recordFromStart": True,
          "startWithSlate": True,
          "enableAutoStart": True,
          "enableAutoStop": True
        },
        "snippet": {
          "title": "broadcast",
          "scheduledStartTime": iso_date,
          "scheduledEndTime": datetime.now().isoformat(),
          
        },
        "status": {
          "privacyStatus": "public",
          "recordingStatus": "recording",
          "lifeCycleStatus": "live",
          "liveBroadcastPriority": "high"
        }
      }
  )
  response = request.execute()
  print(response)
  stream = youtube.liveStreams().insert(
  part="snippet,cdn,contentDetails,status",
      body={
        "cdn": {
          "frameRate": "60fps",
          "ingestionType": "rtmp",
          "resolution": "1080p"
        },
        "contentDetails": {
          "isReusable": True
        },
        "snippet": {
          "title": "stream's name",
          "description": "A description"
        }
      }
  ).execute()
  
  try:
    broadcast = youtube.liveBroadcasts().bind(
      part="id,contentDetails",
      id=response["id"],
      streamId=stream["id"]
    ).execute()
    print(stream)
    print("++++++++++++++++++++++++++++++++++++++++++++++++++++++")
    print(broadcast)

  except Exception as e:
    print ("An HTTP error %d occurred:\n%s" % (e.resp.status, e.content))


if __name__ == "__main__":
    main()