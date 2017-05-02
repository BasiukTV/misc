#/usr/bin/python3

import argparse, os, random, signal, sys, time

class SigtermException(Exception):
	pass

def sigterm_signal_handler(signum, frame):
	raise SigtermException

# Configure sigterm signal to raise SigtermException
signal.signal(signal.SIGTERM, sigterm_signal_handler)

# Configure command line argument parser
parser = argparse.ArgumentParser("Emulator of a service processing some jobs. Use to test service startup/recovery setup.")
parser.add_argument("-j", "--job", type=int, help="Number of jobs to process.")
parser.add_argument("-l", "--latency", type=int, help="Maximum latency (in seconds) processing of one job may take.")
parser.add_argument("-f", "--failure", type=int,
	help="Service will self-destruct unless it started processing last job before specified time (in seconds).")
args = parser.parse_args()

# Read command line arguments (or use default values).
j = args.job if args.job else 10
l = args.latency if args.latency else 1
f = args.failure if args.failure else 5

print("Service started. PID: {}".format(os.getpid()))
print(("Service discovered {} jobs, each with max latency of {} seconds. "
	"Unless last job is started before {} second, service will fail.").format(j, l, f))

def process_job(job_index, latency):
	print("Starting to process job #{}, expecting it to take {} ms.".format(job_index, latency))
	time.sleep(latency / 1000.0)
	print("Finished processing job #{}.".format(job_index))

timer = 0
# Job processing loop
for i in range(1, j + 1):
	job_latency = random.randint(0, l * 1000)

	try:
		if timer > f * 1000:
			raise Exception("Service ran out of time.")

		process_job(i, job_latency)
	except SigtermException as e:
		print("Received a signal to terminate. Processing of {} remaining jobs canceled gracefully.".format(j + 1 - i))
		sys.exit()
	except Exception as e:
		print("Unexpected exception: {} Status of {} remaining jobs is unknown.".format(e, j + 1 - i))
		sys.exit()
	except:
		print("Unexpected system signal: {} Status of {} remaining jobs is unknown.".format(sys.exc_info()[0], j + 1 - i))
		sys.exit()

	timer += job_latency

print("Service finished without problems.")
