# Test web page scrapes for contacts
# TruePeopleSearch.com
# FastPeopleSearch.com
# OpenCorporates.com

import acc
import bb
import dicts
import fun_login
import lao
import fun_text_date as td
from pprint import pprint

service = fun_login.TerraForce()

td.banner('Contact Webscrape Tester v01')

dAcc = dicts.get_blank_account_dict()

dAcc['ENTITY'] = td.uInput(' Enter contact Entity or Person > ')

dAcc = acc.find_create_account_entity(service, dAcc)

dAcc = acc.find_create_account_person(service, dAcc)

pprint(dAcc)
