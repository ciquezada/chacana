import astropy.units as u
from astropy.time import Time
from astropy.coordinates import SkyCoord, EarthLocation, AltAz
from datetime import datetime


EL_SAUCE = EarthLocation(lat=-30.4726064*u.deg, lon=-70.7653747*u.deg, height=789*u.m)
obs_time = "2019-9-10 08:30:10"
alt_az_frame = AltAz(obstime=Time(obs_time), location=EL_SAUCE)
c = SkyCoord("01h37m42.9s", "-57d14m12s", frame='icrs')
c_altaz = c.transform_to(alt_az_frame)
c_altaz
