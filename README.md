# SportsChatBotAPI

An AI-powered sports statistics chatbot with automated data collection from NCAA/USports sources. The system features an ETL pipeline using Beautiful Soup and Selenium for extraction, Pandas for transformation, and SQLAlchemy for loading into PostgreSQL. The AI chatbot uses PandasAI and Meta's Llama 2 to handle data analysis requests, answer statistical questions, identify trends, and generate visualizations.

## 🛠️ Architecture

- **ETL Pipeline**: Automated data collection using Beautiful Soup and Selenium, data processing with Pandas, and storage with SQLAlchemy
- **AI Chatbot**: Natural language processing using PandasAI, with integration for Meta's Llama 2
- **Visualization**: Charts and graphs for sports statistics using matplotlib
- **API**: Django REST Framework backend with PostgreSQL database
- **Containerization**: Docker and docker-compose for easy deployment

## 🚀 Local Installation & Setup

### Prerequisites
- Python 3.8+
- Docker and Docker Compose
- Chrome browser (for Selenium scraping)

### Installation Steps

#### Option 1: Using Docker (Recommended)

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd SportsChatBotAPI
   ```

2. Build and start the services:
   ```bash
   docker-compose up --build
   ```

3. The application will be available at `http://localhost:8000`

4. To populate with sample data (recommended for out-of-the-box experience):
   ```bash
   # In another terminal, run:
   docker-compose exec web python manage.py create_sample_data
   ```

5. To stop the services:
   ```bash
   docker-compose down
   ```

#### Option 2: Local Development

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd SportsChatBotAPI
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Set up environment variables (optional):
   ```bash
   # Create .env file with your OpenAI API key if needed
   echo "OPENAI_API_KEY=your_api_key_here" > .env
   ```

5. Run database migrations:
   ```bash
   python manage.py migrate
   ```

6. Create sample data for immediate functionality:
   ```bash
   python manage.py create_sample_data
   ```

7. Start the development server:
   ```bash
   python manage.py runserver
   ```

8. The application will be available at `http://localhost:8000`

## 📡 API Endpoints

### Scraping Endpoints

- `GET /api/scraping/run/` - Start the complete ETL pipeline for all sports data
- `GET /api/scraping/status/{job_id}/` - Get the status of a specific scraping job
- `GET /api/scraping/ncaa/basketball/` - Run the NCAA basketball scraper
- `GET /api/scraping/ncaa/football/` - Run the NCAA football scraper

### Chatbot Endpoints

- `POST /api/chatbot/chat/` - Main chatbot endpoint for querying sports data
  - Request body: `{"message": "your query here", "session_id": "optional session id"}`

- `GET /api/chatbot/session/` - Start a new chat session
- `GET /api/chatbot/session/{session_id}/` - Get chat history for a specific session
- `GET /api/chatbot/analyze/?type={sport}&season={season}` - Get statistical analysis
- `GET /api/chatbot/visualize/?sport={sport}&chart_type={type}&season={season}` - Get visualization data
- `GET /api/chatbot/trends/?sport={sport}&season={season}` - Get sports trends and insights

### ESPN Proxy Endpoints

- `GET /api/espnproxy/get/` - Placeholder endpoint for ESPN data
- `GET /api/espnproxy/fetch-nba-data/` - Fetch and store NBA statistics

## 🎯 Functionality

### ETL Pipeline
- **Data Extraction**: Automatically scrapes NCAA/USports statistics from official websites using Beautiful Soup for static content and Selenium for dynamic content
  - *Note: May require additional setup and may not work with all sources due to anti-bot measures*
- **Data Transformation**: Processes and cleans scraped data using Pandas, standardizing formats and handling missing values
- **Data Loading**: Stores processed data into PostgreSQL database with SQLAlchemy ORM

### AI Chatbot
- **Natural Language Queries**: Understands and responds to questions about sports statistics
  - *Note: Full AI functionality requires an LLM API key (OpenAI by default)*
  - *Without API key: Shows appropriate messages and can still analyze stored data using basic pandas operations*
- **Data Analysis**: Performs analysis on sports data based on user queries
- **Session Management**: Maintains conversation context across multiple requests
- **Statistical Insights**: Provides meaningful analysis of player and team statistics

### Visualization
- **Leaderboards**: Generates visual leaderboards for top performers in various categories
- **Trend Analysis**: Creates charts showing statistical trends over time
- **Comparison Charts**: Visual comparison of player/team statistics
- **Dynamic Images**: Returns base64-encoded visualization images via API
- *All visualization features work out-of-the-box without external dependencies*

### Data Analysis
- **Basketball Stats**: Points, rebounds, assists, field goal percentages, etc.
- **Football Stats**: Passing yards, rushing yards, receiving yards, touchdowns, etc.
- **Statistical Summary**: Averages, totals, and comparative analysis of sports data
- *All data analysis works with stored data; scraping from external sources requires additional setup*

## 🛠️ Configuration

### Environment Variables

Create a `.env` file in the root directory with the following variables:

```
# Django settings
DEBUG=True
SECRET_KEY=your-secret-key-here

# Database (if using PostgreSQL instead of SQLite)
DATABASE_URL=postgresql://username:password@localhost:5432/sportsdb

# OpenAI API (for LLM functionality)
OPENAI_API_KEY=your-openai-api-key-here

# Host configuration
HOST=localhost
```

### Database Migration

If you make changes to models, run:
```bash
python manage.py makemigrations
python manage.py migrate
```

## 🧪 Testing

To test the API endpoints:

1. Start the server (Docker or local)
2. Use curl or a tool like Postman to test endpoints

Example chatbot query:
```bash
curl -X POST http://localhost:8000/api/chatbot/chat/ \
  -H "Content-Type: application/json" \
  -d '{"message": "Who are the top 5 scorers in basketball?","session_id": "12345"}'
```

## 📊 Data Models

The system includes models for:
- **BasketballStats**: Player statistics for basketball (points, rebounds, assists, etc.)
- **FootballStats**: Player statistics for football (passing, rushing, receiving stats, etc.)
- **ChatSession**: Tracks conversation sessions
- **ChatMessage**: Stores individual messages in a session
- **ScrapingJob**: Tracks scraping job status
- **ScrapedData**: Generic model for storing raw scraped data

## 🚀 Out-of-the-Box Experience

After cloning and setting up the project, you can immediately:
- Access all visualization features (leaderboards, trend analysis, etc.)
- Query the database using the API endpoints
- Use the chatbot functionality (with basic responses without AI enhancement)
- Run data analysis functions on sample data
- Explore the pre-populated sample sports statistics

To get started immediately with sample data, run:
```bash
python manage.py create_sample_data  # Creates demo basketball and football stats
```

For full AI functionality, configure an LLM API key as described in the Configuration section.

## 🚀 Deployment

For production deployment:

1. Update the `docker-compose.yml` with production settings
2. Configure environment variables for production
3. Set up a production-grade PostgreSQL database
4. Configure a reverse proxy (e.g., Nginx) in front of Django

## 🔧 Troubleshooting

- If scraping fails, ensure Chrome is installed and chromedriver is available
- If visualization fails, ensure matplotlib and required dependencies are installed
- If chatbot fails, ensure OpenAI API key is set (or implement Llama 2 integration)
