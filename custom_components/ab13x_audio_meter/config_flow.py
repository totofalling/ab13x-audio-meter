from homeassistant import config_entries
from homeassistant.core import callback
import voluptuous as vol
from . import DOMAIN

class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1
    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        return None
    async def async_step_user(self, user_input=None):
        if self._async_current_entries():
            return self.async_abort(reason="single_instance_allowed")
        if user_input is None:
            return self.async_show_form(step_id="user", data_schema=vol.Schema({}))
        return self.async_create_entry(title="AB13X Audio Meter", data={})
