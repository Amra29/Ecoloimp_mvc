# Servicio Técnico - MVC Application

A technical service management application built with Flask (backend) and Next.js (frontend).

## Project Structure

```
.
├── backend/               # Flask backend application
│   ├── app/              # Application package
│   ├── migrations/       # Database migrations
│   └── requirements.txt  # Python dependencies
├── frontend/             # Next.js frontend application
│   ├── pages/
│   ├── public/
│   └── package.json
├── scripts/              # Utility scripts
│   ├── backup/           # Backup of old initialization scripts
│   └── initialize_app.py # Consolidated initialization script
└── README.md             # This file
```

## Getting Started

### Prerequisites

- Python 3.9+
- Node.js 16+
- PostgreSQL (or SQLite for development)

### Backend Setup

1. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: .\venv\Scripts\activate
   ```

2. Install dependencies:
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

3. Set up environment variables:
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

4. Initialize the database:
   ```bash
   python scripts/initialize_app.py
   ```

5. Run the development server:
   ```bash
   flask run
   ```

### Frontend Setup

1. Install dependencies:
   ```bash
   cd frontend
   npm install
   ```

2. Start the development server:
   ```bash
   npm run dev
   ```

## Development

### Code Style

- Backend: Follow PEP 8 and PEP 257
- Frontend: Follow the project's ESLint and Prettier configuration

### Database Migrations

To create a new database migration:

```bash
flask db migrate -m "Your migration message"
flask db upgrade
```

## Deployment

See `DEPLOYMENT.md` for deployment instructions.

## License

[Your License Here]
