import numpy as np
from typing import Dict, List, Optional
import torch
from transformers import AutoTokenizer, AutoModel
from sklearn.manifold import TSNE
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import smtplib
import PyPDF2
import os

class JobMatchingService:
    def __init__(self):
        # Initialize models and tokenizers
        self.tokenizer = AutoTokenizer.from_pretrained("sentence-transformers/all-mpnet-base-v2")
        self.model = AutoModel.from_pretrained("sentence-transformers/all-mpnet-base-v2")
        
        # Initialize storage
        self.job_seeker_vectors = {}
        self.job_opening_vectors = {}
        self.email_config = {
            "smtp_server": os.getenv("SMTP_SERVER"),
            "smtp_port": int(os.getenv("SMTP_PORT")),
            "sender_email": os.getenv("SENDER_EMAIL"),
            "sender_password": os.getenv("SENDER_PASSWORD")
        }

    def extract_text_from_pdf(self, pdf_path: str) -> str:
        with open(pdf_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            text = ""
            for page in reader.pages:
                text += page.extract_text()
        return text

    def create_embeddings(self, text: str) -> np.ndarray:
        # Tokenize and create embeddings
        inputs = self.tokenizer(text, return_tensors="pt", truncation=True, max_length=512, padding=True)
        with torch.no_grad():
            outputs = self.model(**inputs)
        
        # Use mean pooling
        embeddings = outputs.last_hidden_state.mean(dim=1).numpy()
        return embeddings[0]

    def process_job_seeker(self, profile_info: Dict):
        # Extract text from documents
        resume_text = self.extract_text_from_pdf(profile_info["resume_path"])
        
        cover_letter_text = ""
        if "cover_letter_path" in profile_info:
            cover_letter_text = self.extract_text_from_pdf(profile_info["cover_letter_path"])
        
        certificate_texts = []
        if "certificate_paths" in profile_info:
            for cert_path in profile_info["certificate_paths"]:
                cert_text = self.extract_text_from_pdf(cert_path)
                certificate_texts.append(cert_text)

        # Create separate embeddings for different aspects
        experience_embedding = self.create_embeddings(resume_text)
        development_embedding = self.create_embeddings(cover_letter_text)
        personality_embedding = self.create_embeddings(" ".join(certificate_texts))

        # Store vectors with metadata
        self.job_seeker_vectors[profile_info["id"]] = {
            "experience": experience_embedding,
            "development": development_embedding,
            "personality": personality_embedding,
            "email": profile_info["email"]
        }

    def process_job_opening(self, job_info: Dict):
        # Create separate embeddings for different aspects
        requirements_embedding = self.create_embeddings(job_info["job_description"])
        growth_embedding = self.create_embeddings(job_info["growth_opportunities"])
        team_embedding = self.create_embeddings(f"{job_info['company_values']} {job_info['team_structure']}")

        # Store vectors with metadata
        self.job_opening_vectors[job_info["id"]] = {
            "requirements": requirements_embedding,
            "growth": growth_embedding,
            "team": team_embedding,
            "email": job_info["creator_email"],
            "title": job_info["job_title"],
            "company": job_info["company_name"]
        }

    def calculate_similarity(self, vec1: np.ndarray, vec2: np.ndarray) -> float:
        return float(np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2)))

    def get_matches(self, entity_id: str, entity_type: str, threshold: float = 0.7):
        matches = []
        
        if entity_type == "seeker":
            seeker_data = self.job_seeker_vectors[entity_id]
            for job_id, job_data in self.job_opening_vectors.items():
                similarity_scores = {
                    "experience": self.calculate_similarity(seeker_data["experience"], job_data["requirements"]),
                    "development": self.calculate_similarity(seeker_data["development"], job_data["growth"]),
                    "personality": self.calculate_similarity(seeker_data["personality"], job_data["team"])
                }
                
                average_score = sum(similarity_scores.values()) / len(similarity_scores)
                if average_score >= threshold:
                    matches.append({
                        "job_id": job_id,
                        "company": job_data["company"],
                        "title": job_data["title"],
                        "scores": similarity_scores,
                        "average_score": average_score
                    })
                    self.send_match_notification(seeker_data["email"], job_data["email"], 
                                              similarity_scores, average_score, entity_type)
        
        else:  # entity_type == "job"
            job_data = self.job_opening_vectors[entity_id]
            for seeker_id, seeker_data in self.job_seeker_vectors.items():
                similarity_scores = {
                    "experience": self.calculate_similarity(seeker_data["experience"], job_data["requirements"]),
                    "development": self.calculate_similarity(seeker_data["development"], job_data["growth"]),
                    "personality": self.calculate_similarity(seeker_data["personality"], job_data["team"])
                }
                
                average_score = sum(similarity_scores.values()) / len(similarity_scores)
                if average_score >= threshold:
                    matches.append({
                        "seeker_id": seeker_id,
                        "scores": similarity_scores,
                        "average_score": average_score
                    })
                    self.send_match_notification(job_data["email"], seeker_data["email"], 
                                              similarity_scores, average_score, entity_type)

        # Generate visualization if matches exist
        if matches:
            self.generate_visualization(entity_id, matches)

        return matches

    def generate_visualization(self, entity_id: str, matches: List[Dict]) -> str:
        # Prepare data for t-SNE
        vectors = []
        labels = []
        
        # Add entity vector
        if entity_id in self.job_seeker_vectors:
            main_vector = np.concatenate([
                self.job_seeker_vectors[entity_id]["experience"],
                self.job_seeker_vectors[entity_id]["development"],
                self.job_seeker_vectors[entity_id]["personality"]
            ])
            vectors.append(main_vector)
            labels.append("Main Profile")
        else:
            main_vector = np.concatenate([
                self.job_opening_vectors[entity_id]["requirements"],
                self.job_opening_vectors[entity_id]["growth"],
                self.job_opening_vectors[entity_id]["team"]
            ])
            vectors.append(main_vector)
            labels.append("Main Job")

        # Add match vectors
        for match in matches:
            if "job_id" in match:
                match_vector = np.concatenate([
                    self.job_opening_vectors[match["job_id"]]["requirements"],
                    self.job_opening_vectors[match["job_id"]]["growth"],
                    self.job_opening_vectors[match["job_id"]]["team"]
                ])
                vectors.append(match_vector)
                labels.append(f"Job: {match['title']}")
            else:
                match_vector = np.concatenate([
                    self.job_seeker_vectors[match["seeker_id"]]["experience"],
                    self.job_seeker_vectors[match["seeker_id"]]["development"],
                    self.job_seeker_vectors[match["seeker_id"]]["personality"]
                ])
                vectors.append(match_vector)
                labels.append(f"Profile {match['seeker_id'][:8]}")

        # Perform t-SNE
        tsne = TSNE(n_components=2, random_state=42)
        embeddings_2d = tsne.fit_transform(vectors)

        # Create visualization
        plt.figure(figsize=(12, 8))
        scatter = plt.scatter(embeddings_2d[:, 0], embeddings_2d[:, 1], c=range(len(vectors)), 
                            cmap='viridis', s=100)
        
        # Add labels
        for i, label in enumerate(labels):
            plt.annotate(label, (embeddings_2d[i, 0], embeddings_2d[i, 1]))

        plt.title("Profile-Job Similarity Visualization")
        plt.colorbar(scatter, label="Match Score")

        # Save visualization
        viz_path = f"visualizations/{entity_id}_matches.png"
        os.makedirs("visualizations", exist_ok=True)
        plt.savefig(viz_path)
        plt.close()

        return viz_path

    def send_match_notification(self, recipient1_email: str, recipient2_email: str, 
                          similarity_scores: Dict[str, float], average_score: float, 
                          entity_type: str):
        def create_email_body(scores: Dict[str, float], avg_score: float, is_job_seeker: bool) -> str:
            if is_job_seeker:
                template = """
                <h2>We found a promising job match!</h2>
                <p>Based on our analysis, we found a job that matches your profile with an overall score of {:.1%}</p>
                <h3>Match Breakdown:</h3>
                <ul>
                    <li>Experience Match: {:.1%}</li>
                    <li>Career Development Match: {:.1%}</li>
                    <li>Team/Culture Fit: {:.1%}</li>
                </ul>
                """
            else:
                template = """
                <h2>We found a promising candidate!</h2>
                <p>Based on our analysis, we found a candidate that matches your job opening with an overall score of {:.1%}</p>
                <h3>Match Breakdown:</h3>
                <ul>
                    <li>Experience Match: {:.1%}</li>
                    <li>Career Development Match: {:.1%}</li>
                    <li>Team/Culture Fit: {:.1%}</li>
                </ul>
                """
            return template.format(
                avg_score,
                scores["experience"],
                scores["development"],
                scores["personality"]
            )

        try:
            # Create message for job seeker
            msg_seeker = MIMEMultipart()
            msg_seeker["From"] = self.email_config["sender_email"]
            msg_seeker["To"] = recipient1_email
            msg_seeker["Subject"] = "New Job Match Found!" if entity_type == "seeker" else "Your Profile Matched a Job!"
            
            seeker_body = create_email_body(similarity_scores, average_score, True)
            msg_seeker.attach(MIMEText(seeker_body, "html"))

            # Create message for employer
            msg_employer = MIMEMultipart()
            msg_employer["From"] = self.email_config["sender_email"]
            msg_employer["To"] = recipient2_email
            msg_employer["Subject"] = "New Candidate Match Found!" if entity_type == "job" else "Your Job Matched a Candidate!"
            
            employer_body = create_email_body(similarity_scores, average_score, False)
            msg_employer.attach(MIMEText(employer_body, "html"))

            # Send emails
            with smtplib.SMTP(self.email_config["smtp_server"], self.email_config["smtp_port"]) as server:
                server.starttls()
                server.login(self.email_config["sender_email"], self.email_config["sender_password"])
                
                # Send to both recipients
                server.send_message(msg_seeker)
                server.send_message(msg_employer)

        except Exception as e:
            print(f"Error sending match notification emails: {str(e)}")
            # You might want to log this error or handle it differently in a production environment
            # For example, you could add it to a queue for retry or notify an admin
            raise Exception(f"Failed to send match notification: {str(e)}")