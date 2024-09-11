import openai
import requests
import os

# Set your OpenAI API key


def split_text(text, max_length=1024):
    # Split text into chunks of max_length tokens
    words = text.split()
    chunks = []
    chunk = []
    length = 0
    for word in words:
        length += len(word) + 1  # +1 for the space
        if length > max_length:
            chunks.append(' '.join(chunk))
            chunk = [word]
            length = len(word) + 1
        else:
            chunk.append(word)
    chunks.append(' '.join(chunk))
    return chunks

def translate_text_chunk(text, target_language):
    # Define the prompt for translation
    prompt = f"Translate the following text to {target_language}:\n\n{text}"
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": prompt},
        ],
        max_tokens=1024,
        n=1,
        stop=None,
        temperature=0.7,
    )

    summary = response.choices[0].message["content"].strip()
    print(summary)
    return summary

def translate_text(text, target_language):
    # Split text into chunks
    chunks = split_text(text)
    
    # Translate each chunk and combine results
    translated_chunks = [translate_text_chunk(chunk, target_language) for chunk in chunks]
    translated_text = ' '.join(translated_chunks)
    return translated_text

def generate_audio_from_text(text, api_key, voice_id):
    # Define the API endpoint for Eleven Labs
    api_url = f"https://api.elevenlabs.io/v1/text-to-speech"
    
    headers = {
        "xi-api-key": api_key,  # Use 'xi-api-key' instead of 'Authorization'
        "Content-Type": "application/json"
    }
    
    payload = {
        "text": text,
        "voice_id": voice_id
    }
    
    # Debugging output
    print(f"URL: {api_url}")
    print(f"Headers: {headers}")
    print(f"Payload: {payload}")

    response = requests.post(api_url, json=payload, headers=headers)
    
    if response.status_code == 200:
        audio = response.content
        return audio
    else:
        print(f"Response Status Code: {response.status_code}")
        print(f"Response Text: {response.text}")
        raise Exception(f"Error: {response.status_code}, {response.text}")

def save_audio_to_file(audio, file_path):
    # Define the directory for saving the MP3
    dir_path = os.path.dirname(file_path)
    os.makedirs(dir_path, exist_ok=True)
    
    # Save the audio file
    with open(file_path, "wb") as f:
        f.write(audio)
    
    print(f"Audio saved to {file_path}")

def translate_and_generate_audio(input_text, target_language):
    # Translate the input text to the specified language
    translated_text = translate_text(input_text, target_language)
    print(f"Translated Text: {translated_text}")
    
    # API key and voice ID for Eleven Labs
    elevenlabs_api_key = "sk_5ead7f3db2b9c5586db4502d96a880756e295a30ce688f76"
    elevenlabs_voice_id = "1IVWxPHWEi1qouA3cAop"
    
    # Generate audio from the translated text
    audio = generate_audio_from_text(translated_text, elevenlabs_api_key, elevenlabs_voice_id)
    
    # Save the audio file
    file_path = "static/beats.mp3"
    save_audio_to_file(audio, file_path)

# Example usage
text = input("Enter text: ")
target_language = "Spanish"  # Choose between "Spanish", "Hindi", or "Telugu"
translate_and_generate_audio(text, target_language)
