import subprocess
from datetime import datetime,timedelta
import os
import signal


# get current datetime
today = datetime.now()- timedelta(hours=1, minutes=30)

# Get current ISO 8601 datetime in string format
iso_date = today.isoformat()


def start_stream(cam,youtube):

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
    #print(response)
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
        #print(stream["cdn"]["ingestionInfo"]["streamName"])

    except Exception as e:
        print ("An HTTP error %d occurred:\n%s" % (e.resp.status, e.content))

    proc = subprocess.Popen('cmd /k "ffmpeg -i {}\
        -vcodec copy -acodec aac \
            -f flv {}"'.format(cam,"rtmp://a.rtmp.youtube.com/live2/"+stream["cdn"]["ingestionInfo"]["streamName"]), shell=False)
    
    return([response["id"],stream["id"],proc.pid])


def stop_stream(youtube,id):

    request = youtube.liveBroadcasts().transition(
        broadcastStatus="complete",
        id=id[0],
        part="snippet,status"
    )
    request.execute()

    request = youtube.liveStreams().delete(
        id=id[1]
    )
    request.execute()
    os.killpg(os.getpgid(id[2]), signal.SIGTERM)

    return("OK")
