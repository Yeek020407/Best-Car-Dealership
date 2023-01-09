import sys 
from ibmcloudant.cloudant_v1 import CloudantV1
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator

def main(dict): 
    authenticator = IAMAuthenticator("yR3GYR6cf18CjjT-LChOiLbFYneiYs2fSlcXYeuIs-YM")
    service = CloudantV1(authenticator=authenticator)
    service.set_service_url("https://apikey-v2-1hep5x8vy82pqrk2werqgud9ru0dmfuuvqpfmhokzljh:5d631093e2fa1aeaa8669ce974d517ed@d969adde-2ab2-466e-b3ef-c850f5e3ab59-bluemix.cloudantnosqldb.appdomain.cloud")
    
    try:
        response = service.post_find(
                    db='reviews',
                    selector={'dealership': {'$eq': int(dict['id'])}},
                ).get_result()
        try: 
            # result_by_filter=my_database.get_query_result(selector,raw_result=True) 
            result= {
                'headers': {'Content-Type':'application/json'}, 
                'body': {'data':response} 
                }        
            return result
        except:  
            return { 
                'statusCode': 404, 
                'message': 'Something went wrong'
                }
    except:
        response = service.post_document(db='reviews', document=dict["review"]).get_result()
        try:
        # result_by_filter=my_database.get_query_result(selector,raw_result=True)
            result= {
            'headers': {'Content-Type':'application/json'},
            'body': {'data':response}
            }
            return result
        except:
            return {
            'statusCode': 404,
            'message': 'Something went wrong'
            }
        