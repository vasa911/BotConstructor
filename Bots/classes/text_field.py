from django.shortcuts import render, redirect
from django.views.generic import View
from django.contrib.auth.mixins import LoginRequiredMixin

from ..functions import *
from ..forms import TextForm
from django.http import HttpResponse, JsonResponse


class CreateTextField(LoginRequiredMixin, View):
    context = {}
    login_url = '/signIn/'
    redirect_field_name = 'create_bot_second_step_text_url'

    def get(self, request, token: str):
        text_elements = enumerate_elements(
            request,
            token=token,
            get_object='text'
        )
        text_form = TextForm(request=request, token=token)

        self.context.update({
            'title': 'Second Step - BotConstructor',
            'text_elements': text_elements,
            'text_form': text_form,
            'token': token
        })
        response = render(request, 'SecondStep.html', self.context)
        return response

    def post(self, request, token: str):
        text_elements = enumerate_elements(
            request,
            token=token,
            get_object='text'
        )

        remove_reply = request.POST.get('remove_reply_markup')
        smart = request.POST.get('smart')

        some_post = request.POST.copy()
        some_post.pop('remove_reply_markup')
        some_post.pop('smart')

        text_form = TextForm(some_post, request=request, token=token)

        if request.POST.get('action') == 'post':
            if text_form.is_valid():
                react_text = text_form.cleaned_data['react_text']
                response_text = text_form.cleaned_data['response_text']

                csrf = request.POST.get('csrfmiddlewaretoken')

                remove_reply_markup = True if remove_reply == 'true' else False
                smart = True if smart == 'true' else False

                path = open_configuration(request, token)
                with open(path, 'r+', encoding='utf-8') as file_name:
                    object_config = json.load(file_name)

                    try:
                        object_config['text'].append({
                            'response_text': response_text,
                            'react_text': react_text,
                            'remove_reply_markup': remove_reply_markup,
                            'smart': smart
                        })
                    except KeyError:
                        object_config['text'] = [{
                            'response_text': response_text,
                            'react_text': react_text,
                            'remove_reply_markup': remove_reply_markup,
                            'smart': smart
                        }]
                    file_name.seek(0)
                    json.dump(object_config, file_name,
                              indent=4, ensure_ascii=False)
                    len_text = len(object_config['text']) - 1

                return JsonResponse({
                    'response_text': response_text,
                    'react_text': react_text,
                    'remove_reply_markup': remove_reply_markup,
                    'len_text': len_text,
                    'csrf': csrf,
                    'token': token,
                    'smart': smart
                })
            else:
                return JsonResponse({
                    'text_error': text_form.errors
                })

        self.context.update({
            'title': 'Second Step - BotConstructor',
            'text_elements': text_elements,
            'text_form': text_form,
            'token': token
        })
        response = render(request, 'SecondStep.html', self.context)
        return response


class UpdateTextField(LoginRequiredMixin, View):
    login_url = '/signIn/'
    redirect_field_name = 'create_bot_second_step_text_url'
    context = {}

    def post(self, request, token: str):
        data = dict(request.POST)
        if request.POST.get('action') == 'update_text':
            react_text = dict(request.POST)['react_text[]']
            response_text = dict(request.POST)['response_text[]']
            remove_reply_markup = dict(request.POST)['remove_reply_markup[]']
            smart = request.POST.get('smart[]')

            index = int(react_text[0][-1])
            print(react_text, response_text, remove_reply_markup, index)

            path = open_configuration(request, token)
            with open(path, 'r', encoding='utf-8') as file:
                object_config = json.load(file)

            text_object = object_config['text']
            text_object[index]['react_text'] = react_text[1]
            text_object[index]['response_text'] = response_text[1]
            text_object[index]['smart'] = True if smart == 'true' else False

            if remove_reply_markup[1] == 'true':
                text_object[index][
                    'remove_reply_markup'
                ] = True
            else:
                text_object[index][
                    'remove_reply_markup'
                ] = False

            object_config['text'] = text_object
            with open(path, 'w', encoding='utf-8') as file:
                json.dump(object_config, file, indent=4, ensure_ascii=False)
            return JsonResponse(text_object[index])

        self.context.update({
            'title': 'Second Step - BotConstructor',
            'token': token
        })
        response = render(request, 'SecondStep.html', self.context)
        return response


class DeleteTextField(LoginRequiredMixin, View):
    login_url = '/signIn/'
    redirect_field_name = 'create_bot_second_step_text_url'

    def get(self, request, token: str):
        if request.GET.get('action') == 'delete_text':
            button_id = int(request.GET.get('button_id').split('_')[-1])
            print(button_id)

            path = open_configuration(request, token)
            with open(path, 'r', encoding='utf-8') as file:
                object_config = json.load(file)

            text_object = object_config['text']
            text_object.remove(text_object[button_id])

            object_config['text'] = text_object
            with open(path, 'w', encoding='utf-8') as file:
                json.dump(object_config, file, indent=4, ensure_ascii=False)

            return JsonResponse({
                'button_id': button_id
            })

        self.context.update({
            'title': 'Second Step - BotConstructor',
            'token': token
        })
        response = render(request, 'SecondStep.html', self.context)
        return response
