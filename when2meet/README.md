# When2Meet Extended

A collaborative scheduling tool that helps groups find the best time to meet. This is an extended version of the popular When2Meet platform with additional features and improved user experience.

## Features

- User authentication and authorization
- Event creation and management
- Real-time availability updates
- Interactive grid-based scheduling interface
- Heatmap visualization of group availability
- Automatic best time calculation
- WebSocket-based real-time synchronization

## Requirements

- Python 3.8 or higher
- Flask and related packages (see requirements.txt)
- Modern web browser with JavaScript enabled

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/when2meet-extended.git
cd when2meet-extended
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

4. Set up environment variables:
Create a `.env` file in the project root with the following content:
```
SECRET_KEY=your-secret-key-here
```

5. Initialize the database:
```bash
flask db init
flask db migrate
flask db upgrade
```

## Running the Application

1. Start the development server:
```bash
python app.py
```

2. Open your web browser and navigate to:
```
http://localhost:5000
```

## Usage

1. Register a new account or log in with existing credentials
2. Create a new event by specifying:
   - Event name
   - Date range
   - Time range
   - List of invitees (comma-separated email addresses)
3. Invitees will receive access to the event and can mark their availability
4. The system will automatically calculate and display the best meeting time
5. All updates are synchronized in real-time across all participants

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details. 