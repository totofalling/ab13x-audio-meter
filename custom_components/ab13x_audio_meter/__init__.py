from __future__ import annotations
import logging
import asyncio
from datetime import timedelta
import aiohttp
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

DOMAIN = "ab13x_audio_meter"
API = "http://local-ab13x-audio-meter:8765"
PLATFORMS = ["sensor", "number", "switch"]

async def async_setup(hass: HomeAssistant, config: dict) -> bool:
    return True

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    session = aiohttp.ClientSession()
    async def update():
        try:
            async with session.get(f"{API}/state", timeout=aiohttp.ClientTimeout(total=2)) as r:
                if r.status != 200:
                    raise UpdateFailed(f"HTTP {r.status}")
                return await r.json()
        except Exception as e:
            raise UpdateFailed(str(e)) from e
    coordinator = DataUpdateCoordinator(
        hass, logging.getLogger(__name__), name="AB13X Audio Meter", update_method=update,
        update_interval=timedelta(seconds=0.5),
    )
    await coordinator.async_config_entry_first_refresh()
    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = (coordinator, session)
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    data = hass.data[DOMAIN].pop(entry.entry_id)
    coordinator, session = data
    await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    await session.close()
    return True
