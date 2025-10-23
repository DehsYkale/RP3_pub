# import openai
# import streamlit
import ai
import csv
import lao
from openai import OpenAI
import os
from pprint import pprint
import json
import fun_text_date as td


def get_vizzda_event_ids():
	lViz_ids = []
	with open(filename_out, 'r') as f:
		fin = csv.reader(f)
		for row in fin:
			lViz_ids.append(row[0])
	return lViz_ids

def get_vizzda_data():
	dViz = lao.spreadsheetToDict(filename_in)
	viz_blocks = ''
	count = 1
	dViz_master = {}
	# print('here2')
	for row in dViz:
		# print('here3')
		# print(dViz[row]['Event Id'])
		# print(lViz_ids)
		# exit()
		if str(dViz[row]['Event Id']) in lViz_ids:
			print(' skipping...')
			continue
		elif count <= 5:
			viz_id = dViz[row]['Event Id']
			viz_txt = dViz[row]['Notes']
			viz_blocks = f'{viz_blocks}::[{viz_id}]:{viz_txt}'
			count += 1
		else:
			
			# Remove the first ::
			viz_blocks = viz_blocks.replace('::', '', 1)
			messages = ai.get_ai_message(role_system='VIZZDA', role_user=viz_blocks)
			# pprint(messages)
			# completion = None
			while 1:
				try:
					print('\n Sending to OpenAI...')
					print('here6')
					completion = client.chat.completions.create(model="gpt-3.5-turbo", messages=messages)
					print('here7')
					pprint(completion.choices[0].message)
					pprint(completion.choices[0].message.content)
					content = completion.choices[0].message.content[0]
					content = content.replace("'''json\n", "").replace("}\n```", "")
					pprint(content)
					content_dict = json.loads(completion.choices[0].message.content)
					break
				except (json.decoder.JSONDecodeError):
					td.warningMsg('\n Json file error...')
					ui = td.uInput('\n Continue [00]... > ')
					if ui == '00':
						exit('\n Terminating program...')

			with open(filename_out, 'a', newline='') as f:
				fout = csv.writer(f)
				for key in content_dict:
					f1 = content_dict[key]['Last Sale Amount']
					f2 = content_dict[key]['Lender']
					f3 = content_dict[key]['Loan Amount']
					f4 = content_dict[key]['Loan Date']
					f5 = content_dict[key]['Owner Entity']
					f6 = content_dict[key]['Owner Person']
					line = [key, f1, f2, f3, f4, f5, f6]
					fout.writerow(line)
			count = 1
			viz_blocks = ''
			# ui = td.uInput('\n Continue here1 [00]... > ')
			# if ui == '00':
			# 	exit('\n Terminating program...')
		
	# return dViz_master


td.banner('AI Vizzda Loan Amount')

client = OpenAI()
filepath = 'F:/Research Department/MIMO/zData/Debt/Vizzda/'
# inxlsx = 'Vizzda Debt 2024-09-22.xlsx'
filename = lao.guiFileOpen(path=filepath, titlestring='Open Vizzda Export XLSX', extension=[('Excel files', '.xlsx'), ('all files', '.*')])
inxlsx = os.path.basename(filename)
filename_in = f'{filepath}{inxlsx}'
outcsv = 'dViz_master.csv'
filename_out = f'{filepath}{outcsv}'

lViz_ids = get_vizzda_event_ids()

get_vizzda_data()

lao.openFile(filename_out)

exit('\n Fin...')