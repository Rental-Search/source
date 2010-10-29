# -*- coding: utf-8 -*-


def post_save_answer(sender, instance, created, using, **kwargs):
    instance.question.save()
