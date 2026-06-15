import requests
import base64
from django.conf import settings
from integrations.models import ZoomMeeting
from django.utils.dateparse import parse_datetime

class ZoomService:

    BASE_URL = "https://api.zoom.us/v2"

    def get_access_token(self):

        url = "https://zoom.us/oauth/token"

        auth = f"{settings.ZOOM_CLIENT_ID}:{settings.ZOOM_CLIENT_SECRET}"
        auth_encoded = base64.b64encode(auth.encode()).decode()

        headers = {
            "Authorization": f"Basic {auth_encoded}",
            "Content-Type": "application/x-www-form-urlencoded"
        }

        data = {
            "grant_type": "account_credentials",
            "account_id": settings.ZOOM_ACCOUNT_ID
        }

        response = requests.post(url, headers=headers, data=data)
        response.raise_for_status()

        return response.json()["access_token"]


    def create_meeting(self, topic, start_time, duration, timezone):

        token = self.get_access_token()

        url = f"{self.BASE_URL}/users/me/meetings"

        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }

        payload = {
            "topic": topic,
            "type": 2,
            "start_time": start_time,
            "duration": duration,
            "timezone": timezone,
            "settings": {
                "waiting_room": True,
                "mute_upon_entry": True,
                "auto_recording": "cloud"
            }
        }

        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()

        return response.json()


    # ✅ LIST ALL MEETINGS
    def list_meetings(self):

        token = self.get_access_token()

        url = f"{self.BASE_URL}/users/me/meetings?page_size=300"

        headers = {
            "Authorization": f"Bearer {token}"
        }

        response = requests.get(url, headers=headers)
        response.raise_for_status()

        data = response.json()

        return data.get("meetings", [])


    # ✅ SEARCH MEETING BY TITLE
    def search_meetings(self, query):

        meetings = self.list_meetings()

        results = []

        keywords = query.lower().split()

        for meeting in meetings:

            topic = meeting.get("topic", "").lower()

            if any(word in topic for word in keywords):

                results.append({
                    "id": meeting["id"],
                    "topic": meeting["topic"],
                    "start_time": meeting["start_time"],
                    "duration": meeting.get("duration"),
                    "join_url": meeting.get("join_url")
                })

        return results
    
    def get_meeting_details(self, meeting_id):

        token = self.get_access_token()

        url = f"{self.BASE_URL}/meetings/{meeting_id}"

        headers = {
            "Authorization": f"Bearer {token}"
        }

        response = requests.get(url, headers=headers)
        response.raise_for_status()

        return response.json()
    
    def list_recordings(self):

            token = self.get_access_token()

            url = f"{self.BASE_URL}/users/me/recordings?page_size=300"

            headers = {
                "Authorization": f"Bearer {token}"
            }

            params = {
                "from": "2020-01-01",
                "to": "2030-01-01"
            }

            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()

            data = response.json()

            return data.get("meetings", [])


    # ✅ SEARCH RECORDINGS
    def search_recordings(self, query):

        recordings = self.list_recordings()

        results = []

        keywords = query.lower().split() if query else []

        for meeting in recordings:

            topic = meeting.get("topic", "").lower()

            # If query empty OR keyword matches
            if not keywords or any(word in topic for word in keywords):

                files = meeting.get("recording_files", [])

                video_file = None

                for f in files:
                    if f.get("play_url"):
                        video_file = f
                        break

                if video_file:
                    results.append({
                        "id": meeting["id"],
                        "topic": meeting["topic"],
                        "play_url": video_file["play_url"],
                        "download_url": video_file.get("download_url"),
                        "start_time": meeting["start_time"]
                    })

        return results


# ---------------------------------------
# Django Logic
# ---------------------------------------

def create_zoom_meeting_for_webinar(webinar):

    zoom = ZoomService()

    meeting = zoom.create_meeting(
        topic=webinar.title,
        start_time=webinar.start_datetime.isoformat(),
        duration=webinar.duration_minutes,
        timezone="America/Los_Angeles"
    )

    zoom_meeting = ZoomMeeting.objects.create(
        webinar=webinar,
        zoom_meeting_id=meeting["id"],
        uuid=meeting["uuid"],
        topic=meeting["topic"],
        join_url=meeting["join_url"],
        start_url=meeting["start_url"],
        password=meeting.get("password", ""),
        start_time=webinar.start_datetime,
        duration=webinar.duration_minutes,
        timezone="America/Los_Angeles"
    )

    return zoom_meeting


def link_existing_zoom_meeting(webinar, meeting_data):

    zoom = ZoomService()

    details = zoom.get_meeting_details(meeting_data["id"])

    zoom_meeting, created = ZoomMeeting.objects.update_or_create(
    webinar=webinar,
    defaults={
        "zoom_meeting_id": details["id"],
        "uuid": details.get("uuid", ""),
        "topic": details["topic"],
        "join_url": details["join_url"],
        "start_url": details.get("start_url", ""),
        "password": details.get("password", ""),
        "start_time": parse_datetime(details["start_time"]),
        "duration": details.get("duration", 60),
        "timezone": "UTC"
    }
)

    return zoom_meeting
