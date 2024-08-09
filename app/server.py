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
from email.mime.base import MIMEBase
from email import encoders
import psycopg2
import sys
import csv  # Make sure to import csv module

load_dotenv()

app = Flask(__name__, template_folder='../templates')

def initialize_database():
    try:
        queries = load_sql_queries('./db/queries/initialize.sql').split(';')
        queries = [query.strip() for query in queries if query.strip()]
        if queries:
            conn = get_db_connection()
            cur = conn.cursor()
            cur.execute(queries[0])
            conn.commit()
            cur.close()
            conn.close()
            print("Database and tables created successfully!", file=sys.stderr)
        else:
            print("No queries found in the file.", file=sys.stderr)
    except (Exception, psycopg2.Error) as error:
        print(f"Error while creating database: {error}", file=sys.stderr)

@app.route('/')
def welcome():
    initialize_database()
    summarize()
    return "Welcome to the home"

@app.route('/create', methods=['POST'])
def create():
    try:
        queries = load_sql_queries('./db/queries/initialize.sql').split(';')
        queries = [query.strip() for query in queries if query.strip()]
        if queries:
            conn = get_db_connection()
            cur = conn.cursor()
            cur.execute(queries[0])
            conn.commit()
            cur.close()
            conn.close()
            return "Tables created successfully!", 200
        else:
            return "No queries found in the file.", 400
    except (Exception, psycopg2.Error) as error:
        return f"Error while creating table: {error}", 500

@app.route('/drop', methods=['DELETE'])
def drop():
    try:
        queries = load_sql_queries('./db/queries/drop.sql').split(';')
        queries = [query.strip() for query in queries if query.strip()]
        if queries:
            conn = get_db_connection()
            cur = conn.cursor()
            cur.execute(queries[0])
            conn.commit()
            cur.close()
            conn.close()
            return "Table dropped successfully!", 200
        else:
            return "No queries found in the file.", 400
    except (Exception, psycopg2.Error) as error:
        return f"Error while dropping table: {error}", 500

@app.route('/add', methods=['POST'])
def add():
    try:
        queries = load_sql_queries('./db/queries/initialize.sql').split(';')
        queries = [query.strip() for query in queries if query.strip()]
        if len(queries) > 1:
            conn = get_db_connection()
            cur = conn.cursor()
            cur.execute(queries[1])
            conn.commit()
            cur.close()
            conn.close()
            return "Data added successfully!", 200
        else:
            return "No queries found in the file.", 400
    except (Exception, psycopg2.Error) as error:
        return f"Error while adding data: {error}", 500

@app.route('/view', methods=['GET'])
def view():
    try:
        query = load_sql_queries('./db/queries/view.sql').split(';')
        queries = [query.strip() for query in query if query.strip()]
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(queries[0])
        results = cur.fetchall()
        columns = [desc[0] for desc in cur.description]
        cur.close()
        conn.close()

        data = [dict(zip(columns, row)) for row in results]
        return render_template('view.html', data=data, columns=columns)
    except (Exception, psycopg2.Error) as error:
        return f"Error while fetching data: {error}", 500

@app.route('/send_mail', methods=['POST'])
def send_email():
    from_email = os.getenv("SENDER_EMAIL")
    password = os.getenv('APP_PASSWORD')
    to_email = os.getenv("RECEIVER_EMAIL")
    subject = "Test Subject"
    body = "New summary is generated."

    msg = MIMEMultipart()
    msg['From'] = from_email
    msg['To'] = to_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    csv_file_path = write_summary_to_csv()

    if csv_file_path:
        try:
            with open(csv_file_path, 'rb') as file:
                part = MIMEBase('application', 'octet-stream')
                part.set_payload(file.read())
                encoders.encode_base64(part)
                part.add_header('Content-Disposition', f'attachment; filename={os.path.basename(csv_file_path)}')
                msg.attach(part)
        except Exception as e:
            return f'Failed to attach file: {e}', 500

    try:
        s = smtplib.SMTP('smtp.gmail.com', 587)
        s.starttls()
        s.login(from_email, password)
        s.sendmail(from_email, to_email, msg.as_string())
        s.quit()
        return 'Mail has been sent successfully', 200
    except Exception as e:
        return f'Failed to send mail: {e}', 500

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
        if content_type == 'application/atom+xml':
            root = ET.fromstring(request.data)
            vd.value = get_videoId(root)
            if is_livestream(str(vd.value)):
                p = Process(target=process_livechat, args=(vd,))
                p.start()
                # Let the process run for a while; terminate it if needed
                p.join(timeout=60 * 60)  # Run for up to 1 hour
                if p.is_alive():
                    p.terminate()
                summarize()
            return '', 204
        else:
            abort(415)
    else:
        abort(405)

def load_sql_queries(file_path):
    with open(file_path, 'r') as file:
        return file.read()

def get_db_connection():
    return psycopg2.connect(
        database=os.getenv("DATABASE"),
        user=os.getenv("USER"),
        password=os.getenv("PASSWORD"),
        host=os.getenv("HOST"),
        port=os.getenv("PORT")
    )

def is_livestream(video_id):
    API_KEY = os.getenv('API_KEY')
    YOUTUBE_API_URL = os.getenv('API_URL')
    params = {
        'id': video_id,
        'part': 'snippet, liveStreamingDetails',
        'key': API_KEY
    }
    response = requests.get(YOUTUBE_API_URL, params=params)
    if response.status_code == 200:
        data = response.json()
        if 'items' in data and len(data['items']) > 0:
            item = data['items'][0]
            if 'liveStreamingDetails' in item:
                return True
    return False

def write_summary_to_csv():
    try:
        query = load_sql_queries('./db/queries/view.sql').split(';')
        queries = [query.strip() for query in query if query.strip()]

        if not query:
            return None

        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(queries[1])
        rows = cur.fetchall()

        csv_file_path = 'livechat_data.csv'
        with open(csv_file_path, 'w', newline='') as csvfile:
            csvwriter = csv.writer(csvfile)
            column_names = [desc[0] for desc in cur.description]
            csvwriter.writerow(column_names)
            csvwriter.writerows(rows)

        cur.close()
        conn.close()
        return csv_file_path

    except (Exception, psycopg2.Error) as error:
        print(f"Error while writing data to CSV: {error}", file=sys.stderr)
        return None

def summarize():
    try:
        query = load_sql_queries('./db/queries/summary.sql').strip()
        queries = [query.strip() for query in query.split(';') if query.strip()]

        if len(queries) < 3:
            print("Insufficient queries found in the file.", file=sys.stderr)
            return

        conn = get_db_connection()
        cur = conn.cursor()

        cur.execute(queries[0])
        aggregated_data = cur.fetchall()

        cur.execute(queries[1])
        cur.executemany(queries[2], aggregated_data)

        conn.commit()
        cur.close()
        conn.close()
        print("Data has been successfully aggregated and inserted into author_totals table", file=sys.stderr)

    except (Exception, psycopg2.Error) as error:
        print(f"Error while aggregating data: {error}", file=sys.stderr)

def process_livechat(vd):
    print("Tracking Started...")
    livechat = pytchat.create(video_id=str(vd.value))
    conn = get_db_connection()
    cur = conn.cursor()

    while livechat.is_alive():
        try:
            for c in livechat.get().sync_items():
                if c.amountValue is None:
                    c.amountValue = 0
                cur.execute("""
                    INSERT INTO livechat_data (datetime, author_name, message, amount_value)
                    VALUES (%s, %s, %s, %s)
                """, (c.datetime, c.author.name, c.message, c.amountValue))
                conn.commit()
        except KeyboardInterrupt:
            livechat.terminate()
            break
        except Exception as e:
            print(f"Error during live chat processing: {e}", file=sys.stderr)
            break

    cur.close()
    conn.close()
    print("Tracking Finished...", file=sys.stderr)

def get_grok_url():
    try:
        response = requests.get('http://ngrok:4040/api/tunnels')
        tunnels = response.json().get('tunnels', [])
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
    callback_url = get_grok_url() or os.getenv('CALLBACK_URL')

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
    freeze_support()
    manager = Manager()
    vd = manager.Value(str, "")
    subscribe_to_channel()
    app.run(host='0.0.0.0', port=int(os.getenv("FLASK_RUN_PORT", 8000)))
