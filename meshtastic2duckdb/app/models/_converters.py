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
