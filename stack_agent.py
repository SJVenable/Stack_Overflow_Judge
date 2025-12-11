
from langchain_ibm import ChatWatsonx
from dotenv import load_dotenv

from typing import Dict, List
from pydantic import BaseModel, Field
from retrieve_question_details import get_question, get_first_5_answers_arr
from judge_results import Order, JudgeResults

load_dotenv()

# Define the LLM
parameters = {
    "decoding_method": "sample",
    "max_new_tokens": 1000,
    "min_new_tokens": 1,
    "temperature": 0.5,
    "top_k": 50,
    "top_p": 1,
}
watsonx_llm = ChatWatsonx(
    model_id="ibm/granite-4-h-small",
    url="https://us-south.ml.cloud.ibm.com",
    project_id="e5587637-d927-4b71-8571-ed8624e418a5",
    params=parameters,
)

# Define how the LLM should answer a question (in this case, a dictionary with owners and their answers' score)
class AnswerRanking(BaseModel):
    """Ranking of stack overflow answers, where each entry has a key of the author's ID, and a value of the rating for their answer."""
    rankings: Dict[str, int] = Field(description="Dictionary containing owner IDs as keys, and scores (1-10) as values")

# Set the llm to give the AnswerRanking output
answer_ranking_llm = watsonx_llm.with_structured_output(AnswerRanking)

class AnswerEvaluation(BaseModel):
    """Ranking of an answer for a stack overflow question, as a dictionary mapping each of these 4 attributes to an appropriate score for the given answer.
    The 4 attributes each answer will be evaluated on are:
        1. Accuracy - How correct the answer is with its technical accuracy
        1. Relevance - How well the answer actually tackles the question given
        3. Clarity - How clear the author is in expressing their answer/solution in terms which may be easily understood by the questioner
        4. Conciseness - Is the question thorough but avoiding unnecessary verbosity? 
    A dictionary will be returned, with each attribute as a key, and each score as the value for that key"""
    attribute_rankings: Dict[str, int] = Field(description="Dictionary containing evaluation scores for each attribute (Accuracy, Relevance, Clarity and Conciseness)")

# Set the LLM to give Answer evaluation format
answer_evaluation_llm = watsonx_llm.with_structured_output(AnswerEvaluation)

def orderAnswers(ans, order):
    """Helper function to order an array of answers based on a given Order type"""
    #print(ans)
    if order == Order.REVERSED:
        ans.reverse()
    elif order == Order.SHUFFLED:
        ans.shuffle()
    answer_str = ""
    for i in range(len(ans)):
        answer_str += "**Answer " + str(i) + ", written by author " + str(ans[i][0]) + "** \n\n" + str(ans[i][1] + "\n\n")
    return answer_str

def createOrderedQuestionPrompt(prompt: str, question: str, answers: str):
    """Create a prompt based on the basic information it has to be given"""
    return prompt + "\nHere is the question" + question + "\n And here are the given answers: " + answers

def createAnswerEvaluationPrompt(prompt: str, question: str, answer: str):
    """Create a prompt for a single answer to be evaluated"""
    return prompt + "\nHere is the question" + question + "\n And here is the given answer: " + answer

# Calculate the score
def calculateScore(given_ans: AnswerRanking, actual_order: List[str]) -> int:
    """Calculate score for how close to the actual order the evaluation was"""
    rankings_int = {int(k): v for k, v in given_ans.items()}
    # print("Givenans: " + str(given_ans))
    # print("Rankings_int: " + str(rankings_int))
    # print("Ranknigns_int.items() " + str(rankings_int.items()))

    # Sort votes_dict by value descending and assign ranks 1..N (1 = highest value)
    sorted_by_value_desc = sorted(rankings_int.items(), key=lambda kv: kv[1], reverse=True)
    #print("sorted values desc: " + str(sorted_by_value_desc))
    ranked_votes = {owner_id: rank for rank, (owner_id, _) in enumerate(sorted_by_value_desc, start=1)}
    #print("Ranked votes: " + str(ranked_votes))
    score = sum([abs(ranked_votes[key] - (actual_order.index(key)+1)) for key in ranked_votes.keys()])
    #print(score)
    no_of_answers = len(actual_order)
    return int((1 - (score / get_max_score_for_n_answers(no_of_answers=no_of_answers))) * 100)

# Helper function defining the worst possible score for each number of answers (not an easy formula)
def get_max_score_for_n_answers(no_of_answers: int):
    if no_of_answers > 5:
        return 100000
    if no_of_answers == 5:
        return 12
    elif no_of_answers == 4:
        return 8
    elif no_of_answers == 3:
        return 4
    elif no_of_answers == 2:
        return 2
    else:
        return 1

#### Run over different combinations
# All IDs: '3216013', '60174', '11121352'
questionIDs = ['3216013', '60174', '11121352', '218384', '14220321', '60174', '1732348', '4660142', '588004', '513832', '12573816', '4261133', '12859942', '203198', '605845', '20279484', '18050071', '750486',
                '1452721', '23667086', '12769982', '14028959', '11922383', '40480', '3577641', '23294658', '15112125', '13840429', '240178', '3127429', '5554734', '509211', '1299871', '1132941', '10693845']
#questionIDs = ['3216013']
basePrompt = ['False', "I will give you a stack overflow question, and some answers to it, given by different authors. \
I want you to return a score for each owner's answer, giving them all in the JSON format specified."]
ignoreOrderPrompt = ['True', "I will give you a stack overflow question, and some answers for it. The answers are in **NO PARTICULAR ORDER **. \
I want you to return a score for each owner's answer, giving them all in the JSON format specified. Do not show any bias towards the order in which they are currently given."]
prompts = [basePrompt, ignoreOrderPrompt]

singleAnswerEvaluationPrompt = """
I will give you a question asked on stack overflow, and an answer which was given for it. You will evaluate the answer (give it a score out of 100) for each of 4 attributes: 
    1. Accuracy - How correct the answer is with its technical accuracy 
    2. Relevance - How well the answer actually tackles the question given 
    3. Clarity - How clear the author is in expressing their answer/solution in terms which may be easily understood by the questioner 
    4. Conciseness - Is the question thorough but avoiding unnecessary verbosity? 
With each of these answers, ground them in **what the questioner would find most useful** (i.e. which answer would likely get the most votes on stack overflow).
A dictionary will be returned, with each attribute as a key, and each score (/100) as the value for that key.
"""

results = JudgeResults(filename='test_results.csv')

for id in questionIDs:
    # Get first 5 answers in order (returns 2d array of answers with owner id and answer text)
    answers_arr = get_first_5_answers_arr(id)
    # Get the question
    question = get_question(id)

    # For each ordering of answers
    for order in Order:
       # print("ORDER: " + order.value)
        #print("unordered answers: " + str(answers_arr))
        # Order the answers in the given order
        ordered_answers = orderAnswers(answers_arr, order)
        #print("ordered answers: " + str(ordered_answers))
        # For each given prompt
        for prompt in prompts:
            llm_ans = answer_ranking_llm.invoke(createOrderedQuestionPrompt(prompt=prompt[1], question=question, answers=ordered_answers))
            score = calculateScore(llm_ans.rankings, [i[0] for i in answers_arr])
            #print("Adding id: " + str(id) + " with prompt ignore order set " + str(prompt[0]) + ", with order: " + str(order) + " and score of: " + str(score))
            results.add_score(id, prompt[0], order.value, int(score))
            #sleep(2)
    
    # Now get rankings through evaluation of each prompt seperately
    single_answer_evaluations = dict()
    for ans in answers_arr:
        llm_ans = answer_evaluation_llm.invoke(createAnswerEvaluationPrompt(prompt=singleAnswerEvaluationPrompt, question=question, answer=ans[1]))

        single_answer_evaluations[ans[0]] = sum(llm_ans.attribute_rankings.values()) / 4
    #print(single_answer_evaluations)
    question_score = calculateScore(single_answer_evaluations, [i[0] for i in answers_arr])
    results.add_score(id, "N/A", "Separate", question_score)

# Compare the difference between with the positional prompt and without, with the reversed prompts.
results.show_data()
