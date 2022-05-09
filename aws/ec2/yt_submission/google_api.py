""" This is for GoogleAPI"""
import logging
import random
import time
import httplib2
import http
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from googleapiclient.errors import HttpError

SCOPES = [
  'https://www.googleapis.com/auth/youtube',
  'https://www.googleapis.com/auth/youtube.readonly',
  'https://www.googleapis.com/auth/youtube.upload',
]
TOKEN_URI = 'https://oauth2.googleapis.com/token'

# Explicitly tell the underlying HTTP transport library not to retry, since
# we are handling retry logic ourselves.
httplib2.RETRIES = 1
# Maximum number of times to retry before giving up.
MAX_RETRIES = 10
# Always retry when these exceptions are raised.
RETRIABLE_EXCEPTIONS = (httplib2.HttpLib2Error, IOError, http.client.NotConnected,
    http.client.IncompleteRead, http.client.ImproperConnectionState,
    http.client.CannotSendRequest, http.client.CannotSendHeader,
    http.client.ResponseNotReady, http.client.BadStatusLine)
# Always retry when an apiclient.errors.HttpError with one of these status
# codes is raised.
RETRIABLE_STATUS_CODES = [500, 502, 503, 504]
logger = logging.getLogger(__name__)


def buildYoutube(creds):
  credentials = getCredentials(creds)
  return build('youtube', 'v3', credentials=credentials)


def getCredentials(creds):
    creds = Credentials(
        creds.access_token,
        refresh_token=creds.refresh_token,
        token_uri=TOKEN_URI,
        client_id=creds.client_id,
        client_secret=creds.client_secret)

    print(creds, creds.valid, creds.expired)
    print(creds.token)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            print("Access token expired.")
            creds.refresh(Request())
            print("New access token: {}", creds.token)
        else:
            print('Error.')

    return creds


def uploadVideo(creds, options):
  tags = None
  if options.get("keywords"):
    tags = options["keywords"].split(",")

  body=dict(
    snippet=dict(
      title=options.get("title"),
      description=options.get("description"),
      tags=tags,
      categoryId=options.get("category")
    ),
    status=dict(
      privacyStatus=options.get("privacyStatus")
    )
  )
  youtube = buildYoutube(creds)
  # Call the API's videos.insert method to create and upload the video.
  insert_request = youtube.videos().insert(
    part=",".join(body.keys()),
    body=body,
    # The chunksize parameter specifies the size of each chunk of data, in
    # bytes, that will be uploaded at a time. Set a higher value for
    # reliable connections as fewer chunks lead to faster uploads. Set a lower
    # value for better recovery on less reliable connections.
    #
    # Setting "chunksize" equal to -1 in the code below means that the entire
    # file will be uploaded in a single HTTP request. (If the upload fails,
    # it will still be retried where it left off.) This is usually a best
    # practice, but if you're using Python older than 2.6 or if you're
    # running on App Engine, you should set the chunksize to something like
    # 1024 * 1024 (1 megabyte).
    media_body=MediaFileUpload(options.get("file"), chunksize=-1, resumable=True)
  )

  response = resumable_upload(insert_request)
  youtube.close()
  return response


# This method implements an exponential backoff strategy to resume a
# failed upload.
def resumable_upload(insert_request):
  response = None
  error = None
  retry = 0
  while response is None:
    try:
      print("Uploading file...")
      status, response = insert_request.next_chunk()
      if response is not None:
        if 'id' in response:
          print("Video id '%s' was successfully uploaded." % response['id'])
        else:
          exit("The upload failed with an unexpected response: %s" % response)
    except HttpError as e:
      if e.resp.status in RETRIABLE_STATUS_CODES:
        error = "A retriable HTTP error %d occurred:\n%s" % (e.resp.status, e.content)
      else:
        raise
    except RETRIABLE_EXCEPTIONS as e:
            error = "A retriable error occurred: %s" % e

    if error is not None:
      print(error)
      retry += 1
      if retry > MAX_RETRIES:
        exit("No longer attempting to retry.")

      max_sleep = 2 ** retry
      sleep_seconds = random.random() * max_sleep
      print("Sleeping %f seconds and then retrying..." % sleep_seconds)
      time.sleep(sleep_seconds)

  return response
