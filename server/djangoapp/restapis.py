import requests
import json
# import related models here
from .models import CarModel, CarMake, CarDealer,DealerReview
from requests.auth import HTTPBasicAuth
from decouple import config
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
from ibm_watson import NaturalLanguageUnderstandingV1
from ibm_watson.natural_language_understanding_v1 import Features, SentimentOptions


# Create a `get_request` to make HTTP GET requests
# e.g., response = requests.get(url, params=params, headers={'Content-Type': 'application/json'},
#                                     auth=HTTPBasicAuth('apikey', api_key))

def get_request(url,**kwargs):
    print(kwargs)
    print("GET from {} ".format(url))

    try:
        response = requests.get(url,headers={'Content-Type':'application/json'},
                                    params=kwargs)
    except:
        print("Network exception occurred")

    status_code = response.status_code
    print("With status {} ".format(status_code))
    json_data=json.loads(response.text)
    return json_data


# Create a `post_request` to make HTTP POST requests
# e.g., response = requests.post(url, params=kwargs, json=payload)


# Create a get_dealers_from_cf method to get dealers from a cloud function
# def get_dealers_from_cf(url, **kwargs):
# - Call get_request() with specified arguments
# - Parse JSON results into a CarDealer object list
def get_dealers_from_cf(url,**kwargs):
    results=[]
    json_result=get_request(url)

    for dealer in json_result:
        
        dealer_doc = dealer["doc"]
        dealer_obj = CarDealer(address=dealer_doc["address"],city=dealer_doc["city"],full_name = dealer_doc["full_name"],
                                id=dealer_doc["id"],lat=dealer_doc["lat"],long=dealer_doc["long"],short_name=dealer_doc["short_name"],
                                st=dealer_doc["st"],zip=dealer_doc["zip"],state=dealer_doc["state"])
        results.append(dealer_obj)
    
    return results



def get_dealer_by_id(url,dealerId):
    results=[]
    json_result=get_request(url,id=dealerId)
    for dealer in json_result:
        
        
        dealer_obj = CarDealer(address=dealer["address"],city=dealer["city"],full_name = dealer["full_name"],
                                id=dealer["id"],lat=dealer["lat"],long=dealer["long"],short_name=dealer["short_name"],
                                st=dealer["st"],zip=dealer["zip"],state=dealer["state"])
        results.append(dealer_obj)
    
    return results[0]



# Create a get_dealer_reviews_from_cf method to get reviews by dealer id from a cloud function
# def get_dealer_by_id_from_cf(url, dealerId):
# - Call get_request() with specified arguments
# - Parse JSON results into a DealerView object list

def get_dealer_by_id_from_cf(url,dealerId):
    results=[]
    json_result=get_request(url,id=dealerId)
    review_list = json_result['data']['docs']
    for review in review_list:
        review_text = review['review']
        sentiment = analyze_review_sentiments(review_text)
        review_obj = DealerReview(dealership = review['dealership'],
                                name = review['name'],purchase = review['purchase'],
                                review = review['review'],purchase_date = review['purchase_date'],
                                car_make = review['car_make'],car_model = review['car_model'],
                                car_year = review['car_year'],id = review['id'],sentiment=sentiment)
        results.append(review_obj)

    
    return results



# Create an `analyze_review_sentiments` method to call Watson NLU and analyze text
# def analyze_review_sentiments(text):
# - Call get_request() with specified arguments
# - Get the returned sentiment label such as Positive or Negative

def analyze_review_sentiments(text):
    api_key = config("NLU_API_KEY")
    url = config("NLU_URL")
    version ='2019-07-12'
    authenticator = IAMAuthenticator(api_key)
    nlu = NaturalLanguageUnderstandingV1(version=version,authenticator=authenticator)
    nlu.set_service_url(url)

    try:
        response = nlu.analyze(text=text,features=Features(sentiment=SentimentOptions())).get_result()

        sentiment_label = response['sentiment']['document']['label']

    except:
        sentiment_label = "neutral"

    return sentiment_label


def post_request(url,json_payload,**kwargs):
    response = requests.post(url,params=kwargs,json=json_payload)



