# from flask import Flask, render_template, request, jsonify
#
#
# from transformers import AutoModelForCausalLM, AutoTokenizer
# import torch
#
#
# tokenizer = AutoTokenizer.from_pretrained("microsoft/DialoGPT-medium")
# model = AutoModelForCausalLM.from_pretrained("microsoft/DialoGPT-medium")
#
#
# app = Flask(__name__)
#
# @app.route("/")
# def index():
#     return render_template('chat.html')
#
#
# @app.route("/get", methods=["GET", "POST"])
# def chat():
#     msg = request.form["msg"]
#     input = msg
#     return get_Chat_response(input)
#
#
# def get_Chat_response(text):
#
#     # Let's chat for 5 lines
#     for step in range(5):
#         # encode the new user input, add the eos_token and return a tensor in Pytorch
#         new_user_input_ids = tokenizer.encode(str(text) + tokenizer.eos_token, return_tensors='pt')
#
#         # append the new user input tokens to the chat history
#         bot_input_ids = torch.cat([chat_history_ids, new_user_input_ids], dim=-1) if step > 0 else new_user_input_ids
#
#         # generated a response while limiting the total chat history to 1000 tokens,
#         chat_history_ids = model.generate(bot_input_ids, max_length=1000, pad_token_id=tokenizer.eos_token_id)
#
#         # pretty print last ouput tokens from bot
#         return tokenizer.decode(chat_history_ids[:, bot_input_ids.shape[-1]:][0], skip_special_tokens=True)
#
#
# if __name__ == '__main__':
#     app.run()


from flask import Flask, request, jsonify, render_template
import spacy
import re

app = Flask(__name__)

# Load the spacy model
nlp = spacy.load("en_core_web_sm")

# Define predefined questions and answers
qa_pairs = {
    "what is the purpose of the bob eprocure solutions platform": "The BOB eProcure Solutions platform facilitates vendor bidding for procurement processes. It streamlines communication, document submission, and bid evaluation.",
    "how do i log in as a supplier": "Click on the ‘Login as Supplier’ button to start the process.",
    "how do i participate in an rfq": "First, click on un-participated RFQs, then view the RFQ details by clicking on 'Actions’. Accept the terms and conditions to proceed.",
    "how do i add documents to the repository": "Click on ‘Actions’, then ‘Add Documents’, and upload the necessary files by clicking on 'Start Upload’.",
    "what are the steps for final bid submission": "After uploading all required documents, click on ‘Proceed to Final Bid’, verify the final total price, agree to the terms, and click ‘Submit’.",
    "what should i do if i encounter technical issues during the bidding process": "If you face any technical difficulties, click on the ‘Help’ button or contact our support team at support@bobeProcure.com.",
    "can i withdraw my bid after submission": "Yes, you can withdraw your bid before the bid closing deadline. Go to ‘My Bids’, select the relevant bid, and choose the ‘Withdraw Bid’ option.",
    "how are bids evaluated": "Bids are evaluated based on criteria such as price, quality, delivery time, and compliance with specifications. The evaluation process is transparent and automated.",
    "when will i receive payment for a successful bid": "Payments are typically processed within 30 days after bid acceptance. Ensure your bank details are up-to-date in your profile.",
    "how can i seek clarifications regarding an rfq": "If you have any doubts or need clarifications, use the ‘Ask a Question’ feature within the RFQ. Our team will respond promptly.",
    "how do i verify the authenticity of uploaded documents": "The system automatically checks document validity based on predefined rules. If any discrepancies are found, you’ll receive notifications.",
    "can i submit multiple bids for the same rfq": "Yes, you can submit multiple bids. Each bid should be unique and comply with the RFQ requirements.",
    "where can i view my bid history": "Go to ‘My Bids’ to see your bid history, including submitted bids, withdrawn bids, and bid status updates."
}

# Define greetings and common responses
common_responses = {
    "hello": "Hello! How can I assist you today?",
    "hi": "Hi there! How can I help you?",
    "hey": "Hey! What can I do for you?",
    "thanks": "You're welcome! If you have any other questions, feel free to ask.",
    "thank you": "You're welcome! Glad to be of help.",
    "bye": "Goodbye! Have a great day!",
    "goodbye": "Goodbye! Take care!"
}

def preprocess_text(text):
    # Remove special characters and convert to lowercase
    text = re.sub(r'[^a-zA-Z0-9\s]', '', text)
    text = text.lower()
    return text

def get_response(msg):
    # Preprocess the input message
    processed_msg = preprocess_text(msg)

    # Check if the processed message is in the QA pairs or common responses
    if processed_msg in qa_pairs:
        return qa_pairs[processed_msg]
    elif processed_msg in common_responses:
        return common_responses[processed_msg]
    else:
        # Use spacy to find similar questions if the exact match is not found
        user_doc = nlp(processed_msg)
        best_match = None
        highest_similarity = 0

        for question in qa_pairs.keys():
            question_doc = nlp(question)
            similarity = user_doc.similarity(question_doc)
            if similarity > highest_similarity:
                highest_similarity = similarity
                best_match = question

        if highest_similarity > 0.7:  # Threshold for similarity
            return qa_pairs[best_match]
        else:
            return "Sorry, I don't understand that question."

@app.route("/")
def index():
    return render_template('chat.html')

@app.route('/get', methods=['POST'])
def chatbot_response():
    msg = request.form['msg']
    response = get_response(msg)
    return jsonify({'response': response})

if __name__ == "__main__":
    app.run(debug=True)
