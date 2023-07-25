from django.utils.translation import gettext_lazy
from . import __version__

try:
    from pretix.base.plugins import PluginConfig
except ImportError:
    raise RuntimeError("Please use pretix 2.7 or above to run this plugin!")


class PluginApp(PluginConfig):
    default = True
    name = "pretix_paybox"
    verbose_name = "Paybox plugin"

    class PretixPluginMeta:
        name = gettext_lazy("Paybox plugin")
        author = "Ronan Le Meillat"
        picture = "pretix_paybox/Up2Pay_eTransactions.svg"
        description = gettext_lazy("Paybox payment plugin for Pretix 4")
        visible = True
        version = __version__
        category = "PAYMENT"
        compatibility = "pretix>=4.0.0"

    def ready(self):
        from . import signals  # NOQA


