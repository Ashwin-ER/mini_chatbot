
from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import os
from datetime import datetime
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

app = Flask(__name__)
CORS(app)

# Global variables for the model and knowledge base
model = None
knowledge_base = None
knowledge_embeddings = None

def load_model():
    """Load the sentence transformer model"""
    global model
    print("Loading sentence transformer model...")
    model = SentenceTransformer('all-MiniLM-L6-v2')
    print("Model loaded successfully!")

def load_knowledge_base():
    """Load the knowledge base and compute embeddings"""
    global knowledge_base, knowledge_embeddings, model
    
    # Professional Q&A knowledge base
    knowledge_base = [
        {
            "question": "How do I prioritize tasks effectively?",
            "answer": "Use the Eisenhower Matrix: categorize tasks by urgency and importance. Focus on important-urgent tasks first, schedule important-not urgent tasks, delegate urgent-not important tasks, and eliminate neither urgent nor important tasks."
        },
        {
            "question": "What are the best practices for remote work productivity?",
            "answer": "Set up a dedicated workspace, maintain regular hours, take frequent breaks, communicate clearly with your team, use productivity tools like task managers, and establish boundaries between work and personal life."
        },
        {
            "question": "How do I manage time better during busy periods?",
            "answer": "Use time-blocking to schedule focused work sessions, batch similar tasks together, minimize multitasking, set realistic deadlines, and regularly review and adjust your schedule based on what works best."
        },
        {
            "question": "What should I consider when seeking startup funding?",
            "answer": "Prepare a solid business plan, know your market and competition, have clear financial projections, build a strong team, create a minimum viable product, and research different funding options like angel investors, VCs, or crowdfunding."
        },
        {
            "question": "How do I handle work-life balance?",
            "answer": "Set clear boundaries between work and personal time, learn to say no to non-essential commitments, prioritize self-care and health, communicate your limits to colleagues, and regularly assess and adjust your workload."
        },
        {
            "question": "What are effective communication strategies in the workplace?",
            "answer": "Practice active listening, be clear and concise in your messaging, choose the right communication channel for each situation, provide regular updates on projects, and ask clarifying questions when needed."
        },
        {
            "question": "How do I stay motivated during challenging projects?",
            "answer": "Break large projects into smaller milestones, celebrate small wins, maintain a growth mindset, seek feedback and support from colleagues, and remind yourself of the project's purpose and impact."
        },
        {
            "question": "What skills should I develop for career advancement?",
            "answer": "Focus on both technical skills relevant to your field and soft skills like leadership, communication, problem-solving, and adaptability. Stay updated with industry trends and consider pursuing relevant certifications."
        },
        {
            "question": "How do I build a professional network effectively?",
            "answer": "Attend industry events and conferences, engage on professional social media platforms, offer help and value to others, maintain existing relationships, and follow up consistently with new connections."
        },
        {
            "question": "What are the key elements of a successful presentation?",
            "answer": "Know your audience and tailor your content accordingly, have a clear structure with opening, body, and conclusion, use visual aids effectively, practice your delivery, engage with your audience, and prepare for questions."
        }
    ]
    
    # Compute embeddings for all questions
    questions = [item["question"] for item in knowledge_base]
    print("Computing embeddings for knowledge base...")
    knowledge_embeddings = model.encode(questions)
    print("Knowledge base loaded and embeddings computed!")

def find_best_answer(user_question):
    """Find the best matching answer from the knowledge base"""
    global model, knowledge_base, knowledge_embeddings
    
    # Encode the user question
    user_embedding = model.encode([user_question])
    
    # Compute similarities
    similarities = cosine_similarity(user_embedding, knowledge_embeddings)[0]
    
    # Find the best match
    best_match_idx = np.argmax(similarities)
    confidence = similarities[best_match_idx]
    
    # Return the answer if confidence is above threshold
    if confidence > 0.3:  # Adjust threshold as needed
        return knowledge_base[best_match_idx]["answer"], confidence
    else:
        return "I'm sorry, I don't have information about that specific topic. Could you try rephrasing your question or ask about productivity, remote work, task prioritization, startup funding, or professional development?", 0.0

def save_chat_history(question, answer):
    """Save chat history to local JSON file"""
    history_file = "data/chat_history.json"
    
    # Create data directory if it doesn't exist
    os.makedirs("data", exist_ok=True)
    
    # Load existing history
    if os.path.exists(history_file):
        with open(history_file, 'r', encoding='utf-8') as f:
            history = json.load(f)
    else:
        history = []
    
    # Add new entry
    new_entry = {
        "timestamp": datetime.now().isoformat(),
        "question": question,
        "answer": answer
    }
    
    history.append(new_entry)
    
    # Keep only last 50 entries to prevent file from growing too large
    history = history[-50:]
    
    # Save updated history
    with open(history_file, 'w', encoding='utf-8') as f:
        json.dump(history, f, indent=2, ensure_ascii=False)

@app.route('/ask', methods=['POST'])
def ask_question():
    """API endpoint to handle user questions"""
    try:
        data = request.get_json()
        
        if not data or 'question' not in data:
            return jsonify({
                'error': 'Question is required',
                'answer': '',
                'confidence': 0.0
            }), 400
        
        user_question = data['question'].strip()
        
        if not user_question:
            return jsonify({
                'error': 'Question cannot be empty',
                'answer': '',
                'confidence': 0.0
            }), 400
        
        # Find the best answer
        answer, confidence = find_best_answer(user_question)
        
        # Save to chat history
        save_chat_history(user_question, answer)
        
        # Return response
        response = {
            'question': user_question,
            'answer': answer,
            'confidence': float(confidence),
            'timestamp': datetime.now().isoformat()
        }
        
        return jsonify(response)
    
    except Exception as e:
        print(f"Error processing request: {str(e)}")
        return jsonify({
            'error': 'Internal server error',
            'answer': 'Sorry, there was an error processing your question. Please try again.',
            'confidence': 0.0
        }), 500

@app.route('/history', methods=['GET'])
def get_chat_history():
    """API endpoint to get recent chat history"""
    try:
        history_file = "data/chat_history.json"
        
        if os.path.exists(history_file):
            with open(history_file, 'r', encoding='utf-8') as f:
                history = json.load(f)
            
            # Return last 10 entries
            recent_history = history[-10:] if len(history) > 10 else history
            return jsonify({'history': recent_history})
        else:
            return jsonify({'history': []})
    
    except Exception as e:
        print(f"Error getting chat history: {str(e)}")
        return jsonify({'error': 'Error retrieving chat history', 'history': []})

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'model_loaded': model is not None,
        'knowledge_base_loaded': knowledge_base is not None
    })

if __name__ == '__main__':
    print("Starting AI Chatbot Backend...")
    
    # Load model and knowledge base on startup
    load_model()
    load_knowledge_base()
    
    print("Backend ready! Starting server...")
    app.run(debug=True, host='0.0.0.0', port=5000)