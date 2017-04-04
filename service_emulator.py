#/usr/bin/python3

import argparse, random, sys, time

parser = argparse.ArgumentParser("Emulator of a service processing some jobs. Use to test service startup/recovery setup.")
parser.add_argument("-j", "--job", type=int, help="Number of jobs to process.")
parser.add_argument("-l", "--latency", type=int, help="Maximum latency (in seconds) processing of one job may take.")
parser.add_argument("-f", "--failure", type=int,
	help="Service will self-destruct unless it started processing last job before specified time (in seconds).")
args = parser.parse_args()

j = args.job if args.job else 10
l = args.latency if args.latency else 1
f = args.failure if args.failure else 5

print("Service started.")
print(("Service discovered {} jobs, each with max latency of {} seconds. "
	"Unless last job is started before {} second, service will fail.").format(j, l, f))

def process_job(job, latency):
	print("Starting to process job #{}, expecting it to take {} ms.".format(job, latency))
	time.sleep(latency / 1000.0)
	print("Finished processing work job #{} .".format(job))

timer = 0
for i in range(1, j + 1):

	if timer > f * 1000:
		raise Exception("Failure. Service ran out of time. Status of {} remaining jobs is unknown.".format(j + 1 - i))

	latency = random.randint(0, l * 1000)
	try:
		process_job(i, latency)
	except:
		print("Unexpected error:", sys.exc_info()[0])
		sys.exit()

	timer += latency

print("Service finished without problems.")
