from typing import Type, Any

from injector import Injector, Binder


def configure(binder: Binder):
    from .configuration import AzureLogServiceConfiguration

    binder.bind(AzureLogServiceConfiguration, AzureLogServiceConfiguration.build())


__injector = Injector(configure)


def provide(class_: Type[Any]):
    return __injector.get(class_)
