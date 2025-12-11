# Stack Overflow LLM-as-a-Judge

Using LLM's to judge information is popular these days, especially in areas of big data where it would be costly and impractical to have human evaluators. This has led many discoveries, mostly to the tune of 'they're not as good at judging as humans'; whether through positional, self-favouring, or other biases, as well as issues with it's 'reasoning'. This is probably to be expected, but nevertheless, there have been many attempts to reduce this gap in evaluation quality, and there are numerous ways people have sought to do this.

With this project, I will evaluate many of these methods, analysing their effect on the quality of an LLM's judging capabilities. 

In setting out to do this, I searched for some kind of database with already-evaluated data in it, which I could then compare to the LLM's evaluations. Of course this isn't always an easy thing to find, and this led me to think of Stack Overflow; a forum where questions are asked and answered by a community, and then ranked by their merit and relevance to the question asked. Due to this ranked nature, I realised this is a brilliant opportunity to test an LLM-as-a-judge system. My method is explained below.

### How To Run

Add your watsonx api key (or replace with other LLM provider).
Run stack_agent.py. This will query the LLM for all question IDs in the questionID array and populate a 'test_results.csv' file
Run graphing.py. This will display the data from the test results on a bar chart.

### Method

 - First, I selected questions from the site on various different topics, and grouped them as such.
 - I then extracted and formatted the question and the top 5 answers (if there were 5 answers available)
 - Here is where I tried two different approaches.
First, I tried giving the LLM the question and all 5 answers (identified by their author's user id), and asked it to give the answers a ranking, based on it's merit and relevance to the question. This would often return surprisingly accurate results when compared to the actual upvotes ranking on the site. I then tried giving it the answers in a reverse order (5-4-3-2-1), and saw a sharp drop off in accuracy. I soon realised that this original accuracy was due to a positional bias - the LLM would favour the earlier answers with higher scores, assuming they were better.

I then tried comparing the accuracy of the LLM when given a prompt which specified the answers were in **no particular order**, with its accuracy without.

My next step was to eliminate the positional bias completely, by making seperate calls to the LLM for each answer, passing in the question each time. This of course was slower and more token-intensive, but allowed me to evaluate the LLM's capabilities much more fairly.

I also wanted to test whether it would be better at answering questions which were asked before its training cut-off, which would tell me a) that it had been trained on stack overflow data, and b) that it could 'recall' this information to help it evaluate answers.