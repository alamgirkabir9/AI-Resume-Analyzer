import os
import json
import time
import re
from pathlib import Path
from typing import Optional
import pandas as pd
import fitz  # PyMuPDF
import yagmail
from flask import Flask, render_template, request, jsonify, send_file, flash, redirect, url_for, session
from werkzeug.utils import secure_filename
from dotenv import load_dotenv
from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq
from langchain_core.messages import AIMessage
import zipfile
import tempfile
import shutil

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'your-secret-key-here')
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB max file size
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['RESULTS_FOLDER'] = 'results'

# Create necessary directories
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['RESULTS_FOLDER'], exist_ok=True)

# LangChain prompt template
prompt_template = ChatPromptTemplate.from_messages([
    ("system", "You are a resume analysis expert. You will compare the Resume and Job Description and provide the output ONLY in valid JSON format. Do not include any explanatory text before or after the JSON."),
    ("human", "Analyze the resume against the job description: \n \
     Resume: {resume} \n \
     Job Description: {Job_description} \n \
     Provide a JSON response with these exact keys: Name, email, is_perfect, is_okay, Matching Score in percentage, strong zone, Lack of Knowledge. \
     Make sure the response is valid JSON format only, no additional text.")
])

def load_pdf(pdf_file_path):
    """Extract text from PDF"""
    try:
        pdf_document = fitz.open(pdf_file_path)
        pdf_text_with_links = ""

        for page_num in range(pdf_document.page_count):
            page = pdf_document.load_page(page_num)
            pdf_text_with_links += page.get_text("text")

            links = page.get_links()
            for link in links:
                if 'uri' in link:
                    pdf_text_with_links += f"\n(Link: {link['uri']})"
        
        pdf_document.close()
        return pdf_text_with_links
    except Exception as e:
        print(f"Error loading PDF {pdf_file_path}: {str(e)}")
        return ""

def parser(aimessage: AIMessage) -> str:
    return aimessage.content

def extract_json_from_response(response_text):
    """Extract JSON from LLM response, handling various formats"""
    def normalize_json_keys(data):
        """Normalize JSON keys to expected format"""
        if not isinstance(data, dict):
            return data
        
        normalized = {}
        key_mapping = {
            'name': 'Name',
            'email': 'email',
            'is_perfect': 'is_perfect',
            'is_okay': 'is_okay',
            'matching_score': 'Matching Score in percentage',
            'matching score': 'Matching Score in percentage',
            'matching_score_percentage': 'Matching Score in percentage',
            'score': 'Matching Score in percentage',
            'strong_zone': 'strong zone',
            'strengths': 'strong zone',
            'lack_of_knowledge': 'Lack of Knowledge',
            'weaknesses': 'Lack of Knowledge',
            'gaps': 'Lack of Knowledge'
        }
        
        for key, value in data.items():
            key_lower = key.lower().replace(' ', '_').replace('-', '_')
            
            if key_lower in key_mapping:
                normalized[key_mapping[key_lower]] = value
            else:
                if 'score' in key_lower and 'percentage' in key_lower:
                    normalized['Matching Score in percentage'] = value
                elif 'score' in key_lower:
                    normalized['Matching Score in percentage'] = value
                else:
                    normalized[key] = value
        
        # Ensure all required keys exist
        default_values = {
            "Name": "Unknown",
            "email": "unknown@email.com", 
            "is_perfect": False,
            "is_okay": False,
            "Matching Score in percentage": "0%",
            "strong zone": "Not specified",
            "Lack of Knowledge": "Not specified"
        }
        
        for req_key, default_val in default_values.items():
            if req_key not in normalized:
                normalized[req_key] = default_val
        
        return normalized
    
    try:
        data = json.loads(response_text)
        return normalize_json_keys(data)
    except json.JSONDecodeError:
        try:
            cleaned = response_text.replace('```json', '').replace('```', '').strip()
            data = json.loads(cleaned)
            return normalize_json_keys(data)
        except json.JSONDecodeError:
            try:
                json_match = re.search(r'\{.*\}', cleaned, re.DOTALL)
                if json_match:
                    data = json.loads(json_match.group())
                    return normalize_json_keys(data)
                else:
                    return normalize_json_keys({})
            except:
                return normalize_json_keys({})

def resume_checker(resume, job_description, llm):
    """Generate resume analysis using LangChain"""
    Chain = prompt_template | llm | parser
    result = Chain.invoke({"resume": resume, "Job_description": job_description})
    return result

def send_mail(data_path, sender_email, sender_password):
    """Send email notifications"""
    try:
        csv_data = pd.read_csv(data_path)
        yag = yagmail.SMTP(sender_email, sender_password)
        
        # Find the score column dynamically
        score_column = None
        possible_score_columns = [
            'Matching Score in percentage', 
            'Matching Score', 
            'Score', 
            'matching_score', 
            'score'
        ]
        
        for col in possible_score_columns:
            if col in csv_data.columns:
                score_column = col
                break
        
        if not score_column:
            for col in csv_data.columns:
                if 'score' in col.lower():
                    score_column = col
                    break
        
        if not score_column:
            return False, "No score column found in the data"
        
        success_count = 0
        total_count = len(csv_data)
        
        for i in range(csv_data.shape[0]):
            data = csv_data.iloc[i]
            name = data.get('Name', 'Unknown')
            email = data.get('email', 'unknown@email.com')
            score_val = data.get(score_column, '0%')
            
            # Parse score
            try:
                if "%" in str(score_val):
                    score = int(str(score_val).replace("%", ""))
                else:
                    score = int(float(score_val))
            except (ValueError, TypeError):
                score = 0
            
            weak_zone = data.get('Lack of Knowledge', 'Not specified')

            if score < 70:
                message = f"""Hello {name},

Thank you for your application for the Machine Learning position in our company. Unfortunately, we cannot consider you for the further process. We found some areas that don't match with our requirements:

{weak_zone}

You can upgrade yourself and try later.

Best Regards,
HR Team"""
            else:
                message = f"""Hello {name},

Thank you for your application for the Machine Learning position in our company. We are pleased to consider you for the further process.

Best Regards,
HR Team"""
            
            try:
                yag.send(email, 'Response to Your ML Engineer Application', message)
                success_count += 1
            except Exception as e:
                print(f"Failed to send email to {email}: {str(e)}")
        
        return True, f"Successfully sent {success_count}/{total_count} emails"
    
    except Exception as e:
        return False, f"Error sending emails: {str(e)}"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_files():
    try:
        # Get form data
        job_description = request.form.get('job_description', '').strip()
        api_key = request.form.get('api_key', '').strip()
        model_option = request.form.get('model_option', 'llama3-70b-8192')
        temperature = float(request.form.get('temperature', 0.0))
        
        if not job_description:
            return jsonify({'error': 'Please enter a job description'}), 400
        
        if not api_key:
            return jsonify({'error': 'Please enter your LLAMA API key'}), 400
        
        # Handle file uploads
        uploaded_files = request.files.getlist('pdf_files')
        
        if not uploaded_files or all(file.filename == '' for file in uploaded_files):
            return jsonify({'error': 'Please select PDF files to upload'}), 400
        
        # Initialize LLM
        try:
            llm = ChatGroq(
                model=model_option,
                api_key=api_key,
                temperature=temperature
            )
        except Exception as e:
            return jsonify({'error': f'Error initializing LLM: {str(e)}'}), 400
        
        # Process uploaded files
        pdf_files = []
        upload_session_dir = os.path.join(app.config['UPLOAD_FOLDER'], str(int(time.time())))
        os.makedirs(upload_session_dir, exist_ok=True)
        
        for file in uploaded_files:
            if file and file.filename.lower().endswith('.pdf'):
                filename = secure_filename(file.filename)
                file_path = os.path.join(upload_session_dir, filename)
                file.save(file_path)
                pdf_files.append((filename, file_path))
        
        if not pdf_files:
            return jsonify({'error': 'No valid PDF files found'}), 400
        
        # Process resumes
        information_list = []
        
        for idx, (filename, file_path) in enumerate(pdf_files):
            try:
                resume_text = load_pdf(file_path)
                
                if not resume_text.strip():
                    information_list.append({
                        "Name": f"Error: {filename}",
                        "email": "error@email.com", 
                        "is_perfect": False,
                        "is_okay": False,
                        "Matching Score in percentage": "0%",
                        "strong zone": "Could not extract text",
                        "Lack of Knowledge": "PDF text extraction failed"
                    })
                    continue
                
                # Analysis
                checker = resume_checker(resume=resume_text, job_description=job_description, llm=llm)
                data = extract_json_from_response(checker)
                information_list.append(data)
                
                # Rate limiting
                time.sleep(1)
                
            except Exception as e:
                information_list.append({
                    "Name": f"Error: {filename}",
                    "email": "error@email.com", 
                    "is_perfect": False,
                    "is_okay": False,
                    "Matching Score in percentage": "0%",
                    "strong zone": "Processing failed",
                    "Lack of Knowledge": f"Error: {str(e)}"
                })
        
        # Save results
        if information_list:
            df = pd.DataFrame(information_list)
            results_file = os.path.join(app.config['RESULTS_FOLDER'], f'results_{int(time.time())}.csv')
            df.to_csv(results_file, index=False)
            
            # Store results file path in session
            session['latest_results'] = results_file
            
            # Clean up uploaded files
            shutil.rmtree(upload_session_dir, ignore_errors=True)
            
            return jsonify({
                'success': True,
                'message': f'Successfully processed {len(pdf_files)} resume(s)',
                'results': information_list,
                'results_file': results_file
            })
        else:
            return jsonify({'error': 'No resumes were successfully processed'}), 400
    
    except Exception as e:
        return jsonify({'error': f'An error occurred: {str(e)}'}), 500

@app.route('/download_results')
def download_results():
    try:
        results_file = session.get('latest_results')
        if not results_file or not os.path.exists(results_file):
            flash('No results file found. Please run analysis first.', 'error')
            return redirect(url_for('index'))
        
        return send_file(results_file, as_attachment=True, download_name='resume_analysis_results.csv')
    
    except Exception as e:
        flash(f'Error downloading results: {str(e)}', 'error')
        return redirect(url_for('index'))

@app.route('/send_emails', methods=['POST'])
def send_emails():
    try:
        # Get email configuration
        sender_email = request.form.get('sender_email', '').strip()
        sender_password = request.form.get('sender_password', '').strip()
        
        if not sender_email or not sender_password:
            return jsonify({'error': 'Please provide sender email and password'}), 400
        
        # Get results file
        results_file = session.get('latest_results')
        if not results_file or not os.path.exists(results_file):
            return jsonify({'error': 'No results file found. Please run analysis first.'}), 400
        
        # Send emails
        success, message = send_mail(results_file, sender_email, sender_password)
        
        if success:
            return jsonify({'success': True, 'message': message})
        else:
            return jsonify({'error': message}), 400
    
    except Exception as e:
        return jsonify({'error': f'An error occurred: {str(e)}'}), 500

@app.route('/results')
def view_results():
    try:
        results_file = session.get('latest_results')
        if not results_file or not os.path.exists(results_file):
            flash('No results found. Please run analysis first.', 'warning')
            return redirect(url_for('index'))
        
        # Load and process results
        df = pd.read_csv(results_file)
        
        # Calculate statistics
        total_resumes = len(df)
        perfect_candidates = 0
        okay_candidates = 0
        
        if 'is_perfect' in df.columns:
            perfect_candidates = len(df[df['is_perfect'].isin([True, 'True', 'true', 'TRUE', 1, '1'])])
        
        if 'is_okay' in df.columns:
            okay_candidates = len(df[df['is_okay'].isin([True, 'True', 'true', 'TRUE', 1, '1'])])
        
        # Calculate average score
        avg_score = 0
        score_column = 'Matching Score in percentage'
        
        if score_column in df.columns:
            scores = []
            for score in df[score_column]:
                try:
                    if isinstance(score, str):
                        clean_score = score.replace('%', '').strip()
                        scores.append(int(float(clean_score)))
                    elif isinstance(score, (int, float)):
                        scores.append(int(score))
                    else:
                        scores.append(0)
                except (ValueError, TypeError):
                    scores.append(0)
            avg_score = sum(scores) / len(scores) if scores else 0
        
        # Sort by score for better display
        if score_column in df.columns:
            df_display = df.copy()
            df_display['numeric_score'] = 0
            
            for idx, score in enumerate(df[score_column]):
                try:
                    if isinstance(score, str):
                        clean_score = score.replace('%', '').strip()
                        df_display.iloc[idx, df_display.columns.get_loc('numeric_score')] = int(float(clean_score))
                    elif isinstance(score, (int, float)):
                        df_display.iloc[idx, df_display.columns.get_loc('numeric_score')] = int(score)
                except (ValueError, TypeError):
                    df_display.iloc[idx, df_display.columns.get_loc('numeric_score')] = 0
            
            df_sorted = df_display.sort_values('numeric_score', ascending=False)
            df_sorted = df_sorted.drop('numeric_score', axis=1)
        else:
            df_sorted = df
        
        results_data = df_sorted.to_dict('records')
        
        return render_template('results.html',
                             results=results_data,
                             total_resumes=total_resumes,
                             perfect_candidates=perfect_candidates,
                             okay_candidates=okay_candidates,
                             avg_score=round(avg_score, 1))
    
    except Exception as e:
        flash(f'Error loading results: {str(e)}', 'error')
        return redirect(url_for('index'))

@app.errorhandler(413)
def too_large(e):
    return jsonify({'error': 'File too large. Maximum size is 50MB.'}), 413

@app.errorhandler(404)
def not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(e):
    return render_template('500.html'), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))