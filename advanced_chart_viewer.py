#!/usr/bin/env python3
"""
Advanced Chart Viewer with Enhanced Trend Line Detection
This creates professional-looking charts similar to TradingView with precise trend lines.
"""

from app import OrderBlockDetector
import sys
import os
import webbrowser
import tempfile
import numpy as np
import pandas as pd
from datetime import datetime
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import from your app


class AdvancedTrendLineDetector:
    """Enhanced trend line detection using multiple algorithms"""

    def __init__(self):
        self.min_touches = 2
        self.max_slope_angle = 85  # degrees
        self.tolerance_percentage = 0.5  # 0.5% tolerance for line touches

    def detect_precise_trend_lines(self, df, lookback_period=100):
        """Detect trend lines using advanced algorithms"""
        trend_lines = []

        # Get recent data for analysis
        recent_df = df.tail(lookback_period).copy().reset_index(drop=True)

        # Detect support lines (connecting lows)
        support_lines = self._detect_support_lines(recent_df)
        trend_lines.extend(support_lines)

        # Detect resistance lines (connecting highs)
        resistance_lines = self._detect_resistance_lines(recent_df)
        trend_lines.extend(resistance_lines)

        # Filter and rank by quality
        return self._filter_best_lines(trend_lines, max_lines=8)

    def _detect_support_lines(self, df):
        """Detect support trend lines connecting significant lows"""
        support_lines = []

        # Find local minima (significant lows)
        lows = self._find_significant_lows(df)

        # Try all combinations of lows to form trend lines
        for i in range(len(lows)):
            for j in range(i + 1, len(lows)):
                point1 = lows[i]
                point2 = lows[j]

                # Calculate line parameters
                x1, y1 = point1['index'], point1['price']
                x2, y2 = point2['index'], point2['price']

                if x2 == x1:  # Avoid division by zero
                    continue

                slope = (y2 - y1) / (x2 - x1)
                intercept = y1 - slope * x1

                # Check if slope angle is reasonable
                angle = np.degrees(np.arctan(slope))
                if abs(angle) > self.max_slope_angle:
                    continue

                # Count touches and validate line
                touches = self._count_line_touches(df, slope, intercept, 'low')
                if touches >= self.min_touches:
                    support_lines.append({
                        'type': 'support',
                        'slope': slope,
                        'intercept': intercept,
                        'start_index': x1,
                        'end_index': len(df) - 1,
                        'touches': touches,
                        'strength': self._calculate_line_strength(df, slope, intercept, 'support'),
                        'touch_points': self._get_touch_indices(df, slope, intercept, 'low')
                    })

        return support_lines

    def _detect_resistance_lines(self, df):
        """Detect resistance trend lines connecting significant highs"""
        resistance_lines = []

        # Find local maxima (significant highs)
        highs = self._find_significant_highs(df)

        # Try all combinations of highs to form trend lines
        for i in range(len(highs)):
            for j in range(i + 1, len(highs)):
                point1 = highs[i]
                point2 = highs[j]

                # Calculate line parameters
                x1, y1 = point1['index'], point1['price']
                x2, y2 = point2['index'], point2['price']

                if x2 == x1:  # Avoid division by zero
                    continue

                slope = (y2 - y1) / (x2 - x1)
                intercept = y1 - slope * x1

                # Check if slope angle is reasonable
                angle = np.degrees(np.arctan(slope))
                if abs(angle) > self.max_slope_angle:
                    continue

                # Count touches and validate line
                touches = self._count_line_touches(
                    df, slope, intercept, 'high')
                if touches >= self.min_touches:
                    resistance_lines.append({
                        'type': 'resistance',
                        'slope': slope,
                        'intercept': intercept,
                        'start_index': x1,
                        'end_index': len(df) - 1,
                        'touches': touches,
                        'strength': self._calculate_line_strength(df, slope, intercept, 'resistance'),
                        'touch_points': self._get_touch_indices(df, slope, intercept, 'high')
                    })

        return resistance_lines

    def _find_significant_lows(self, df, window=5):
        """Find significant low points in the data"""
        lows = []

        for i in range(window, len(df) - window):
            current_low = df.iloc[i]['low']

            # Check if this is a local minimum
            is_local_min = True
            for j in range(i - window, i + window + 1):
                if j != i and df.iloc[j]['low'] <= current_low:
                    is_local_min = False
                    break

            if is_local_min:
                lows.append({
                    'index': i,
                    'price': current_low,
                    'timestamp': df.iloc[i]['timestamp']
                })

        return lows

    def _find_significant_highs(self, df, window=5):
        """Find significant high points in the data"""
        highs = []

        for i in range(window, len(df) - window):
            current_high = df.iloc[i]['high']

            # Check if this is a local maximum
            is_local_max = True
            for j in range(i - window, i + window + 1):
                if j != i and df.iloc[j]['high'] >= current_high:
                    is_local_max = False
                    break

            if is_local_max:
                highs.append({
                    'index': i,
                    'price': current_high,
                    'timestamp': df.iloc[i]['timestamp']
                })

        return highs

    def _count_line_touches(self, df, slope, intercept, price_type):
        """Count how many times price touches the trend line"""
        touches = 0
        tolerance = self.tolerance_percentage / 100

        for i in range(len(df)):
            line_price = slope * i + intercept
            actual_price = df.iloc[i][price_type]

            # Calculate percentage difference
            if line_price > 0:
                diff_percentage = abs(actual_price - line_price) / line_price
                if diff_percentage <= tolerance:
                    touches += 1

        return touches

    def _get_touch_indices(self, df, slope, intercept, price_type):
        """Get indices where price touches the trend line"""
        touch_indices = []
        tolerance = self.tolerance_percentage / 100

        for i in range(len(df)):
            line_price = slope * i + intercept
            actual_price = df.iloc[i][price_type]

            # Calculate percentage difference
            if line_price > 0:
                diff_percentage = abs(actual_price - line_price) / line_price
                if diff_percentage <= tolerance:
                    touch_indices.append(i)

        return touch_indices

    def _calculate_line_strength(self, df, slope, intercept, line_type):
        """Calculate the strength/quality of a trend line"""
        touches = self._count_line_touches(
            df, slope, intercept, 'low' if line_type == 'support' else 'high')

        # Factor in number of touches and line length
        line_length = len(df)
        strength = touches * 0.4 + (line_length / 100) * 0.3

        # Bonus for lines that haven't been broken recently
        recent_data = df.tail(20)
        broken = False
        for i in range(len(recent_data)):
            line_price = slope * (len(df) - 20 + i) + intercept
            if line_type == 'support' and recent_data.iloc[i]['low'] < line_price * 0.99:
                broken = True
                break
            elif line_type == 'resistance' and recent_data.iloc[i]['high'] > line_price * 1.01:
                broken = True
                break

        if not broken:
            strength += 0.5

        return strength

    def _filter_best_lines(self, trend_lines, max_lines=8):
        """Filter and return the best trend lines"""
        # Sort by strength
        trend_lines.sort(key=lambda x: x['strength'], reverse=True)

        # Remove duplicate/similar lines
        filtered_lines = []
        for line in trend_lines:
            is_duplicate = False
            for existing_line in filtered_lines:
                # Check if slopes are similar (within 10%)
                slope_diff = abs(line['slope'] - existing_line['slope'])
                if slope_diff < abs(line['slope']) * 0.1:
                    is_duplicate = True
                    break

            if not is_duplicate:
                filtered_lines.append(line)

            if len(filtered_lines) >= max_lines:
                break

        return filtered_lines


def create_advanced_chart(symbol="BTC/USDT", timeframe="1h"):
    """Create an advanced chart with precise trend lines"""

    print(f"Creating advanced chart for {symbol} ({timeframe})...")

    # Initialize detectors
    detector = OrderBlockDetector()
    trend_detector = AdvancedTrendLineDetector()

    # Get data
    print("Fetching market data...")
    df = detector.fetch_ohlcv_data(symbol, timeframe, limit=500)

    if df is None or len(df) == 0:
        print("Failed to get data, generating sample data...")
        df = detector.generate_sample_data(symbol)

    if df is None or len(df) == 0:
        print("Failed to generate any data")
        return None

    print(f"Got {len(df)} candles")

    # Detect swing points and order blocks
    print("Detecting swing points and order blocks...")
    df = detector.find_swing_highs_lows(df)
    df = detector.detect_order_blocks(df)

    # Detect advanced trend lines
    print("Detecting precise trend lines...")
    trend_lines = trend_detector.detect_precise_trend_lines(df)

    print(f"Found {len(trend_lines)} high-quality trend lines")

    # Create the chart with enhanced trend lines
    fig = detector.create_chart(df, symbol)

    # Add advanced trend lines
    for i, trend_line in enumerate(trend_lines):
        start_idx = max(0, trend_line['start_index'])
        end_idx = min(trend_line['end_index'], len(df) - 1)

        start_price = trend_line['slope'] * start_idx + trend_line['intercept']
        end_price = trend_line['slope'] * end_idx + trend_line['intercept']

        start_timestamp = df.iloc[start_idx]['timestamp']
        end_timestamp = df.iloc[end_idx]['timestamp']

        # Color based on type and strength
        if trend_line['type'] == 'resistance':
            # Gold
            line_color = f"rgba(255, 215, 0, {min(0.9, 0.4 + trend_line['strength'] * 0.1)})"
        else:
            # Deep Sky Blue
            line_color = f"rgba(0, 191, 255, {min(0.9, 0.4 + trend_line['strength'] * 0.1)})"

        # Add trend line
        fig.add_trace(
            go.Scatter(
                x=[start_timestamp, end_timestamp],
                y=[start_price, end_price],
                mode='lines',
                line=dict(
                    color=line_color,
                    width=2 + int(trend_line['strength']),
                    dash='solid'
                ),
                name=f"{trend_line['type'].title()} ({trend_line['touches']} touches)",
                showlegend=True,
                hovertemplate=f"<b>{trend_line['type'].title()} Line</b><br>" +
                f"Touches: {trend_line['touches']}<br>" +
                f"Strength: {trend_line['strength']:.2f}<br>" +
                f"Price: $%{{y:.2f}}<extra></extra>"
            ),
            row=1, col=1
        )

        # Add touch points
        if trend_line['touch_points']:
            # Show max 6 touch points
            touch_indices = trend_line['touch_points'][:6]
            touch_timestamps = [df.iloc[idx]['timestamp']
                                for idx in touch_indices if idx < len(df)]
            touch_prices = [trend_line['slope'] * idx + trend_line['intercept']
                            for idx in touch_indices if idx < len(df)]

            if touch_timestamps and touch_prices:
                fig.add_trace(
                    go.Scatter(
                        x=touch_timestamps,
                        y=touch_prices,
                        mode='markers',
                        marker=dict(
                            color=line_color,
                            size=6 + int(trend_line['strength']),
                            symbol='circle',
                            line=dict(color='white', width=1)
                        ),
                        name=f"{trend_line['type'].title()} Touches",
                        showlegend=False,
                        hovertemplate=f"<b>Touch Point</b><br>Price: $%{{y:.2f}}<extra></extra>"
                    ),
                    row=1, col=1
                )

    # Create HTML file
    chart_html = f"""
<!DOCTYPE html>
<html>
<head>
    <title>{symbol} - Advanced Chart Analysis</title>
    <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
    <style>
        body {{
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #0d1421;
            color: white;
        }}
        .header {{
            text-align: center;
            margin-bottom: 20px;
        }}
        .stats {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin-bottom: 20px;
        }}
        .stat-card {{
            background: rgba(255,255,255,0.1);
            padding: 15px;
            border-radius: 10px;
            border: 1px solid rgba(255,255,255,0.2);
        }}
        .chart-container {{
            height: 850px;
            background: rgba(255,255,255,0.05);
            border-radius: 15px;
            padding: 15px;
            border: 1px solid rgba(255,255,255,0.1);
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>{symbol} Advanced Chart Analysis</h1>
        <p>Timeframe: {timeframe} | Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
    </div>
    
    <div class="stats">
        <div class="stat-card">
            <h4>Chart Data</h4>
            <p>Total Candles: {len(df)}</p>
            <p>Swing Highs: {len(df[df['swing_high']])}</p>
            <p>Swing Lows: {len(df[df['swing_low']])}</p>
        </div>
        <div class="stat-card">
            <h4>Order Blocks</h4>
            <p>Bullish OBs: {len(df[df['bullish_ob']])}</p>
            <p>Bearish OBs: {len(df[df['bearish_ob']])}</p>
        </div>
        <div class="stat-card">
            <h4>Trend Lines</h4>
            <p>Total Lines: {len(trend_lines)}</p>
            <p>Support: {len([tl for tl in trend_lines if tl['type'] == 'support'])}</p>
            <p>Resistance: {len([tl for tl in trend_lines if tl['type'] == 'resistance'])}</p>
        </div>
        <div class="stat-card">
            <h4>Current Price</h4>
            <p>${df['close'].iloc[-1]:.2f}</p>
            <p>24h Change: {((df['close'].iloc[-1] / df['close'].iloc[-24] - 1) * 100 if len(df) >= 24 else 0):.2f}%</p>
        </div>
    </div>
    
    <div class="chart-container">
        <div id="chartDiv" style="height: 100%;"></div>
    </div>
    
    <script>
        var chartData = {fig.to_json()};
        
        var config = {{
            displayModeBar: true,
            displaylogo: false,
            modeBarButtonsToRemove: ['pan2d', 'lasso2d', 'select2d'],
            responsive: true,
            toImageButtonOptions: {{
                format: 'png',
                filename: '{symbol}_chart',
                height: 800,
                width: 1200,
                scale: 1
            }}
        }};
        
        Plotly.newPlot('chartDiv', chartData.data, chartData.layout, config);
        console.log("Advanced chart loaded successfully!");
    </script>
</body>
</html>
"""

    # Save to file
    temp_file = tempfile.NamedTemporaryFile(
        mode='w', suffix='.html', delete=False, encoding='utf-8')
    temp_file.write(chart_html)
    temp_file.close()

    return temp_file.name


def main():
    """Main function"""
    print("=" * 60)
    print("ADVANCED CRYPTO CHART VIEWER")
    print("=" * 60)

    symbols = ["BTC/USDT"]  # Focus on one symbol for detailed analysis

    for symbol in symbols:
        try:
            chart_file = create_advanced_chart(symbol, "1h")
            if chart_file:
                print(f"Advanced chart created: {chart_file}")
                print(f"Opening {symbol} chart in browser...")
                webbrowser.open(f"file://{chart_file}")
            else:
                print(f"Failed to create chart for {symbol}")

        except Exception as e:
            print(f"Error creating chart for {symbol}: {e}")

    print("\n" + "=" * 60)
    print("ADVANCED CHART ANALYSIS COMPLETED")
    print("=" * 60)


if __name__ == "__main__":
    main()
