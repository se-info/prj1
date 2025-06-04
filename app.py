from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import ccxt
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly
import json
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
CORS(app)


class OrderBlockDetector:
    def __init__(self):
        self.exchange = ccxt.binance()

    def fetch_ohlcv_data(self, symbol, timeframe='1h', limit=500):
        """Fetch OHLCV data from Binance"""
        try:
            ohlcv = self.exchange.fetch_ohlcv(symbol, timeframe, limit=limit)
            df = pd.DataFrame(
                ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            return df
        except Exception as e:
            print(f"Error fetching data: {e}")
            return None

    def find_swing_highs_lows(self, df, period=5):
        """Identify swing highs and lows for BOS detection"""
        df = df.copy()
        df['swing_high'] = False
        df['swing_low'] = False

        for i in range(period, len(df) - period):
            # Check for swing high
            if all(df.iloc[i]['high'] >= df.iloc[j]['high'] for j in range(i-period, i+period+1) if j != i):
                df.iloc[i, df.columns.get_loc('swing_high')] = True

            # Check for swing low
            if all(df.iloc[i]['low'] <= df.iloc[j]['low'] for j in range(i-period, i+period+1) if j != i):
                df.iloc[i, df.columns.get_loc('swing_low')] = True

        return df

    def detect_break_of_structure(self, df, min_move_percentage=2.0):
        """Detect Break of Structure (BOS)"""
        df = df.copy()
        df['bullish_bos'] = False
        df['bearish_bos'] = False

        swing_highs = df[df['swing_high']].copy()
        swing_lows = df[df['swing_low']].copy()

        for i, row in df.iterrows():
            if i < 10:  # Need some history
                continue

            # Check for bullish BOS (break above recent swing high)
            recent_swing_highs = swing_highs[swing_highs.index < i].tail(3)
            if not recent_swing_highs.empty:
                highest_swing = recent_swing_highs['high'].max()
                if row['close'] > highest_swing:
                    move_percentage = (
                        (row['close'] - highest_swing) / highest_swing) * 100
                    if move_percentage >= min_move_percentage:
                        df.iloc[i, df.columns.get_loc('bullish_bos')] = True

            # Check for bearish BOS (break below recent swing low)
            recent_swing_lows = swing_lows[swing_lows.index < i].tail(3)
            if not recent_swing_lows.empty:
                lowest_swing = recent_swing_lows['low'].min()
                if row['close'] < lowest_swing:
                    move_percentage = (
                        (lowest_swing - row['close']) / lowest_swing) * 100
                    if move_percentage >= min_move_percentage:
                        df.iloc[i, df.columns.get_loc('bearish_bos')] = True

        return df

    def detect_order_blocks(self, df, lookback_period=20):
        """Detect Order Blocks based on BOS and candle patterns"""
        df = df.copy()
        df['bullish_ob'] = False
        df['bearish_ob'] = False
        df['ob_high'] = np.nan
        df['ob_low'] = np.nan

        for i, row in df.iterrows():
            if i < lookback_period:
                continue

            # Detect Bullish Order Block
            if row['bullish_bos']:
                # Look back for the last bearish candle before this bullish move
                lookback_data = df.iloc[max(0, i-lookback_period):i]
                bearish_candles = lookback_data[lookback_data['close']
                                                < lookback_data['open']]

                if not bearish_candles.empty:
                    # Get the most recent bearish candle
                    last_bearish_idx = bearish_candles.index[-1]
                    last_bearish = df.iloc[last_bearish_idx]

                    # Mark as bullish OB if it's followed by significant upward movement
                    subsequent_data = df.iloc[last_bearish_idx:i+1]
                    if len(subsequent_data) > 1:
                        price_move = (
                            row['high'] - last_bearish['low']) / last_bearish['low'] * 100
                        if price_move >= 1.5:  # At least 1.5% move
                            df.iloc[last_bearish_idx,
                                    df.columns.get_loc('bullish_ob')] = True
                            df.iloc[last_bearish_idx, df.columns.get_loc(
                                'ob_high')] = last_bearish['high']
                            df.iloc[last_bearish_idx, df.columns.get_loc(
                                'ob_low')] = last_bearish['low']

            # Detect Bearish Order Block
            if row['bearish_bos']:
                # Look back for the last bullish candle before this bearish move
                lookback_data = df.iloc[max(0, i-lookback_period):i]
                bullish_candles = lookback_data[lookback_data['close']
                                                > lookback_data['open']]

                if not bullish_candles.empty:
                    # Get the most recent bullish candle
                    last_bullish_idx = bullish_candles.index[-1]
                    last_bullish = df.iloc[last_bullish_idx]

                    # Mark as bearish OB if it's followed by significant downward movement
                    subsequent_data = df.iloc[last_bullish_idx:i+1]
                    if len(subsequent_data) > 1:
                        price_move = (
                            last_bullish['high'] - row['low']) / last_bullish['high'] * 100
                        if price_move >= 1.5:  # At least 1.5% move
                            df.iloc[last_bullish_idx,
                                    df.columns.get_loc('bearish_ob')] = True
                            df.iloc[last_bullish_idx, df.columns.get_loc(
                                'ob_high')] = last_bullish['high']
                            df.iloc[last_bullish_idx, df.columns.get_loc(
                                'ob_low')] = last_bullish['low']

        return df

    def create_chart(self, df, symbol):
        """Create interactive Plotly chart with Order Blocks"""
        fig = make_subplots(
            rows=2, cols=1,
            shared_xaxes=True,
            vertical_spacing=0.03,
            subplot_titles=(
                f'{symbol} Price Chart with Order Blocks', 'Volume'),
            row_width=[0.7, 0.3]
        )

        # Candlestick chart
        fig.add_trace(
            go.Candlestick(
                x=df['timestamp'],
                open=df['open'],
                high=df['high'],
                low=df['low'],
                close=df['close'],
                name='Price',
                increasing_line_color='#00ff00',
                decreasing_line_color='#ff0000'
            ),
            row=1, col=1
        )

        # Add Order Blocks
        bullish_obs = df[df['bullish_ob']]
        bearish_obs = df[df['bearish_ob']]

        # Bullish Order Blocks (green rectangles)
        for idx, ob in bullish_obs.iterrows():
            fig.add_shape(
                type="rect",
                x0=ob['timestamp'],
                y0=ob['ob_low'],
                # Extend 20 candles forward
                x1=df.iloc[min(idx + 20, len(df) - 1)]['timestamp'],
                y1=ob['ob_high'],
                line=dict(color="rgba(0, 255, 0, 0.3)"),
                fillcolor="rgba(0, 255, 0, 0.2)",
                row=1, col=1
            )

        # Bearish Order Blocks (red rectangles)
        for idx, ob in bearish_obs.iterrows():
            fig.add_shape(
                type="rect",
                x0=ob['timestamp'],
                y0=ob['ob_low'],
                # Extend 20 candles forward
                x1=df.iloc[min(idx + 20, len(df) - 1)]['timestamp'],
                y1=ob['ob_high'],
                line=dict(color="rgba(255, 0, 0, 0.3)"),
                fillcolor="rgba(255, 0, 0, 0.2)",
                row=1, col=1
            )

        # Add BOS markers
        bullish_bos = df[df['bullish_bos']]
        bearish_bos = df[df['bearish_bos']]

        fig.add_trace(
            go.Scatter(
                x=bullish_bos['timestamp'],
                y=bullish_bos['high'],
                mode='markers',
                marker=dict(color='green', size=10, symbol='triangle-up'),
                name='Bullish BOS',
                showlegend=True
            ),
            row=1, col=1
        )

        fig.add_trace(
            go.Scatter(
                x=bearish_bos['timestamp'],
                y=bearish_bos['low'],
                mode='markers',
                marker=dict(color='red', size=10, symbol='triangle-down'),
                name='Bearish BOS',
                showlegend=True
            ),
            row=1, col=1
        )

        # Volume chart
        fig.add_trace(
            go.Bar(
                x=df['timestamp'],
                y=df['volume'],
                name='Volume',
                marker_color='rgba(0, 150, 255, 0.6)'
            ),
            row=2, col=1
        )

        fig.update_layout(
            title=f'{symbol} Order Block Analysis',
            xaxis_rangeslider_visible=False,
            height=800,
            showlegend=True,
            template='plotly_dark'
        )

        return fig


detector = OrderBlockDetector()


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/api/analyze', methods=['POST'])
def analyze():
    try:
        data = request.get_json()
        symbol = data.get('symbol', 'BTC/USDT')
        timeframe = data.get('timeframe', '1h')

        # Fetch data
        df = detector.fetch_ohlcv_data(symbol, timeframe)
        if df is None:
            return jsonify({'error': 'Failed to fetch data'}), 500

        # Process data
        df = detector.find_swing_highs_lows(df)
        df = detector.detect_break_of_structure(df)
        df = detector.detect_order_blocks(df)

        # Create chart
        fig = detector.create_chart(df, symbol)

        # Convert to JSON
        chart_json = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

        # Get statistics
        bullish_obs = len(df[df['bullish_ob']])
        bearish_obs = len(df[df['bearish_ob']])
        bullish_bos = len(df[df['bullish_bos']])
        bearish_bos = len(df[df['bearish_bos']])

        return jsonify({
            'chart': chart_json,
            'stats': {
                'bullish_obs': bullish_obs,
                'bearish_obs': bearish_obs,
                'bullish_bos': bullish_bos,
                'bearish_bos': bearish_bos,
                'total_candles': len(df)
            }
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/symbols')
def get_symbols():
    """Get available trading symbols"""
    try:
        markets = detector.exchange.load_markets()
        symbols = [symbol for symbol in markets.keys() if '/USDT' in symbol]
        symbols = sorted(symbols[:50])  # Limit to top 50 for performance
        return jsonify({'symbols': symbols})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
