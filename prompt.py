import datetime
import json
import openai
from openai.embeddings_utils import distances_from_embeddings
import numpy as np
import pandas as pd
import csv

################################################################################
### Step 12
################################################################################

def create_context(
    question, max_len=1800, size="ada"
):
    """
    Create a context for a question by finding the most similar context from the dataframe
    """
    
    df=pd.read_csv('processed/embeddings.csv', index_col=0)
    df['embeddings'] = df['embeddings'].apply(eval).apply(np.array)

    df.head()

    # Get the embeddings for the question
    q_embeddings = openai.Embedding.create(input=question, engine='text-embedding-ada-002')['data'][0]['embedding']

    # Get the distances from the embeddings
    df['distances'] = distances_from_embeddings(q_embeddings, df['embeddings'].values, distance_metric='cosine')

    returns = []
    cur_len = 0

    # Sort by distance and add the text to the context until the context is too long
    for i, row in df.sort_values('distances', ascending=True).iterrows():
        
        # Add the length of the text to the current length
        cur_len += row['n_tokens'] + 4
        
        # If the context is too long, break
        if cur_len > max_len:
            break
        
        # Else add it to the text that is being returned
        returns.append(row["text"])

    # Return the context
    return "\n\n###\n\n".join(returns)

def answer_question(
    model="text-davinci-003",
    question="Am I allowed to publish model outputs to Twitter, without a human review?",
    max_len=1800,
    size="ada",
    debug=False,
    max_tokens=150,
    stop_sequence=None, 
    user_id="000"
):
    """
    Answer a question based on the most similar context from the dataframe texts
    """
    context = create_context(
        question,
        max_len=max_len,
        size=size,
    )
    # If debug, print the raw model response
    if debug:
        print("Context:\n" + context)
        print("Model: " + model)
        print("\n\n")

    if model == "text-davinci-003":

        try:
            # Create a completions using the questin and context
            response = openai.Completion.create(
                prompt=f"Act like you were a customer service assitant at a company called Apizee. If the question the user is asking can't be answered based on the context, ask a question to clarify the question or provide a list of possible topics for the user to choose and orientate your answer. If you give a reference to a webpage or website, provide the exact url in the form of a <a> tag. If you really struggle with the answer or the user ask for an escalation to a real person just anser \"#ESCALATION#\"\n\nContext: {context}\n\n---\n\nQuestion: {question}\nAnswer:",
                temperature=0.3,
                max_tokens=max_tokens,
                top_p=1,
                frequency_penalty=0,
                presence_penalty=0,
                stop=stop_sequence,
                model=model,
            )
            return response["choices"][0]["text"].strip()
        except Exception as e:
            print(e)
            return ""
    elif model == "gpt-3.5-turbo":

        userMessageFilePath = './messages/'+user_id+'.txt'

        try:
            messages=[
                {"role": "system", "content": f"Act like you were a customer service assitant at a company called Apizee operating a video communication platform calle ApiRTC. If the question the user is asking can't be answered based on the context, ask a question to clarify the question or provide a list of possible topics for the user to choose and orientate your answer. When answering some code, encapsulate it into a <code> tag. If you give a reference to a webpage or website, provide the exact url in the form of a <a> tag. If you really struggle with the answer or the user ask for an escalation to speak to a non-AI person, say goodbye and add the following keyword \"#ESCALATION#\"  \n\n"}
            ]


            # TODO: get only the most relevant messages from file

            try:
                #Retrieve past conversation with the user
                with open(userMessageFilePath, encoding='UTF8') as f:
                    csv_reader = csv.reader(f)

                    for line in csv_reader:
                        print({"role : " + line[2] +  " - content : " + line[3]})
                        messages.append({"role": line[2], "content": line[3]})
            except FileNotFoundError as e:
                with open(userMessageFilePath, 'w', encoding='UTF8') as f:
                    print("New user file " + userMessageFilePath)


            # Insert context 
            messages.append({"role":"system", "content": "Context: " + context})

             # Insert user question 
            messages.append({"role":"user", "content" : "Question: " + question})
            print("####MESSAGES####\n\n")
            print(json.dumps(messages))
            print("####END OF MESSAGES####\n\n")

            # Create a completions using the questin and context
            response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=messages, 
            temperature= 0.1
            )

            print(json.dumps(response["choices"]))

            answer =  response["choices"][0]["message"]

            # open the file in the write mode
            with open('messages/'+user_id+'.txt', 'a', encoding="UTF8") as f:
                # create the csv writer
                writer = csv.writer(f)

                rows = [[datetime.datetime.now().timestamp(), user_id, "user", question], 
                        [datetime.datetime.now().timestamp(), user_id, "assistant", answer.content]]

                # write a row to the csv file
                writer.writerows(rows)

            return answer
        
        except Exception as e:
            print(e)
            return ""

