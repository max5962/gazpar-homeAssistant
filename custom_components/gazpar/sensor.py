from homeassistant.helpers.entity import Entity
from homeassistant.components.sensor import PLATFORM_SCHEMA
import homeassistant.helpers.config_validation as cv
from datetime import datetime, timedelta
from homeassistant.const import (
    CONF_LATITUDE, CONF_LONGITUDE, CONF_ELEVATION)
import voluptuous as vol
import logging
import sys
from gazpart import *
ATTR_NAME = "Station name"
ATTR_LAST_UPDATE = "Last update"

CONF_GRDF_LOGIN = 'grdfLogin'
CONF_GRDF_PASSWORD = 'grdfPassword'

SCAN_INTERVAL = timedelta(seconds=3600)



# Validation of the user's configuration
PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Optional(CONF_GRDF_LOGIN): cv.string,
    vol.Optional(CONF_GRDF_PASSWORD): cv.string,
})


def setup_platform(hass, config, add_devices, discovery_info=None):
    #from .old import PrixCarburantClient
    logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)
    logging.info("[gazpart] start")
    """Setup the sensor platform."""
    login = config.get(CONF_GRDF_LOGIN)
    password = config.get(CONF_GRDF_PASSWORD)
    # Try to log in Enedis API
    try:
       logging.info("logging in GRDF URI %s...", gazpar.API_BASE_URI)
       token = gazpar.login(login,password)
       logging.info("logged in successfully!")
    except:
       logging.error("unable to login on %s : %s", gazpar.API_BASE_URI, exc)
    add_devices([Gazpar(token,gazpar)])


class Gazpar(Entity):
    """Representation of a Sensor."""

    def __init__(self, token, gazpar):
        """Initialize the sensor."""
        self._state = None
        self.token = token
        self.gazpar = gazpar
        self._state = ""
    
    def _dayToStr(date):
        return date.strftime("%d/%m/%Y")
   
    # Sub to get StartDate depending today - daysNumber
    def _getStartDate(today, daysNumber):
        return _dayToStr(today - relativedelta(days=daysNumber))

    # Get the midnight timestamp for startDate
    def _getStartTS(daysNumber):
        date = (datetime.datetime.now().replace(hour=12,minute=0,second=0,microsecond=0) - relativedelta(days=daysNumber))
        return date.timestamp()

    # Get the timestamp for calculating if we are in HP / HC
    def _getDateTS(y,mo,d,h,m):
        date = (datetime.datetime(year=y,month=mo,day=d,hour=h,minute=m,second=0,microsecond=0))
        return date.timestamp()

    @property
    def name(self):
        """Return the name of the sensor."""
        return 'Gazpar'

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._state

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement."""
        return "€"

    @property
    def device_state_attributes(self):
        """Return the device state attributes of the last update."""

        attrs = {
            ATTR_ID: "",
        }
        return attrs

    def update(self):
        """Fetch new state data for the sensor.

        This is the only method that should fetch new data for Home Assistant.
        """
        startDate = _getStartDate(datetime.date.today(), args.days)
        endDate = _dayToStr(datetime.date.today())
        resGrdf = gazpar.get_data_per_day(token, startDate, endDate)

        for d in resGrdf:
          # Use the formula to create timestamp, 1 ordre = 30min
          t = datetime.datetime.strptime(d['date'] + " 12:00", '%d-%m-%Y %H:%M')
          logging.info(("found value : {0:3} kWh / {1:7.2f} m3 at {2}").format(d['kwh'], d['mcube'], t.strftime('%Y-%m-%dT%H:%M:%SZ')))
        

        #self.client.reloadIfNecessary()
        #if self.client.lastUpdate == self.lastUpdate:
        #    logging.debug("[UPDATE]["+self.station.id+"] valeur a jour") 
        #else:
        #    logging.debug("[UPDATE]["+self.station.id+"] valeur pas a jour")
        #    list = []
        #    list.append(str(self.station.id))
        #    myStation = self.client.extractSpecificStation(list)
        #    self.station = myStation.get(self.station.id)
        #    self.lastUpdate=self.client.lastUpdate
        #
        #self._state = self.station.gazoil['valeur']
        #self.client.clean()
