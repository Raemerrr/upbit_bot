from slack_sdk import WebClient


class SlackAPI:
    def __init__(self, token):
        # 슬랙 클라이언트 인스턴스 생성
        self.client = WebClient(token)

    def post_message(self, channel_id, blocks=None, text=""):
        result = self.client.chat_postMessage(
            channel=channel_id, **({"blocks": blocks} if blocks else {}), text=text
        )
        return result
