# Assistant to make AI prompts based on user input

import fun_text_date as td
import lao

td.banner('AI Prompt Maker v0.1')
while 1:
	ui_task = td.uInput('\n Enter the Task [00] > ')
	if ui_task == '0' or ui_task == '00':
		exit('\n Terminating program...')

	ui_objectives = td.uInput('\n Enter the Objectives [00] > ')
	if ui_objectives == '00':
		exit('\n Terminating program...')