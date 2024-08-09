I dont have money to deploy this, so might be deployed later.
Main core functionality is implemeneted at this moment.
# Superchat Tracking System

This project is a Dockerized Flask-based web application for tracking YouTube live chat superchats, with data stored in a PostgreSQL database. The application allows you to track live chat messages, aggregate superchat amounts by author, and send the data as a CSV file via email.

## Features

- **Livechat Tracking**: Automatically tracks live chat messages from a YouTube live stream.
- **Superchat Aggregation**: Calculates the total superchat amount for each user.
- **Database Storage**: Stores live chat data and aggregated results in a PostgreSQL database.
- **CSV Export and Email**: Generates a CSV summary of the tracked data and emails it as an attachment.
- **Web Interface**: Simple Flask web interface to interact with the database and view results.

## Prerequisites

- Docker
- Docker Compose
- Python 3.x
- PostgreSQL

## Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/your-repo/superchat-tracker.git
cd superchat-tracker
```

### 2. Set up an environment variable

Create a .env file in the project root directory with the following variables:

```bash
# PostgreSQL
DATABASE=your_database_name
USER=your_database_user
PASSWORD=your_database_password
HOST=db
PORT=5432

# YouTube API
API_KEY=your_youtube_api_key
API_URL=https://www.googleapis.com/youtube/v3/videos

# Email Settings
SENDER_EMAIL=your_email@example.com
APP_PASSWORD=your_email_app_password
RECEIVER_EMAIL=recipient_email@example.com

# ngrok
CALLBACK_URL=your_ngrok_callback_url

# YouTube PubSubHubBub
HUB_URL=https://pubsubhubbub.appspot.com/subscribe
TOPIC_URL=https://www.youtube.com/xml/feeds/videos.xml?channel_id=your_channel_id
```

### 3. Build and run docker

```bash
docker-compose up --build
```

### 4. Access to the service
Once the containers are running, you can access the Flask application at: __http://localhost:8000__

## Usage

### API Endpoints

- **GET `/`**: Initialize the database and summarize data.
- **POST `/create`**: Create the necessary database tables.
- **DELETE `/drop`**: Drop the existing database tables.
- **POST `/add`**: Insert sample data into the database.
- **GET `/view`**: View the contents of the `livechat_data` and `author_total` tables.
- **POST `/send_mail`**: Send an email with the CSV file attached.
- **POST `/youtube-callback`**: Handle YouTube PubSubHubbub notifications for live chat tracking.

### CSV Export

The system generates a CSV file containing the live chat data and sends it via email to the specified recipient.

## Development

### Running Locally

To run the application locally without Docker, ensure you have Python and PostgreSQL installed, then follow these steps:

1. **Create a virtual environment and install dependencies:**

    ```bash
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    ```

2. **Set up the PostgreSQL database and configure environment variables in the `.env` file.**

3. **Start the Flask application:**

    ```bash
    flask run
    or
    python server.py
    ```

### Database Setup

The database is initialized using SQL scripts located in the `./db/queries/` directory. The primary tables include:

- **`livechat_data`**: Stores live chat messages with author names and superchat amounts.
- **`author_total`**: Stores the aggregated superchat amounts for each author.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Flask
- PostgreSQL
- pytchat (YouTube Live Chat Library)
- Docker
