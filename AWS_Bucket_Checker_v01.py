# Checks the contents of an AWS S3 bucket and returns the number of files in the bucket

import aws
import fun_text_date as td
import lao
from pprint import pprint
import requests
import subprocess
import webs
import xml.etree.ElementTree as ET

def menu():
	print('\n AWS Bucket Checker v01')
	print('\n  1) Check if OPR maps are in bucket')
	print('  2) List PDF files in bucket')
	print('  3) List all files in bucket')
	print(' 00) to quit')
	ui = input('\n Enter choice > ')
	return ui

def check_bucket():
	bucket_name = 'lao-landadvisors'
	url = f'https://s3.amazonaws.com/{bucket_name}/'
	resp = requests.get(url)
	if resp.status_code == 200:
		print(f'\n Bucket {bucket_name} exists')
		print(f' Number of files in bucket: {len(resp.text)}')
	else:
		print(f'\n Bucket {bucket_name} does not exist')

def list_pdf_files_in_bucket():
	# r = aws s3 ls s3://request-server/maps/
	r = requests.get('https://request-server.s3.amazonaws.com/maps/maintain_mm_mi_lists_v04.pdf')

	pprint(r.text)

	ui = td.uInput('\n Continue [00]... > ')
	if ui == '00':
		exit('\n Terminating program...')

while 1:
	lao.banner('AWS Bucket Checker v01')
	ui = menu()
	if ui == '00':
		exit('\n Terminating program...')
	elif ui == '1':
		PID = input('\n Enter PID > ')
		if aws.aws_file_exists(PID, extention='jpg', verbose=False):
			print(f'\n OPR Map for {PID} exists in bucket')
		else:
			print(f'\n OPR Map for {PID} does not exist in bucket')
		ui = td.uInput('\n Continue [00]... > ')
		if ui == '00':
			exit('\n Terminating program...')
	elif ui == '2':
		list_pdf_files_in_bucket()
	elif ui == '3':
		lUsers = ['avidela', 'blandis', 'cheuser', 'iwade', 'lkane', 'lcoxworth', 'lsweetser', 'msosongkham', 'mklingen', 'tjacobson']
		for user in lUsers:
			print(f'\n User: {user}')
			folder_aws = f's3://research-datastore/{user}/'
			result = subprocess.run(f'aws s3 ls {folder_aws} --output text', stdout = subprocess.PIPE, text=True)
			pprint(result.stdout)
		ui = td.uInput('\n Continue [00]... > ')
		if ui == '00':
			exit('\n Terminating program...')