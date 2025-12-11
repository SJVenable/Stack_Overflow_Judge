import requests
from bs4 import BeautifulSoup
import html
from judge_results import Order
from numpy import random

# Get the question title and explanation (title and body) in plain text
def get_question(qid: str):
    # Take a given S/O URL
    detail_url = f"https://api.stackexchange.com/2.3/questions/{qid}?order=desc&sort=activity&site=stackoverflow&filter=withbody"
    # Get the HTML response
    detail_response = requests.get(detail_url, timeout=10)
    detail_response.raise_for_status()

    # Convert to JSON and extract the title and question
    detail_data = detail_response.json()
    title = str(detail_data['items'][0]['title'])
    rawbody = str(detail_data['items'][0]['body'])
    body = BeautifulSoup(rawbody, 'html.parser').get_text()
    full_question = "\n\n**" + title + "**\n\n" + body
    # After converting them to text, return the full question (title and body)
    return full_question

# Gets the first 5 answers for a question and returns them in order, inside a 2d array like so: [owner_id, answer]
def get_first_5_answers_arr(qid: str):
    # Get the answers URL from SO API
    answers_url = f"https://api.stackexchange.com/2.3/questions/{qid}/answers?order=desc&sort=votes&site=stackoverflow&filter=withbody"
    answers_response = requests.get(answers_url, timeout=10)
    answers_response.raise_for_status()
    # Convert HTML to JSON
    answers_data = answers_response.json()
    if not answers_data or not answers_data['items']:
        print("Invalid question ID")
        return None
    answers_arr = []

    for i in range(5):
        # Stop if there aren't 5
        if i >= len(answers_data['items']):
            break
        # Get the owner id
        owner_id = answers_data['items'][i]['owner']['user_id']
        # Get the body of the answer
        body = BeautifulSoup(answers_data['items'][i]['body'], 'html.parser').get_text()
        answers_arr.append([owner_id, body])
    return answers_arr
    
    
def get_answers(qid: str, order: Order):
    answers_arr = get_first_5_answers_arr(qid)
    if order == Order.ORDERED:
        return '\n'.join(answers_arr)
    elif order == Order.REVERSED:
        return '\n'.join(answers_arr.reverse())
    else: return '\n'.join(answers_arr)

def get_answer_order(qid: str):
    # Get the answers URL from SO API
    answers_url = f"https://api.stackexchange.com/2.3/questions/{qid}/answers?order=desc&sort=votes&site=stackoverflow&filter=withbody"
    answers_response = requests.get(answers_url, timeout=10)
    answers_response.raise_for_status()
    # Convert HTML to JSON
    answers_data = answers_response.json()
    if not answers_data or not answers_data['items']:
        print("Invalid question ID")
        return None
    votes_dict = dict()
    for i in range(5):
        # Stop if there aren't 5
        if not answers_data['items'][i]:
            break
        votes_dict[answers_data['items'][i]['owner']['user_id']] = i+1
    return votes_dict

get_first_5_answers_arr('3216013')