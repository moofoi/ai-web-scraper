import streamlit as st
import requests
from bs4 import BeautifulSoup
import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel("gemini-2.5-flash")

def scrape_website(url):
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # ลบ script และ style ออก
        for tag in soup(['script', 'style', 'nav', 'footer']):
            tag.decompose()
        
        text = soup.get_text(separator=' ', strip=True)
        # จำกัดความยาวไม่เกิน 5000 ตัวอักษร
        return text[:5000]
    except Exception as e:
        return f"Error scraping: {str(e)}"

def summarize_with_ai(text, task):
    prompt = f"""
    Based on this website content:
    {text}
    
    Task: {task}
    
    Please provide a clear and structured response in the same language as the content.
    """
    response = model.generate_content(prompt)
    return response.text

# UI
st.title("🌐 AI Web Scraper & Summarizer")
st.write("Enter any URL and let AI analyze the content for you")

url = st.text_input("🔗 Website URL", placeholder="https://example.com")

task = st.selectbox("What do you want to do?", [
    "Summarize the main content",
    "Extract key points",
    "Find contact information",
    "Analyze products/services",
    "Custom task"
])

if task == "Custom task":
    task = st.text_input("Describe your task")

if st.button("🚀 Scrape & Analyze") and url:
    with st.spinner("Scraping website..."):
        content = scrape_website(url)
    
    if "Error" in content:
        st.error(content)
    else:
        st.success("✅ Website scraped successfully!")
        
        with st.expander("📄 Raw Content"):
            st.text(content[:1000] + "...")
        
        with st.spinner("AI is analyzing..."):
            result = summarize_with_ai(content, task)
        
        st.subheader("🤖 AI Analysis")
        st.write(result)