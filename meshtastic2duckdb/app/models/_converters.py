import math
import datetime

def echo(val):
	return val

def epoch_to_str(val):
	return datetime.datetime.utcfromtimestamp(val).strftime('%Y-%m-%d %H:%M:%S')

def user_id(val):
	if   val.startswith("!"): # user
		res = 'u ' + val[1:]
	elif val.startswith("^"): # broadcast
		res = 'b ' + val[1:]
	else:
		raise ValueError(f"Not a ID: {val}")
	return res

def gps_float_to_degree_lat(val):
	return gps_float_to_degree(val, mode="lat")

def gps_float_to_degree_lon(val):
	return gps_float_to_degree(val, mode="lon")

def gps_float_to_degree(val, mode):
	## https://learn.finaldraftmapping.com/convert-decimal-degrees-dd-to-degrees-minutes-seconds-dms-with-python/

	## math.modf() splits whole number and decimal into tuple
	## eg 53.3478 becomes (0.3478, 53)
	split_deg = math.modf(val)

	## the whole number [index 1] is the degrees
	degrees  = int(split_deg[1])

	## multiply the decimal part by 60: 0.3478 * 60 = 20.868
	## split the whole number part of the total as the minutes: 20
	## abs() absoulte value - no negative
	minutes  = abs(int(math.modf(split_deg[0] * 60)[1]))

	## multiply the decimal part of the split above by 60 to get the seconds
	## 0.868 x 60 = 52.08, round excess decimal places to 2 places
	## abs() absoulte value - no negative
	seconds  = abs(round(math.modf(split_deg[0] * 60)[0] * 60,2))

	## account for E/W & N/S
	if mode == "lon":
		if degrees < 0:
			direction = "W"
		else:
			direction = "E"
	else:
		if degrees < 0:
			direction = "S"
		else:
			direction = "N"

	val = str(abs(degrees)) + u"\u00b0 " + str(minutes) + "' " + str(seconds) + "\" " + direction

	return val
