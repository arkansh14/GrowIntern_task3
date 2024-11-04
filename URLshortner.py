from flask import Flask, request, redirect
import sqlite3
import time

app = Flask(__name__)

# Database setup function to create the URLShort table if it doesn't exist
def initialize_database():
    db_path = "C:\\Users\\arkan\\Desktop\\connectdata.db"
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    # Create the URLShort table if it doesn't exist
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS URLShort (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            OriginalURL TEXT NOT NULL,
            ConvertedURL TEXT UNIQUE NOT NULL
        );
    ''')
    conn.commit()
    conn.close()

# Call the database setup function when the app starts
initialize_database()

@app.route("/")
def welcome():
    # HTML form to submit URLs
    form_html = """
        <form method='POST' action='/'>
        <input name='text' placeholder='Enter URL'>
        <input type='Submit' value='Shorten URL'>
        </form>
    """
    return form_html

@app.route("/", methods=['POST'])
def processurl():
    text = request.form['text']
    
    # Remove "www." from the start of the URL if present
    if text.startswith("www."):
        text = text.replace("www.", "", 1)

    # Generate a unique identifier for the shortened URL
    unique_id = str(text[-1:]) + str(round(time.time()))
    shorturl = f"http://127.0.0.1:5000/short/{unique_id}"

    # Connect to SQLite database and insert the original and short URL
    db_path = "C:\\Users\\arkan\\Desktop\\connectdata.db"
    sqlconnection = sqlite3.connect(db_path)
    cursor = sqlconnection.cursor()
    cursor.execute("INSERT INTO URLShort (OriginalURL, ConvertedURL) VALUES (?, ?)", (text, unique_id))
    sqlconnection.commit()
    sqlconnection.close()

    # Return the shortened URL as a clickable link
    return f"Shortened URL: <a href='{shorturl}'>{shorturl}</a>"

@app.route("/short/<unique_id>")
def opensite(unique_id):
    # Connect to the database to find the original URL based on the unique_id
    db_path = "C:\\Users\\arkan\\Desktop\\connectdata.db"
    sqlconnection = sqlite3.connect(db_path)
    cursor = sqlconnection.cursor()
    cursor.execute("SELECT OriginalURL FROM URLShort WHERE ConvertedURL = ?", (unique_id,))
    result = cursor.fetchone()
    sqlconnection.close()
    
    if result:
        original_url = result[0]
        
        # Check if the URL already has http:// or https:// at the beginning
        if not original_url.startswith("http://") and not original_url.startswith("https://"):
            # If not, prepend "https://"
            original_url = "https://" + original_url
        
        # Redirect to the final, formatted URL
        return redirect(original_url)
    else:
        return "URL not found", 404

# Enable debug mode to see detailed error messages in the browser
if __name__ == "__main__":
    app.run(debug=True)