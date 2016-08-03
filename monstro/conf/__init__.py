# coding=utf-8

import os
import importlib

import tornado.gen
import tornado.ioloop

from monstro.core.exceptions import ImproperlyConfigured
from monstro.core.constants import SETTINGS_ENVIRONMENT_VARIABLE
from tornado.util import import_object
from monstro.modules import ModulesRegistry

from .schema import SettingsSchema


def _import_settings_class():
    try:
        settings_class = import_object(
            os.environ[SETTINGS_ENVIRONMENT_VARIABLE]
        )
    except KeyError:
        raise ImproperlyConfigured(
            'You must either define the environment variable {}'.format(
                SETTINGS_ENVIRONMENT_VARIABLE
            )
        )

    return settings_class

settings = _import_settings_class()
modules = ModulesRegistry(settings.modules)
