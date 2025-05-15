from channels.generic.websocket import AsyncWebsocketConsumer
import json



class TripUpdateConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        from rest_framework_simplejwt.tokens import AccessToken
        from user.models import User

        query_string = self.scope['query_string'].decode()  # Decode the query string
        token = None

        if 'token=' in query_string:
            token = query_string.split('token=')[1]

        if token:
            try:
                access_token = AccessToken(token)
                user_id = access_token['user_id']
                user = await self.get_user(user_id)  # Get the user asynchronously

                if user is not None and isinstance(user, User):
                    self.user = user
                    self.group_name = f'driver_{user.id}'
                    print("self.group_name------------------------",self.group_name)
                    await self.channel_layer.group_add(self.group_name, self.channel_name)
                    await self.accept()
                else:
                    await self.close()
            except Exception as e:
                await self.close()
        else:
            await self.close()


    async def disconnect(self, close_code):
        if hasattr(self, "group_name"):
            await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def send_trip_update(self, event):
        await self.send(text_data=json.dumps(event["message"]))

    @staticmethod
    async def get_user(user_id):
        from django.contrib.auth.models import AnonymousUser
        from user.models import User

        try:
            return await User.objects.aget(id=user_id)
        except User.DoesNotExist:
            return AnonymousUser()
