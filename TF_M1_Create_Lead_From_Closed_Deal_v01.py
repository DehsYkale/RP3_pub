# #!/usr/bin/env python
# -*- coding: utf-8 -*-


import aws
import bb
import fun_login
import fun_text_date as td
import lao

service = fun_login.TerraForce()

while 1:
	lao.banner('TF M1 Create Lead From Closed Deal v01')
	salePID = (td.uInput(' Enter PID > ')).strip()
	DID = bb.getDIDfromPID(service, salePID)
	leadPID = bb.tf_create_lead_of_sale_deal(service, PID=salePID, DEALID=DID)
	ui = td.uInput('\n Create another Lead [0/1/00] > ')
	if ui != '1':
		exit('\n Program terminated...')



