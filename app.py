
from flask import Flask, request, jsonify, render_template
import spacy
import re
from waitress import serve
import difflib


app = Flask(__name__)

# Load the spacy model
nlp = spacy.load("en_core_web_sm")

# Define predefined questions and answers
qa_pairs = {
    "what is the purpose of the bob eprocure solutions platform ?": "The BOB eProcure Solutions platform facilitates vendor bidding for procurement processes. It streamlines communication, document submission, and bid evaluation.",
    "how do i log in as a supplier ?": "Click on the ‘Login as Supplier’ button to start the process.",
    "how do i participate in an rfq ?": "First, click on un-participated RFQs, then view the RFQ details by clicking on 'Actions’. Accept the terms and conditions to proceed.",
    "how do i add documents to the repository ?": "Click on ‘Actions’, then ‘Add Documents’, and upload the necessary files by clicking on 'Start Upload’.",
    "what are the steps for final bid submission ?": "After uploading all required documents, click on ‘Proceed to Final Bid’, verify the final total price, agree to the terms, and click ‘Submit’.",
    "what should i do if i encounter technical issues during the bidding process ?": "If you face any technical difficulties, click on the ‘Help’ button or contact our support team at support@bobeProcure.com.",
    "can i withdraw my bid after submission ?": "Yes, you can withdraw your bid before the bid closing deadline. Go to ‘My Bids’, select the relevant bid, and choose the ‘Withdraw Bid’ option.",
    "how are bids evaluated ?": "Bids are evaluated based on criteria such as price, quality, delivery time, and compliance with specifications. The evaluation process is transparent and automated.",
    "when will i receive payment for a successful bid ?": "Payments are typically processed within 30 days after bid acceptance. Ensure your bank details are up-to-date in your profile.",
    "how can i seek clarifications regarding an rfq ?": "If you have any doubts or need clarifications, use the ‘Ask a Question’ feature within the RFQ. Our team will respond promptly.",
    "how do i verify the authenticity of uploaded documents ?": "The system automatically checks document validity based on predefined rules. If any discrepancies are found, you’ll receive notifications.",
    "can i submit multiple bids for the same rfq ?": "Yes, you can submit multiple bids. Each bid should be unique and comply with the RFQ requirements.",
    "where can i view my bid history ?": "Go to ‘My Bids’ to see your bid history, including submitted bids, withdrawn bids, and bid status updates."
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

def suggest_questions(user_keyword):
    keyword = user_keyword.lower()
    suggestions = [question for question in qa_pairs.keys() if keyword in question.lower()]
    return suggestions

def format_suggestions(suggestions):
    formatted_suggestions = []
    for suggestion in suggestions:
        parts = suggestion.split('?')
        formatted_suggestions.extend([part.strip() + '?' for part in parts if part.strip()])
    return formatted_suggestions

def get_response(msg):
    # Preprocess the input message
    processed_msg = preprocess_text(msg)

    # Check if the processed message is in the QA pairs or common responses
    if processed_msg in qa_pairs:
        return qa_pairs[processed_msg]
    elif processed_msg in common_responses:
        return common_responses[processed_msg]
    else:
        # Use spaCy to find similar questions if the exact match is not found
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
            suggestions = suggest_questions(processed_msg)
            if suggestions:
                formatted_suggestions = format_suggestions(suggestions)
                clickable_suggestions = ['<a href="#" onclick="sendMessage(\'{}\')">{}</a>'.format(sug, sug) for sug in formatted_suggestions]
                return "Did you mean:<br>" + "<br>".join(clickable_suggestions)
            else:
                return "Sorry, I don't have any suggestions related to that keyword."

def handle_user_click(clicked_suggestion):
    # Retrieve the answer corresponding to the clicked suggestion
    return qa_pairs.get(clicked_suggestion, "Sorry, I don't have an answer for that.")

# Assuming you have an event listener for when a suggestion is clicked
def handleSuggestionClick(clicked_suggestion):
    response = handle_user_click(clicked_suggestion)
    # Display the response to the user
    display_response(response)

# Sample function to display response, replace it with actual implementation based on your environment
def display_response(response):
    print(response)

@app.route("/")
def index():
    return render_template('chat.html')

@app.route('/get', methods=['POST'])
def chatbot_response():
    msg = request.form['msg']
    response = get_response(msg)
    return jsonify({'response': response})

@app.route('/handle_click', methods=['POST'])
def handle_click():
    clicked_suggestion = request.json['suggestion']
    response = handle_user_click(clicked_suggestion)
    return jsonify({'response': response})

if __name__ == "__main__":
    # app.run(debug=True)  // Comment this while deploymet
    # production command
    serve(app, host="0.0.0.0", port=5000)

