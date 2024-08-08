from flask import Flask, request, abort, render_template
import requests
from dotenv import load_dotenv
import os
import xml.etree.ElementTree as ET
from multiprocessing import Process, Manager, freeze_support
import pytchat 
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import psycopg2

load_dotenv()

app = Flask(__name__, template_folder='../templates')


@app.before_request
def initialize_database():
    try:
        # Load SQL queries from the file
        queries = load_sql_queries('./db/queries/initialize.sql').split(';')
        
        # Remove any empty queries from the list
        queries = [query.strip() for query in queries if query.strip()]
        
        conn = get_db_connection()
        cur = conn.cursor()

        cur.execute(queries[0])
        
        conn.commit()
        cur.close()
        conn.close()
        
        print("Database and tables created successfully!")
    except (Exception, psycopg2.Error) as error:
        print(f"Error while creating database: {error}")

@app.route('/')
def welcome():
    return "Welcome to the home"

@app.route('/add')
def add():
    try:
        # Load SQL queries from the file
        queries = load_sql_queries('./db/queries/initialize.sql').split(';')
        
        # Remove any empty queries from the list
        queries = [query.strip() for query in queries if query.strip()]
        
        conn = get_db_connection()
        cur = conn.cursor()


        cur.execute(queries[1])
        
        conn.commit()
        cur.close()
        conn.close()
        
        return "Database and tables created successfully!", 200
    except (Exception, psycopg2.Error) as error:
        return f"Error while creating database: {error}", 500

@app.route('/view')
def view():
    try:
        # Load SQL query from the file
        query = load_sql_queries('./db/queries/view.sql').strip() 

        # Get database connection
        conn = get_db_connection()

        # Create a cursor object
        cur = conn.cursor()
        
        # Execute the SQL query
        cur.execute(query)
        
        # Fetch all results
        results = cur.fetchall()
        
        # Get column names
        columns = [desc[0] for desc in cur.description]

        # Close the cursor and connection
        cur.close()
        conn.close()

        # Format results as a list of dictionaries
        data = [dict(zip(columns, row)) for row in results]

        # Return results as a JSON response
        return render_template('view.html', data=data, columns=columns)
    
    except (Exception, psycopg2.Error) as error:
        return f"Error while fetching data: {error}", 500


@app.route('/send_mail')
def send_email():
    from_email = os.getenv("SENDER_EMAIL")  # Change to your email
    password = os.getenv('APP_PASSWORD')
    to_email = os.getenv("RECEIVER_EMAIL")  # Change to recipient's email
    subject = "Test Subject"
    body = "This is a test message."

    # Create the email message
    msg = MIMEMultipart()
    msg['From'] = from_email
    msg['To'] = to_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    try:
        # Connect to the Gmail SMTP server
        s = smtplib.SMTP('smtp.gmail.com', 587)
        s.starttls()
        s.login(from_email, password)
        s.sendmail(from_email, to_email, msg.as_string())
        s.quit()
        return 'Mail has been sent successfully'
    except Exception as e:
        return f'Failed to send mail: {e}'

@app.route('/youtube-callback', methods=["GET", "POST"])
def youtube_callback():
    if request.method == "GET":
        hub = request.args.get("hub.challenge")
        if hub:
            return hub
        else:
            abort(400)
    elif request.method == "POST":
        content_type = request.headers.get('Content-Type')
        print(f"Content-Type: {content_type}")

        if content_type == 'application/atom+xml':
            root = ET.fromstring(request.data)
            print("Received notification XML:", ET.tostring(root, encoding='utf8').decode('utf8'))
            vd.value = get_videoId(root)
            print("Video ID: ", str(vd.value))

            if is_livestream(str(vd.value)):
                print("The video is a livestream.")
                p = Process(target=process_livechat, args=(vd,))
                p.start()
            else:
                print("The video is not a livestream.")
            return '', 204
        else:
            abort(415)  # Unsupported Media Type
    else:
        abort(405)

def load_sql_queries(file_path):
    with open(file_path, 'r') as file:
        return file.read()

def create_dictionary():
    pass

def get_db_connection():
    conn = psycopg2.connect(
            database=os.getenv("DATABASE"),
            user=os.getenv("USER"),
            password=os.getenv("PASSWORD"),
            host=os.getenv("HOST"),
            port=os.getenv("PORT")
            )
    return conn

def is_livestream(video_id):
    API_KEY =  os.getenv('API_KEY')
    YOUTUBE_API_URL = os.getenv('API_URL')
    params = {
        'id': video_id,
        'part': 'snippet, liveStreamingDetails',
        'key': API_KEY
    }
    response = requests.get(YOUTUBE_API_URL, params = params)
    if response.status_code == 200:
        data = response.json()
        if 'items' in data and len(data['items']) > 0:
            item = data['items'][0]
            if 'liveStreamingDetails' in item:
                return True
    return False

def process_livechat(vd):
    livechat = pytchat.create(video_id=str(vd.value))
    while livechat.is_alive():
        try:
            for c in livechat.get().sync_items():
                print(f"{c.datetime} [{c.author.name}] - {c.message}")
                if c.amountValue:
                    print(f"Superchat detected, {c.datetime} [{c.author.name}] - {c.amountValue}")
        except KeyboardInterrupt:
            livechat.terminate()
            break

def get_grok_url():
    try:
        response = requests.get('http://ngrok:4040/api/tunnels')
        tunnels = response.json()['tunnels']
        for tunnel in tunnels:
            if tunnel['proto'] == 'https':
                return tunnel['public_url'] + "/youtube-callback"
        return None
    except Exception as e:
        print("Error in get_grok_url function: ", e)

def get_videoId(root):
    namespaces = {
        'ns0': 'http://www.w3.org/2005/Atom',
        'ns1': 'http://www.youtube.com/xml/schemas/2015'
    }
    for entry in root.findall('ns0:entry', namespaces):
        videoId = entry.find('ns1:videoId', namespaces).text
        return videoId

def subscribe_to_channel():
    print("Subscription started...")

    hub_url = os.getenv('HUB_URL')
    topic_url = os.getenv('TOPIC_URL')
    callback_url = get_grok_url()

    if not callback_url:
        callback_url = os.getenv('CALLBACK_URL')

    data = {
        'hub.mode': 'subscribe',
        'hub.topic': topic_url,
        'hub.callback': callback_url,
    }
    response = requests.post(hub_url, data=data)
    if response.status_code == 202:
        print('Subscribed successfully!')
    else:
        print("Failed to subscribe: ", response.status_code, response.text)

if __name__ == '__main__':
    freeze_support()  # Needed for Windows to prevent RuntimeError
    manager = Manager()
    vd = manager.Value(str, "")
    subscribe_to_channel()
    app.run(host='0.0.0.0', port=int(os.getenv("FLASK_RUN_PORT", 8000)))
