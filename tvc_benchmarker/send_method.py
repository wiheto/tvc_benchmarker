import requests
import inspect


def send_method(method_code,param_code,author_name=None,method_name=None,email_address=None,publications=None,agree_dfcbenchmarker=None,agree_teneto=None,email_list=None):


    privacy = input('All data provided here is saved by tvc_benchmarker. It is sent via Google Forms and the data provided will be stored on a (private) Google Spreadsheet. By continuing you agree to this. Press "y" and enter to continue: ')

    if privacy != 'y':
        print('Not agreed to sending information. Not continuing.')
        return

    if not isinstance(method_code,list):
        method_code = [method_code]

    if isinstance(param_code,dict):
        param_code = [param_code]
    elif not isinstance(param_code,list):
        raise valueError('incorrect parameter format')

    method_code_text = ''
    for f in method_code:
        if not callable(f):
            raise('funcitons must be callable')
        method_code_text += inspect.getsource(f)
        method_code_text += '\n'

    if not author_name:
        author_name = input('Please specify author name(s): ')

    if not method_name:
        method_name = input('Please specify method name: ')

    if not email_address:
        email_address = input('Please specify email address: ')

    if not publications:
        publications = input('Please specify publication(s) to credit method (full reference, PMID or DOI) [OPTIONAL, leave blank if none]: ')

    if not agree_dfcbenchmarker:
        agree_dfcbenchmarker = input('Agree for tvc_benchmarker to use code in future releases (with credit to published reference) [Yes or No]: ')

    if agree_dfcbenchmarker.capitalize() != 'Yes' and agree_dfcbenchmarker.capitalize() != 'Y':
        raise ValueError('Must agree that tvc_benchmarker can use the code if sending to tvc_benchmarker')

    if not email_list:
        email_list = input('Do you want to receive updates from tvc_benchmarker (e.g. when we release new reports)? [OPTIONAL] [Yes or No]: ')

    if not agree_teneto:
        agree_teneto = input('Agree for teneto to use code in future releases (with credit to published reference) [OPTIONAL] [Yes or No]: ')

    url = 'https://docs.google.com/forms/d/e/1FAIpQLSfaMtpSGkgjB2bh2D34xY0z09S_RzLsiyDukF47_9Um4udb7g/formResponse'
    form_data = {'entry.2005620554': author_name,
                'entry.1464144212': email_address,
                'entry.1259855693': method_name,
                'entry.1166974658': publications,
                'entry.839337160': method_code_text,
                'entry.1676341971': str(param_code),
                'entry.1283101604': agree_dfcbenchmarker.capitalize(),
                'entry.1308527282': agree_teneto.capitalize(),
                'entry.702133873': email_list.capitalize(),
                'draftResponse':[],
                'pageHistory':0}
    user_agent = {'Referer':'https://docs.google.com/forms/d/e/1FAIpQLSfaMtpSGkgjB2bh2D34xY0z09S_RzLsiyDukF47_9Um4udb7g/viewform','User-Agent': "Mozilla/5.0 (X11; Linux i686) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/28.0.1500.52 Safari/537.36"}
    r = requests.post(url, data=form_data, headers=user_agent)

    if r.status_code == 200:
        print('Everything got sent successfully. \n If no confirmation e-mail is received, contact DFCBenchmarker [ at ] gmail')
    else:
        print('Something went wrong. If problem persists, visit https://docs.google.com/forms/d/e/1FAIpQLSfaMtpSGkgjB2bh2D34xY0z09S_RzLsiyDukF47_9Um4udb7g/formResponse for manual entry')
