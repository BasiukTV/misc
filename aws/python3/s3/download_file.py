#/usr/bin/python3

import argparse, boto3, os, sys

# Configure command line argument parser
parser = argparse.ArgumentParser("Simple script for downoalding a file from an S3 bucket.")
parser.add_argument("bucket", help="Bucket name.")
parser.add_argument("file_path", help="Path to the file within the bucket.")
parser.add_argument("-o", "--output-path", help="Resulting path to downloaded file.")
args = parser.parse_args()

# Read command line arguments (or use default values).
b = args.bucket
f = args.file_path

o = f.split("/")[-1]
if args.output_path:
	o = args.output_path
	if os.path.exists(o):
		print("ERROR! Output path '{}' already exists.".format(o))
		sys.exit()

	dir = "".join(o.split("/")[:-1])
	if dir and (not os.path.exists(dir) or not os.path.isdir(dir)):
		print("ERROR! Outpur directory '{}' doesn't exist or not a directory.".format(dir))
		sys.exit()

print("Will attempt to dowload file '{}' from the bucket '{}'.".format(f, b))

s3 = boto3.resource('s3')
s3.meta.client.download_file(b, f, o)

print("File successfuly downloaded into '{}'".format(o))
