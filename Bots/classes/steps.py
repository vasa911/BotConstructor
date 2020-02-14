from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import View

from ..functions import *
from ..forms import GetAccessToken

import autopep8


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
        data = {}

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
        fixed_code = autopep8.fix_code(code)
        try:
            is_right_sliced = autopep8.check_syntax(code[:-30])
            exec(is_right_sliced)

            with open(path, 'w', encoding='utf-8') as file:
                file.write(fixed_code)
            return redirect('create_bot_third_step_url')
        except (NameError, ValueError, TypeError, AttributeError) as error:
            messages.error(
                request,
                'You made a mistake in changing the program. '
                f'Current problem: {error}'
            )

        context = {
            'title': 'Third Step - BotConstructor',
            'content': fixed_code
        }
        return render(request, 'ThirdStep.html', context)
