# Crypto Order Block Detector

A sophisticated web application that automatically detects and visualizes Order Blocks (OBs) on cryptocurrency price charts using Smart Money Concepts (SMC) principles.

## Features

- **Real-time Data**: Connect to Binance API for live cryptocurrency data
- **Order Block Detection**: Automatically identify bullish and bearish Order Blocks
- **Break of Structure (BOS)**: Detect and visualize market structure breaks
- **Interactive Charts**: Beautiful, responsive charts using Plotly
- **Multiple Timeframes**: Support for 15m, 1h, 4h, and 1d timeframes
- **50+ Trading Pairs**: Analyze popular USDT pairs
- **Modern UI**: Dark theme with glass morphism design
- **Mobile Responsive**: Works on desktop, tablet, and mobile devices

## How It Works

### Order Block Detection Algorithm

1. **Swing Point Identification**: Identifies swing highs and lows for structure analysis
2. **Break of Structure (BOS) Detection**: Looks for significant moves that break recent market structure
3. **Order Block Validation**: Finds the last opposite candle before a significant move
4. **Visual Representation**: Displays Order Blocks as rectangular zones on the chart

### Detection Criteria

- **Bullish Order Block**: Last bearish candle before a significant bullish move that breaks structure
- **Bearish Order Block**: Last bullish candle before a significant bearish move that breaks structure
- **Minimum Move Threshold**: 1.5% price movement for validation
- **BOS Threshold**: 2.0% break of recent swing points

## Installation & Setup

### Prerequisites

- Python 3.11.7 or higher
- pip (Python package manager)

### Local Development Setup

1. **Clone or download the project files**

2. **Create a virtual environment** (recommended):
   ```bash
   python -m venv venv
   
   # Windows
   venv\Scripts\activate
   
   # macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application**:
   ```bash
   python app.py
   ```

5. **Open your browser** and navigate to:
   ```
   http://localhost:5000
   ```

## Network Access & Static IP Configuration

### Default Configuration

The application is configured to run on `0.0.0.0:5000`, making it accessible from any IP address within your network.

### Accessing from Other Devices

#### 1. Find Your Server's IP Address

**Windows:**
```cmd
ipconfig
# Look for "IPv4 Address" line
# Example: 192.168.1.100
```

**Mac/Linux:**
```bash
ifconfig
# or
ip addr show
# Look for IP in 192.168.x.x or 10.x.x.x range
```

#### 2. Access from Other Devices

Once you know the server's IP (e.g., `192.168.1.100`), other devices on the same network can access:

```
http://192.168.1.100:5000
```

#### 3. Firewall Configuration (If Needed)

**Windows Firewall:**
```cmd
# Run Command Prompt as Administrator
netsh advfirewall firewall add rule name="Python Flask App" dir=in action=allow protocol=TCP localport=5000
```

**Linux (Ubuntu/Debian):**
```bash
sudo ufw allow 5000
sudo ufw reload
```

**macOS:**
```bash
# Usually no configuration needed
# Check System Preferences → Security & Privacy → Firewall
```

### Custom Port Configuration

To change the port (e.g., from 5000 to 8080), edit `app.py`:

```python
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8080)  # Change port here
```

### Internet Access (Advanced)

#### 1. Port Forwarding on Router

1. Access your router (usually `192.168.1.1` or `192.168.0.1`)
2. Find **"Port Forwarding"** or **"Virtual Server"** section
3. Add new rule:
   - **Service Name**: Flask App
   - **External Port**: 5000
   - **Internal Port**: 5000
   - **Internal IP**: Server's IP (e.g., 192.168.1.100)
   - **Protocol**: TCP

#### 2. Security When Exposing to Internet

⚠️ **Security Warning:**
```python
# DO NOT use debug=True when exposing to internet
if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=5000)
```

### Network Example

```
Router (192.168.1.1)
├── Flask Server (192.168.1.100:5000)
├── Computer A (192.168.1.101) → access: http://192.168.1.100:5000
├── Phone B (192.168.1.102) → access: http://192.168.1.100:5000
└── Laptop C (192.168.1.103) → access: http://192.168.1.100:5000
```

### Check IP Script

Run the included `kiem_tra_ip.py` script to automatically detect and display network information:

```bash
python kiem_tra_ip.py
```

This script will:
- Detect your current IP address
- Check if port 5000 is open
- Provide direct access URLs
- Show firewall configuration commands

## Usage

1. **Select Trading Pair**: Choose from 50+ available cryptocurrency pairs
2. **Choose Timeframe**: Select from 15m, 1h, 4h, or 1d intervals
3. **Click "Analyze Order Blocks"**: The app will fetch data and process it
4. **View Results**: 
   - Interactive candlestick chart with detected Order Blocks
   - Green rectangles = Bullish Order Blocks
   - Red rectangles = Bearish Order Blocks
   - Triangle markers = Break of Structure points
   - Statistics panel showing detection counts

## Deployment Options

### 1. Heroku Deployment

1. **Create a Heroku account** at [heroku.com](https://heroku.com)

2. **Install Heroku CLI** and login:
   ```bash
   heroku login
   ```

3. **Create a new Heroku app**:
   ```bash
   heroku create your-app-name
   ```

4. **Deploy to Heroku**:
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git push heroku main
   ```

5. **Open your deployed app**:
   ```bash
   heroku open
   ```

### 2. Railway Deployment

1. **Create account** at [railway.app](https://railway.app)
2. **Connect your GitHub repository**
3. **Deploy automatically** - Railway will detect Python and use the Procfile

### 3. Render Deployment

1. **Create account** at [render.com](https://render.com)
2. **Create a new Web Service**
3. **Connect your repository**
4. **Use these settings**:
   - Environment: Python 3
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `gunicorn app:app`

### 4. Docker Deployment

Create a `Dockerfile`:

```dockerfile
FROM python:3.11.7-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 5000

CMD ["gunicorn", "app:app", "--bind", "0.0.0.0:5000"]
```

Build and run:
```bash
docker build -t crypto-ob-detector .
docker run -p 5000:5000 crypto-ob-detector
```

## Project Structure

```
crypto_project/
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── Procfile              # Deployment configuration
├── runtime.txt           # Python version specification
├── README.md             # This file
├── plan_eng.md           # Original project plan
├── kiem_tra_ip.py        # IP detection script
├── cai_dat.py            # Vietnamese setup script
├── HUONG_DAN_TIENG_VIET.md # Vietnamese guide
├── HUONG_DAN_NHANH.md    # Vietnamese quick guide
├── templates/
│   └── index.html        # Frontend HTML template
└── vn_version.txt        # Vietnamese version documentation
```

## Technical Stack

- **Backend**: Flask (Python web framework)
- **Data Source**: Binance API via CCXT library
- **Data Processing**: Pandas, NumPy
- **Charting**: Plotly.js for interactive charts
- **Frontend**: HTML5, CSS3, JavaScript, Bootstrap 5
- **Deployment**: Gunicorn WSGI server

## API Endpoints

- `GET /`: Main application page
- `POST /api/analyze`: Analyze Order Blocks for given symbol/timeframe
- `GET /api/symbols`: Get available trading symbols

## Configuration

The application uses environment variables for configuration:

- `FLASK_ENV`: Set to 'production' for deployment
- `PORT`: Port number (default: 5000)

## Performance Considerations

- **Data Caching**: Consider implementing Redis for caching market data
- **Rate Limiting**: Respect Binance API rate limits (default: 1200 requests/minute)
- **Optimization**: For high-traffic scenarios, consider using WebSocket connections for real-time data

## Troubleshooting

### Common Issues

1. **"Failed to fetch data"**: Check internet connection and try different trading pair
2. **"Module not found"**: Run `pip install -r requirements.txt`
3. **Port already in use**: Change port in `app.py` or kill existing process
4. **Can't access from other devices**: Check firewall settings and network configuration

### Network Connectivity Issues

```bash
# Test connectivity from another device
ping 192.168.1.100

# Test port accessibility
telnet 192.168.1.100 5000
# or
nc -zv 192.168.1.100 5000
```

## Limitations & Disclaimers

1. **Educational Purpose**: This tool is for educational and analysis purposes only
2. **Not Financial Advice**: Trading involves significant risk
3. **False Positives**: Automated detection may identify patterns that aren't true Order Blocks
4. **Market Conditions**: Performance may vary in different market conditions
5. **API Dependency**: Requires stable internet connection for data fetching

---

## 📖 Documentation

- **English**: README.md (this file)
- **Vietnamese**: HUONG_DAN_TIENG_VIET.md (complete guide)
- **Quick Start**: HUONG_DAN_NHANH.md (Vietnamese quick guide)

**Happy Trading! 📈**

*Remember: This tool is for analysis only. Always do your own research and never risk more than you can afford to lose.* 