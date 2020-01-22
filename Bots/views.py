from django.shortcuts import render, redirect
from django.views.generic import View
from django.core.exceptions import ObjectDoesNotExist
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.conf import settings
from django.http import HttpResponse, Http404
from django.contrib.auth.decorators import login_required
# from pylint import epylint as lint

import json
import os
# import pycodestyle

from .models import Profile, Bot
from .program import TextBuilder
from .forms import *
from .pythonanywhere import AutoDeploy
from .classes.text_field import *
from .classes.reply_markup_field import *
from .classes.reply_buttons_field import *
from .classes.inline_markup_field import *
from .classes.inline_buttons_field import *
from .functions import *


class ShowBots(LoginRequiredMixin, View):
    login_url = '/signIn/'
    redirect_field_name = 'show_bots_url'

    def get(self, request):
        context = {
            'title': 'Your Bots - BotConstructor',
        }

        try:
            current_user_profile = Profile.objects.get(user=request.user)
            all_bots = Bot.objects.filter(owner=current_user_profile)[::-1]
            if not all_bots:
                messages.error(request, 'No bots here')

            context.update({
                'all_bots': all_bots
            })
        except ObjectDoesNotExist:
            messages.error(request, 'Such user does not exist')

        return render(request, 'AllBots.html', context)


class UpdateBot(View):
    def get(self, request, bot_id: int):
        current_bot = Bot.objects.get(id=bot_id)
        update_bot_form = CreateBotForm(instance=current_bot)

        context = {
            'title': 'Update Bot - BotConstructor',
            'update_bot_form': update_bot_form
        }
        return render(request, 'UpdateBot.html', context)

    def post(self, request, bot_id: int):
        current_bot = Bot.objects.get(id=bot_id)
        update_bot_form = CreateBotForm(
            request.POST, request.FILES, instance=current_bot)
        current_user = Profile.objects.get(user=request.user)

        if update_bot_form.is_valid():
            access_token = update_bot_form.cleaned_data['access_token']
            file = update_bot_form.cleaned_data['file_script']

            current_bot.access_token = access_token
            current_bot.file_script = file
            current_bot.owner = current_user
            current_bot.save()

            return redirect('show_bots_url')

        context = {
            'title': 'Update Bot - BotConstructor',
            'update_bot_form': update_bot_form
        }
        return render(request, 'UpdateBot.html', context)


class DeleteBot(View):
    def get(self, request, bot_id: int):
        context = {
            'title': 'Delete Bot - BotConstructor'
        }
        return render(request, 'DeleteBot.html', context)

    def post(self, request, bot_id: int):
        current_bot = Bot.objects.get(id=bot_id)
        current_bot.delete()
        return redirect('show_bots_url')


class CreateBotStepOne(LoginRequiredMixin, View):
    login_url = '/signIn/'
    redirect_field_name = 'create_bot_first_step_url'

    def get(self, request):
        first_form = GetAccessToken()

        context = {
            'title': 'First Step - BotConstructor',
            'first_form': first_form
        }
        return render(request, 'FirstStep.html', context)

    def post(self, request):
        first_form = GetAccessToken(request.POST)

        if first_form.is_valid():
            access_token = first_form.cleaned_data['access_token']
            name = first_form.cleaned_data['name']
            username = first_form.cleaned_data['username']

            data.update({
                'access_token': access_token,
                'name': name,
                'username': username
            })

            path = open_configuration(request)
            with open(path, 'w', encoding='utf-8') as file:
                json.dump(data, file, indent=4, ensure_ascii=False)
            return redirect('create_bot_second_step_text_url')

        context = {
            'title': 'First Step - BotConstructor',
            'first_form': first_form
        }
        return render(request, 'FirstStep.html', context)


class GenerateFile(LoginRequiredMixin, View):
    login_url = '/signIn/'
    redirect_field_name = 'create_bot_second_step_next_step_url'

    def get(self, request):
        path = open_configuration(request)
        with open(path, 'r', encoding='utf-8') as file:
            data = json.load(file)

        program = TextBuilder(token=data['access_token'],
                              user_username=str(request.user.username))
        final_text_dictionary = {}
        for text_element in data['text']:
            final_text_dictionary[text_element['react_text']
                                  ] = text_element['response_text']

        final_reply_markup_keyboard = {}
        for reply_markup_element in data['reply_markup']:
            buttons = []

            for button_element in reply_markup_element['buttons']:
                buttons.append(
                    {
                        'response': button_element['response_text'],
                        'request_contact': button_element['request_contact'],
                        'request_location': button_element['request_location']
                    }
                )

            final_reply_markup_keyboard[reply_markup_element['react_text']] = {
                'resize_keyboard': reply_markup_element['resize_keyboard'],
                'one_time_keyboard': reply_markup_element['one_time_keyboard'],
                'selective': reply_markup_element['selective'],
                'row_width': reply_markup_element['row_width'],
                'response_text': reply_markup_element['response_text'],
                'buttons': buttons
            }

        final_inline_markup_keyboard = {}
        for inline_markup_element in data['inline_markup']:
            buttons = []

            for button_element in inline_markup_element['buttons']:
                buttons.append(
                    {
                        'text': button_element['text'],
                        'url': button_element['url'],
                        'callback': button_element['callback'],
                        'switch_inline': button_element['switch_inline'],
                        'switch_inline_current': button_element[
                            'switch_inline_current'
                        ]
                    }
                )

            final_inline_markup_keyboard[
                inline_markup_element['react_text']
            ] = {
                'row_width': inline_markup_element['row_width'],
                'response_text': inline_markup_element['response_text'],
                'buttons': buttons
            }

        program.text_response(text_dictionary=final_text_dictionary)
        program.reply_markup_response(
            reply_markup_dictionary=final_reply_markup_keyboard
        )
        program.inline_markup_response(
            inline_markup_dictionary=final_inline_markup_keyboard
        )
        program.polling_bot()

        file_script_path = 'ScriptBots/test_bot.py'
        file_config_path = 'ScriptBots/configuration.json'
        current_user = Profile.objects.get(user=request.user)
        access_token = data['access_token']

        bot_object = Bot(file_script=file_script_path,
                         file_config=file_config_path, owner=current_user,
                         access_token=access_token, title=data['name'],
                         username=data['username'])
        bot_object.save()
        return redirect('create_bot_third_step_url')


class CreateBotStepThree(LoginRequiredMixin, View):
    login_url = '/signIn/'
    redirect_field_name = 'create_bot_third_step_url'

    def get(self, request):
        path = open_test_bot(request)
        with open(path, 'r', encoding='utf-8') as file:
            content = file.read()

        context = {
            'title': 'Third Step - BotConstructor',
            'content': content
        }
        return render(request, 'ThirdStep.html', context)

    def post(self, request):
        data = dict(request.POST)
        code = data['code_editor'][0].replace('\r', '')

        path = open_test_bot(request)
        # pylint_stdout, pylint_stderr = lint.py_run(path, return_std=True)
        # print(pylint_stdout, pylint_stderr)
        # some = pycodestyle.Checker(filename=path).run_check()
        # print(some)
        with open(path, 'w', encoding='utf-8') as file:
            file.write(code)

        return redirect('create_bot_third_step_url')


class RunBot(LoginRequiredMixin, View):
    login_url = '/signIn/'
    redirect_field_name = 'create_bot_third_step_url'

    def get(self, request):
        AutoDeploy(file_title=f'{request.user.username}_test_bot.py')
        return redirect('show_bots_url')


class Download:
    @staticmethod
    @login_required
    def config(request):
        file_path = open_configuration(request)
        if os.path.exists(file_path):
            with open(file_path, 'rb') as file:
                response = HttpResponse(
                    file.read(), content_type='application/configuration.json')
                response[
                    'Content-Disposition'
                ] = f'inline; filename={os.path.basename(file_path)}'
                return response
        return Http404

    @staticmethod
    @login_required
    def script(request):
        file_path = open_test_bot(request)
        if os.path.exists(file_path):
            with open(file_path, 'rb') as file:
                response = HttpResponse(
                    file.read(), content_type='application/test_bot.py')
                response[
                    'Content-Disposition'
                ] = f'inline; filename={os.path.basename(file_path)}'
                return response
        return Http404
