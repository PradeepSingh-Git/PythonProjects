




def MIN_MAX_1(act_res):
	'''
	A generic function to evaluate if the value is in between a specified range
	make sure to pass proper parameters:
	MIN=response containing Minimum vlaue to check for
	MAX=response containing Maximum vlaue to check for
	POS= the position from where the significant/bytes to check start except for the first 6 pos(the default resp)
	SIZE= the size in bytes to check
	act_res = this will be automatically fetched(do not change var name)

	eg.;	MIN="62FD472E7C0000"
			MAX="62FD472F440000"
			POS=0
			SIZE=2

	'''
	#[MIN]:62 FD 47 (2E 7C) 00 00
	#[MAX]:62 FD 47 (2F 44) 00 00
	MIN="2E7C"
	MAX="2F44"
	POS=0
	SIZE=2
	'''size in bytes'''
	EXP_RES=''
   	return_tracker=1#The purpose of this tracker is for tracking multiple returns
   	#make sure any new functions you create return 1 on success and 0 on failure
 	return_tracker *= min_max_generic(MIN,MAX,POS,SIZE,act_res)

 	if(return_tracker==1):
 		print "ret 1"
 		return 1

 	else:
 		return 0

 	return 0#default return do not remove

def MIN_MAX_2(act_res):

	MIN="2E7C"
	MAX="2F44"
	POS=0
	SIZE=2
	'''size in bytes for bits keep SIZE=0(zero)'''
	EXP_RES=''
   	return_tracker=1#The purpose of this tracker is for tracking multiple returns from local functions
   	#make sure any new functions you create return 1 on success and 0 on failure
 	return_tracker *= min_max_generic(MIN,MAX,POS,SIZE,act_res)
 	if(return_tracker==1):
 		print "ret 1"
 		return 1

 	else:
 		return 0

 	return 0#default return do not remove


	#FUNC:"MIN_MAX_1"
def MIN_MAX_3(act_res):
	return 0

def MIN_MAX_4(act_res):
	return 0

def CHECK_BYTE_1(act_res):
	return 0



def SEARCH_DTC_1(canObj, act_res):
	'''
	A generic function to search if the dtc is in response
	make sure to pass proper parameters:
	DTC=DTC vlaue to check for
	act_res = this will be automatically fetched(do not change var name)

	eg.;	DTC="9A5916"

	'''
	#[MIN]:62 FD 47 (2E 7C) 00 00
	#[MAX]:62 FD 47 (2F 44) 00 00
	DTC="9A5916"
	return_tracker=1#The purpose of this tracker is for tracking multiple returns
	#make sure any new functions you create return 1 on success and 0 on failure
	return_tracker *= SEARCH_DTC_generic(DTC,act_res)
	return_tracker *= canObj.dgn.is_dtc_in_response(DTC, act_res)
	if(return_tracker==1):
		print "ret 1"
		return 1

	else:
		return 0

	return 0#default return do not remove














def min_max_direct(exp_res_min,exp_res_max,act_res):
	# exp_res='[MIN]:62FD47(2E7C)0000[MAX]:62FD47(2F44)0000'
	# act_res='62FD472EFC0000'
	# exp_res_max='[MAX]:62 FD 47 (2F 44) 00 00 '
 	# exp_res_min='[MIN]:62 FD 47 (2E 7C) 00 00'
 	try:
		exp_res_max  = exp_res_max.upper()
		exp_res_max  = exp_res_max.replace(' ','')
		exp_res_max  = exp_res_max.split(':')[1]
		exp_res_min  = exp_res_min.upper()
		exp_res_min  = exp_res_min.replace(' ','')
		exp_res_min  = exp_res_min.split(':')[1]
		start_index	 = exp_res_max.find('(')+1
		stop_index	 = exp_res_max.find(')')
		MAX_VAL		 = exp_res_max[start_index:stop_index]
		MIN_VAL		 = exp_res_min[start_index:stop_index]



		print "\n"+'MAXVAL====>>'+MAX_VAL+'\n'
		print "\n"+'MINVAL====>>'+MIN_VAL+'\n'



		MIN_VAL='0x' + MIN_VAL
		MIN_VAL=int(MIN_VAL,16)
		MAX_VAL='0x' + MAX_VAL
		MAX_VAL=int(MAX_VAL,16)
		#act_res does not contain brackets so indexes start and stop are subtracted by 1
		Actual_rangevalue = '0x' + act_res[start_index-1:stop_index-1]
		print Actual_rangevalue+"------------1"
		Actual_rangevalue = int(Actual_rangevalue,16)


		print act_res[start_index-1:stop_index-1]
		print Actual_rangevalue
		print MIN_VAL
		print MAX_VAL
		#if (EXP_RES[POS:(POS+(SIZE*2))] == act_res[POS:(POS+(SIZE*2))]):
		if ((Actual_rangevalue >= MIN_VAL) and (Actual_rangevalue <= MAX_VAL)):
			print "return1"
			return 1
		else:
			print "return0"
			return 0
	except:

		print "user_defined_api.py:Error in min_max_direct "



def min_max_generic(MIN,MAX,POS,SIZE,act_res):
	try:
		POS+=6
		Actual_rangevalue = '0x' + act_res[POS:(POS+(SIZE*2))]
		print Actual_rangevalue+"------------1"
		Actual_rangevalue = int(Actual_rangevalue,16)

		MIN_VAL='0x' + MIN
		MIN_VAL=int(MIN_VAL,16)
		MAX_VAL='0x' + MAX
		MAX_VAL=int(MAX_VAL,16)

		print act_res[POS:(POS+(SIZE*2))]
		print Actual_rangevalue
		print MIN_VAL
		print MAX_VAL
		#if (EXP_RES[POS:(POS+(SIZE*2))] == act_res[POS:(POS+(SIZE*2))]):
		if ((Actual_rangevalue >= MIN_VAL) and (Actual_rangevalue <= MAX_VAL)):
			return 1

			print "return1"
		else:
			return 0
	except:
		print "user_defined_api.py: Error in min_max_generic "


def dontCareCheck_default(expectedResponse,actualResponse):
	count=0
	ret=0

	for expec_letter in expectedResponse:
		if(expec_letter=='X' or expec_letter=='x'):
			count+=1
			break
		elif(expec_letter==actualResponse[count]):
			count+=1
			ret*=1
		else:
			count+=1
			ret*=0
	print 'Performed Test on specific byte '

	return ret


def rangeCheck_default(expectedResponse,actualResponse):

	return 0


def searchDTC_default(dtc, response):
	'''
	Description: Checks if provided DTC is present in the response of a readDTCs service.
	Returns: True or False

	Example:
		dtcs = dgn.read_dtcs([0x02, 0x08])
		if dgn.is_dtc_in_response([0xe0, 0x10, 0x15], dtcs):
			print 'DTC E01015 is present'
	'''
	try:
		if(response[0:2] != '7F'):
			for i in range(3, len(response) - 3, 4):
				rdtc = [response[i], response[i+1], response[i+2]]
				if dtc == rdtc:
					return 1
			return 0
		else:
			return 0
	except:

		print "user_defined_api.py: Error in searchDTC_default "

