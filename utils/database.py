from utils import botlists


grabber = None
session = None


async def setup(ses):
    global session
    session = ses

    global grabber
    grabber = botlists.BotGrabber(session=session)
    await grabber.update_bots()


async def get_bots(**filters):
    return grabber.bots