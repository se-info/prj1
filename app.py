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
import csv
import logging
from datetime import datetime

load_dotenv()

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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

    def generate_trading_signals(self, df):
        """Generate trading signals based on Order Blocks"""
        signals = []
        current_price = df['close'].iloc[-1]

        # Lấy các Order Blocks gần đây (trong 50 candles cuối)
        recent_data = df.tail(50)

        # Bullish Order Blocks (Long signals)
        bullish_obs = recent_data[recent_data['bullish_ob']]
        for idx, ob in bullish_obs.iterrows():
            if not pd.isna(ob['ob_high']) and not pd.isna(ob['ob_low']):
                # Entry: khi giá retest về vùng OB
                entry_zone_high = ob['ob_high']
                entry_zone_low = ob['ob_low']
                entry_price = (entry_zone_high + entry_zone_low) / 2

                # Stop Loss: dưới OB low
                stop_loss = entry_zone_low * 0.995  # 0.5% buffer

                # Take Profit: 1:2 Risk/Reward ratio
                risk = entry_price - stop_loss
                take_profit = entry_price + (risk * 2)

                # Risk/Reward calculation
                risk_percentage = (
                    (entry_price - stop_loss) / entry_price) * 100
                reward_percentage = (
                    (take_profit - entry_price) / entry_price) * 100

                signal = {
                    'type': 'LONG',
                    'entry_price': round(entry_price, 2),
                    'entry_zone_high': round(entry_zone_high, 2),
                    'entry_zone_low': round(entry_zone_low, 2),
                    'stop_loss': round(stop_loss, 2),
                    'take_profit': round(take_profit, 2),
                    'risk_percentage': round(risk_percentage, 2),
                    'reward_percentage': round(reward_percentage, 2),
                    'rr_ratio': '1:2',
                    'timestamp': ob['timestamp'],
                    'status': 'ACTIVE' if current_price <= entry_zone_high * 1.02 else 'MISSED',
                    'description': f'Long từ Bullish OB tại {entry_price}'
                }
                signals.append(signal)

        # Bearish Order Blocks (Short signals)
        bearish_obs = recent_data[recent_data['bearish_ob']]
        for idx, ob in bearish_obs.iterrows():
            if not pd.isna(ob['ob_high']) and not pd.isna(ob['ob_low']):
                # Entry: khi giá retest về vùng OB
                entry_zone_high = ob['ob_high']
                entry_zone_low = ob['ob_low']
                entry_price = (entry_zone_high + entry_zone_low) / 2

                # Stop Loss: trên OB high
                stop_loss = entry_zone_high * 1.005  # 0.5% buffer

                # Take Profit: 1:2 Risk/Reward ratio
                risk = stop_loss - entry_price
                take_profit = entry_price - (risk * 2)

                # Risk/Reward calculation
                risk_percentage = (
                    (stop_loss - entry_price) / entry_price) * 100
                reward_percentage = (
                    (entry_price - take_profit) / entry_price) * 100

                signal = {
                    'type': 'SHORT',
                    'entry_price': round(entry_price, 2),
                    'entry_zone_high': round(entry_zone_high, 2),
                    'entry_zone_low': round(entry_zone_low, 2),
                    'stop_loss': round(stop_loss, 2),
                    'take_profit': round(take_profit, 2),
                    'risk_percentage': round(risk_percentage, 2),
                    'reward_percentage': round(reward_percentage, 2),
                    'rr_ratio': '1:2',
                    'timestamp': ob['timestamp'],
                    'status': 'ACTIVE' if current_price >= entry_zone_low * 0.98 else 'MISSED',
                    'description': f'Short từ Bearish OB tại {entry_price}'
                }
                signals.append(signal)

        return signals

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

        # Enhanced chart layout with free scrolling/zooming
        fig.update_layout(
            title=f'{symbol} Order Block Analysis',
            xaxis_rangeslider_visible=False,
            height=800,
            showlegend=True,
            template='plotly_dark',
            # Enable free drag mode for panning
            dragmode='pan',
            # Better selection options
            selectdirection='any',
            # Configure additional interaction settings
            hovermode='closest',
            # Add margin for better viewing
            margin=dict(l=50, r=50, t=80, b=50)
        )

        # Configure X-axis for better interaction
        fig.update_xaxes(
            rangeslider_visible=False,
            # Enable zooming and panning
            showspikes=True,
            spikemode='across',
            spikesnap='cursor',
            spikedash='solid',
            spikecolor='#999999',
            spikethickness=1
        )

        # Configure Y-axis for better interaction
        fig.update_yaxes(
            showspikes=True,
            spikemode='across',
            spikesnap='cursor',
            spikedash='solid',
            spikecolor='#999999',
            spikethickness=1
        )

        return fig


detector = OrderBlockDetector()


class UserLogger:
    def __init__(self, log_file='user_activity_log.csv'):
        self.log_file = log_file
        self.init_log_file()

    def init_log_file(self):
        """Initialize CSV log file with headers if it doesn't exist"""
        try:
            if not os.path.exists(self.log_file):
                with open(self.log_file, 'w', newline='', encoding='utf-8') as file:
                    writer = csv.writer(file)
                    writer.writerow([
                        'timestamp', 'username', 'action', 'symbol',
                        'timeframe', 'details', 'ip_address', 'session_id'
                    ])
                logger.info(f"Created new log file: {self.log_file}")
        except Exception as e:
            logger.error(f"Error initializing log file: {e}")

    def log_activity(self, username, action, symbol=None, timeframe=None,
                     details=None, ip_address=None, session_id=None):
        """Log user activity to CSV file"""
        try:
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

            with open(self.log_file, 'a', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                writer.writerow([
                    timestamp, username, action, symbol or '',
                    timeframe or '', details or '', ip_address or '', session_id or ''
                ])

            logger.info(f"Logged activity: {username} - {action}")
            return True
        except Exception as e:
            logger.error(f"Error logging activity: {e}")
            return False

    def get_user_stats(self, username):
        """Get usage statistics for a specific user"""
        try:
            stats = {
                'total_sessions': 0,
                'total_analyses': 0,
                'favorite_symbols': {},
                'favorite_timeframes': {},
                'last_activity': None,
                'first_activity': None
            }

            if not os.path.exists(self.log_file):
                return stats

            with open(self.log_file, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    if row['username'].lower() == username.lower():
                        # Count activities
                        if row['action'] == 'LOGIN':
                            stats['total_sessions'] += 1
                        elif row['action'] == 'ANALYZE':
                            stats['total_analyses'] += 1

                            # Track favorite symbols
                            symbol = row['symbol']
                            if symbol:
                                stats['favorite_symbols'][symbol] = stats['favorite_symbols'].get(
                                    symbol, 0) + 1

                            # Track favorite timeframes
                            timeframe = row['timeframe']
                            if timeframe:
                                stats['favorite_timeframes'][timeframe] = stats['favorite_timeframes'].get(
                                    timeframe, 0) + 1

                        # Track activity dates
                        activity_date = row['timestamp']
                        if not stats['first_activity']:
                            stats['first_activity'] = activity_date
                        stats['last_activity'] = activity_date

            return stats
        except Exception as e:
            logger.error(f"Error getting user stats: {e}")
            return {}


user_logger = UserLogger()


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/api/login', methods=['POST'])
def login_user():
    """Log user login activity"""
    try:
        data = request.get_json()
        username = data.get('username', '').strip()

        if not username:
            return jsonify({'error': 'Username is required'}), 400

        # Log login activity
        user_logger.log_activity(
            username=username,
            action='LOGIN',
            details='User logged in',
            ip_address=request.remote_addr
        )

        # Get user stats
        stats = user_logger.get_user_stats(username)

        return jsonify({
            'success': True,
            'message': f'Welcome back {username}!',
            'user_stats': stats
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/user_stats/<username>')
def get_user_stats(username):
    """Get user statistics"""
    try:
        stats = user_logger.get_user_stats(username)
        return jsonify({'user_stats': stats})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/analyze', methods=['POST'])
def analyze():
    try:
        data = request.get_json()
        symbol = data.get('symbol', 'BTC/USDT')
        timeframe = data.get('timeframe', '1h')
        username = data.get('username', 'Anonymous')

        # Log analysis activity
        user_logger.log_activity(
            username=username,
            action='ANALYZE',
            symbol=symbol,
            timeframe=timeframe,
            details=f'Analyzed {symbol} on {timeframe} timeframe',
            ip_address=request.remote_addr
        )

        # Fetch data
        df = detector.fetch_ohlcv_data(symbol, timeframe)
        if df is None:
            return jsonify({'error': 'Failed to fetch data'}), 500

        # Process data
        df = detector.find_swing_highs_lows(df)
        df = detector.detect_break_of_structure(df)
        df = detector.detect_order_blocks(df)

        # Generate trading signals
        trading_signals = detector.generate_trading_signals(df)

        # Create chart
        fig = detector.create_chart(df, symbol)

        # Convert to JSON
        chart_json = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

        # Get statistics
        bullish_obs = len(df[df['bullish_ob']])
        bearish_obs = len(df[df['bearish_ob']])
        bullish_bos = len(df[df['bullish_bos']])
        bearish_bos = len(df[df['bearish_bos']])

        # Current price info
        current_price = df['close'].iloc[-1]
        price_change = (
            (current_price - df['open'].iloc[0]) / df['open'].iloc[0]) * 100

        return jsonify({
            'chart': chart_json,
            'stats': {
                'bullish_obs': bullish_obs,
                'bearish_obs': bearish_obs,
                'bullish_bos': bullish_bos,
                'bearish_bos': bearish_bos,
                'total_candles': len(df),
                'current_price': round(current_price, 2),
                'price_change': round(price_change, 2)
            },
            'trading_signals': trading_signals
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


@app.route('/api/logs/<username>')
def get_user_logs(username):
    """Get recent logs for a specific user"""
    try:
        logs = []
        limit = request.args.get('limit', 20, type=int)

        if os.path.exists(user_logger.log_file):
            with open(user_logger.log_file, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    if row['username'].lower() == username.lower():
                        logs.append(row)

        # Return most recent logs first
        logs = logs[-limit:] if len(logs) > limit else logs
        logs.reverse()

        return jsonify({'logs': logs})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
