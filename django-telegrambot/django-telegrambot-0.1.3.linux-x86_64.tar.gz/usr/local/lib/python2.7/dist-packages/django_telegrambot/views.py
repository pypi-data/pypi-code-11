# coding=utf-8
from django.shortcuts import render
from django.http import JsonResponse
from django_telegrambot.apps import DjangoTelegramBot
from django.views.decorators.csrf import csrf_exempt
import json
import telegram
# import the logging library
import logging

# Get an instance of a logger
logger = logging.getLogger(__name__)


# Create your views here.

@csrf_exempt
def webhook (request, bot_token):
    
    #verifico la validità del token
    if DjangoTelegramBot.getBot(bot_token, safe=False) is None:
        return JsonResponse({})
    
    try:
        data = json.loads(request.body.decode("utf-8"))
        logger.info(data)
    except:
        logger.info('Telegram bot receive invalid request' )
        return JsonResponse({'Error':'Invalid Request'})

    update = telegram.Update.de_json(data)
    
    dispatcher = DjangoTelegramBot.getDispatcher(bot_token, safe=False)
    dispatcher.processUpdate(update)
    
    return JsonResponse({})
