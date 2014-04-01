# -*- coding: utf-8 -*-
import subprocess
import inspect
from django.conf import settings
from django.utils.encoding import smart_str

class SlimPayManager(object):

    def __init__(self, *args, **kwargs):
        self.PREFIX_COMMAND = ["java -Dfile.encoding=UTF-8 -Dlog4j.configuration=file:%s -Dscim.home=%s -jar %s"  % (settings.SLIMPAY_LOGGER_CONFIG, settings.SLIMPAY_SCIM_HOME, settings.SLIMPAY_SCIM_JAR_FILE)]


    def execute_command(self, arguments):
        content = '\n'.join('{}="{}"'.format(key, val) for key, val in arguments.items())
        pipe = subprocess.Popen(self.PREFIX_COMMAND, shell=True, stdout=subprocess.PIPE,
                 stdin=subprocess.PIPE, stderr=subprocess.PIPE)
        
        blob = pipe.communicate(content)[0]

        return blob
	
    def decodeBlob(self, blob):
        args = {
            'response': blob
        }

        response = dict(e.split('=') for e in self.execute_command(args).split('&'))

        return response

    def initRequest(self, clientInitializationUrl, mode, siteId, returnUrl, notifyUrl):
		args = {
			'requestType': 'init',
			'mode': mode,
			'siteId': siteId,
			'clientInitializationUrl': clientInitializationUrl,
 			'notifyUrl': notifyUrl,
 			'returnUrl': returnUrl
 		}

 		return self.execute_command(args)

    def transactionRequest(self, requestType, clientReference, contactFN, contactLN, Iline1, Icity, IpostalCode, Icountry, 
            transactionId=None, clientType=None,  companyName=None, organizationId=None, contactTitle=None,
            contactEmail=None, contactPhone=None, Iline2=None, Dline1=None, Dline2=None, Dcity=None, DpostalCode=None, 
            Dcountry=None, invoiceReference=None, bic=None, iban=None, RUM=None, unitCollectPayment=None, debitAmount=None, 
            debitExecutionDate=None, debitLabel=None, recurrentCollectPayment=None, recurrentDebitAmount=None, recurrentDebitExecutionDate=None,
            recurrentDebitLabel=None, frequency=None, recurrentMaxNumber=None, cardOperation=None, cardAmount=None,
            cardLabel=None, recurrentCardOperation=None, recurrentCardAmount=None, recurrentCardExecutionDate=None,
            recurrentCardLabel=None, recurrentCardFrequency=None, locale=None, branchId=None, creditorId=None):

            
        frame = inspect.currentframe()

        args, _, _, values = inspect.getargvalues(frame)
            
        return self.execute_command(dict((k, v) for k, v in values.iteritems() if v and k in args and k != 'self'))