#!/usr/bin/env python3
"""
Standalone Chart Viewer for Crypto Analysis
This creates and displays candlestick charts with trend lines and order blocks.
"""

from app import OrderBlockDetector
import sys
import os
import webbrowser
import tempfile
from datetime import datetime

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import from your app


def create_standalone_chart(symbol="BTC/USDT", timeframe="1h"):
    """Create a standalone HTML chart file"""

    print(f"🔍 Creating chart for {symbol} ({timeframe})...")

    # Initialize detector
    detector = OrderBlockDetector()

    # Get data (will use sample data if API fails)
    print("📊 Fetching market data...")
    df = detector.fetch_ohlcv_data(symbol, timeframe, limit=500)

    if df is None or len(df) == 0:
        print("❌ Failed to get data, generating sample data...")
        df = detector.generate_sample_data(symbol)

    if df is None or len(df) == 0:
        print("❌ Failed to generate any data")
        return None

    print(f"✅ Got {len(df)} candles")

    # Add swing highs/lows
    print("🔍 Detecting swing points...")
    df = detector.find_swing_highs_lows(df)

    # Detect order blocks (this will also detect BOS)
    print("📦 Detecting order blocks...")
    df = detector.detect_order_blocks(df)

    # Create the chart
    print("📈 Creating interactive chart...")
    fig = detector.create_chart(df, symbol)

    # Create HTML file
    chart_html = f"""
<!DOCTYPE html>
<html>
<head>
    <title>{symbol} - Crypto Chart Analysis</title>
    <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
    <style>
        body {{
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #1a1a1a;
            color: white;
        }}
        .header {{
            text-align: center;
            margin-bottom: 20px;
        }}
        .info {{
            background: rgba(255,255,255,0.1);
            padding: 15px;
            border-radius: 10px;
            margin-bottom: 20px;
        }}
        .chart-container {{
            height: 800px;
            background: rgba(255,255,255,0.05);
            border-radius: 10px;
            padding: 10px;
        }}
        .legend {{
            display: flex;
            justify-content: center;
            flex-wrap: wrap;
            gap: 20px;
            margin-top: 10px;
        }}
        .legend-item {{
            display: flex;
            align-items: center;
            gap: 5px;
        }}
        .legend-color {{
            width: 15px;
            height: 15px;
            border-radius: 3px;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>{symbol} Chart Analysis</h1>
        <p>Timeframe: {timeframe} | Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
    </div>
    
    <div class="info">
        <h3>Chart Information:</h3>
        <p><strong>Total Candles:</strong> {len(df)}</p>
        <p><strong>Bullish Order Blocks:</strong> {len(df[df['bullish_ob']])}</p>
        <p><strong>Bearish Order Blocks:</strong> {len(df[df['bearish_ob']])}</p>
        <p><strong>Swing Highs:</strong> {len(df[df['swing_high']])}</p>
        <p><strong>Swing Lows:</strong> {len(df[df['swing_low']])}</p>
    </div>
    
    <div class="chart-container">
        <div id="chartDiv" style="height: 100%;"></div>
    </div>
    
    <div class="legend">
        <div class="legend-item">
            <div class="legend-color" style="background: #26a69a;"></div>
            <span>Bullish Candles</span>
        </div>
        <div class="legend-item">
            <div class="legend-color" style="background: #ef5350;"></div>
            <span>Bearish Candles</span>
        </div>
        <div class="legend-item">
            <div class="legend-color" style="background: rgba(0,255,0,0.3);"></div>
            <span>Bullish Order Blocks</span>
        </div>
        <div class="legend-item">
            <div class="legend-color" style="background: rgba(255,0,0,0.3);"></div>
            <span>Bearish Order Blocks</span>
        </div>
        <div class="legend-item">
            <div class="legend-color" style="background: #FFD700;"></div>
            <span>Resistance Lines</span>
        </div>
        <div class="legend-item">
            <div class="legend-color" style="background: #00BFFF;"></div>
            <span>Support Lines</span>
        </div>
    </div>
    
    <script>
        // Convert the Plotly figure to JSON
        var chartData = {fig.to_json()};
        
        // Plotly configuration
        var config = {{
            displayModeBar: true,
            displaylogo: false,
            modeBarButtonsToRemove: ['pan2d', 'lasso2d', 'select2d'],
            responsive: true
        }};
        
        // Create the plot
        Plotly.newPlot('chartDiv', chartData.data, chartData.layout, config);
        
        console.log("Chart loaded successfully!");
        console.log("Data points:", chartData.data.length);
    </script>
</body>
</html>
"""

    # Save to temporary file
    temp_file = tempfile.NamedTemporaryFile(
        mode='w', suffix='.html', delete=False, encoding='utf-8')
    temp_file.write(chart_html)
    temp_file.close()

    return temp_file.name


def main():
    """Main function"""
    print("=" * 60)
    print("📈 CRYPTO CHART VIEWER")
    print("=" * 60)

    # You can customize these parameters
    symbols_to_test = ["BTC/USDT", "ETH/USDT"]
    timeframe = "1h"

    for symbol in symbols_to_test:
        try:
            chart_file = create_standalone_chart(symbol, timeframe)
            if chart_file:
                print(f"✅ Chart created: {chart_file}")
                print(f"🌐 Opening {symbol} chart in browser...")
                webbrowser.open(f"file://{chart_file}")
                print(f"📁 Chart file saved: {chart_file}")
            else:
                print(f"❌ Failed to create chart for {symbol}")

        except Exception as e:
            print(f"❌ Error creating chart for {symbol}: {e}")

    print("\n" + "=" * 60)
    print("🎉 CHART GENERATION COMPLETED")
    print("=" * 60)
    print("📝 Instructions:")
    print("  • Charts will open automatically in your browser")
    print("  • You can zoom, pan, and interact with the charts")
    print("  • Green areas = Bullish Order Blocks")
    print("  • Red areas = Bearish Order Blocks")
    print("  • Gold lines = Resistance trend lines")
    print("  • Blue lines = Support trend lines")
    print("  • Triangles = Break of Structure points")


if __name__ == "__main__":
    main()
