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
from scipy import stats
from sklearn.linear_model import LinearRegression

load_dotenv()

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)


class OrderBlockDetector:
    def __init__(self):
        self.exchange = None
        self.init_exchange()

    def init_exchange(self):
        """Initialize exchange with better error handling"""
        try:
            self.exchange = ccxt.binance({
                'apiKey': '',  # Not needed for public data
                'secret': '',  # Not needed for public data
                'timeout': 20000,  # 20 seconds timeout
                'enableRateLimit': True,
                'options': {
                    'defaultType': 'spot'  # Use spot market
                }
            })

            # Test connection
            self.exchange.load_markets()
            logger.info("Binance exchange initialized successfully")

        except Exception as e:
            logger.error(f"Failed to initialize Binance exchange: {e}")
            # Try alternative exchange or fallback
            try:
                self.exchange = ccxt.binance({
                    'sandbox': False,
                    'timeout': 30000,
                    'enableRateLimit': True,
                    'rateLimit': 1200,
                    'options': {
                        'defaultType': 'spot'
                    }
                })
                logger.info(
                    "Binance exchange initialized with fallback settings")
            except Exception as e2:
                logger.error(f"Fallback exchange initialization failed: {e2}")
                self.exchange = None

    def fetch_ohlcv_data(self, symbol, timeframe='1h', limit=500):
        """Fetch OHLCV data from Binance with improved error handling"""
        max_retries = 3
        retry_count = 0

        while retry_count < max_retries:
            try:
                # Reinitialize exchange if needed
                if self.exchange is None:
                    self.init_exchange()
                    if self.exchange is None:
                        raise Exception("Exchange initialization failed")

                # Ensure markets are loaded
                if not hasattr(self.exchange, 'markets') or not self.exchange.markets:
                    self.exchange.load_markets()

                # Fetch OHLCV data
                logger.info(
                    f"Fetching {symbol} data for {timeframe} timeframe")
                ohlcv = self.exchange.fetch_ohlcv(
                    symbol, timeframe, limit=limit)

                if not ohlcv or len(ohlcv) == 0:
                    raise Exception("No data received from exchange")

                df = pd.DataFrame(
                    ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
                df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')

                logger.info(
                    f"Successfully fetched {len(df)} candles for {symbol}")
                return df

            except Exception as e:
                retry_count += 1
                logger.error(
                    f"Attempt {retry_count}/{max_retries} failed: {e}")

                if retry_count < max_retries:
                    logger.info("Retrying with fresh exchange connection...")
                    self.exchange = None  # Force reinitialize
                    import time
                    time.sleep(2)  # Wait before retry
                else:
                    logger.error(f"All retry attempts failed for {symbol}")
                    return self.generate_sample_data(symbol)

        return None

    def generate_sample_data(self, symbol):
        """Generate sample data when API fails"""
        logger.info(f"Generating sample data for {symbol}")
        try:
            import random
            from datetime import datetime, timedelta

            # Generate 500 sample candles
            current_time = datetime.now()
            base_price = 50000 if 'BTC' in symbol else 3000 if 'ETH' in symbol else 500

            data = []
            for i in range(500):
                timestamp = current_time - timedelta(hours=500-i)

                # Simulate price movement
                change = random.uniform(-0.02, 0.02)  # ±2% change
                base_price *= (1 + change)

                high = base_price * random.uniform(1.001, 1.01)
                low = base_price * random.uniform(0.99, 0.999)
                open_price = base_price * random.uniform(0.995, 1.005)
                close_price = base_price
                volume = random.uniform(100, 1000)

                data.append([
                    timestamp,
                    open_price,
                    high,
                    low,
                    close_price,
                    volume
                ])

            df = pd.DataFrame(
                data, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
            logger.info(f"Generated {len(df)} sample candles for {symbol}")
            return df

        except Exception as e:
            logger.error(f"Failed to generate sample data: {e}")
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

    def detect_trend_lines(self, df, min_touches=3):
        """Detect trend lines based on swing highs and lows"""
        trend_lines = []

        # Get swing points
        swing_highs = df[df['swing_high']].copy()
        swing_lows = df[df['swing_low']].copy()

        # Detect resistance lines (connecting swing highs)
        if len(swing_highs) >= min_touches:
            trend_lines.extend(self._find_trend_line_combinations(
                swing_highs, 'high', 'resistance', min_touches))

        # Detect support lines (connecting swing lows)
        if len(swing_lows) >= min_touches:
            trend_lines.extend(self._find_trend_line_combinations(
                swing_lows, 'low', 'support', min_touches))

        return trend_lines

    def _find_trend_line_combinations(self, swing_points, price_col, line_type, min_touches):
        """Find all possible trend line combinations"""
        trend_lines = []
        points = swing_points.reset_index()

        # Try all combinations of points
        for i in range(len(points)):
            for j in range(i + 1, len(points)):
                # Get two points to define the line
                point1 = points.iloc[i]
                point2 = points.iloc[j]

                # Calculate line parameters
                x1, y1 = point1['index'], point1[price_col]
                x2, y2 = point2['index'], point2[price_col]

                if x2 - x1 == 0:  # Avoid division by zero
                    continue

                slope = (y2 - y1) / (x2 - x1)
                intercept = y1 - slope * x1

                # Count how many points touch this line (within tolerance)
                touches = self._count_line_touches(
                    points, slope, intercept, price_col, tolerance=0.005)

                if touches >= min_touches:
                    # Calculate line strength based on number of touches and time span
                    time_span = x2 - x1
                    strength = touches * time_span / len(points)

                    trend_line = {
                        'type': line_type,
                        'slope': float(slope),
                        'intercept': float(intercept),
                        'start_index': int(x1),
                        'end_index': int(x2),
                        'start_timestamp': point1['timestamp'].isoformat() if hasattr(point1['timestamp'], 'isoformat') else str(point1['timestamp']),
                        'end_timestamp': point2['timestamp'].isoformat() if hasattr(point2['timestamp'], 'isoformat') else str(point2['timestamp']),
                        'start_price': float(y1),
                        'end_price': float(y2),
                        'touches': int(touches),
                        'strength': float(strength),
                        'touch_points': [int(tp) for tp in self._get_touch_points(points, slope, intercept, price_col)]
                    }
                    trend_lines.append(trend_line)

        # Filter out overlapping lines and keep the strongest ones
        trend_lines = self._filter_best_trend_lines(trend_lines)

        return trend_lines

    def _count_line_touches(self, points, slope, intercept, price_col, tolerance=0.005):
        """Count how many points touch the trend line within tolerance"""
        touches = 0
        for _, point in points.iterrows():
            expected_price = slope * point['index'] + intercept
            actual_price = point[price_col]

            # Calculate percentage difference
            if expected_price != 0:
                diff_percentage = abs(
                    actual_price - expected_price) / expected_price
                if diff_percentage <= tolerance:
                    touches += 1

        return touches

    def _get_touch_points(self, points, slope, intercept, price_col, tolerance=0.005):
        """Get indices of points that touch the trend line"""
        touch_points = []
        for _, point in points.iterrows():
            expected_price = slope * point['index'] + intercept
            actual_price = point[price_col]

            if expected_price != 0:
                diff_percentage = abs(
                    actual_price - expected_price) / expected_price
                if diff_percentage <= tolerance:
                    touch_points.append(point['index'])

        return touch_points

    def _filter_best_trend_lines(self, trend_lines, max_lines=5):
        """Filter to keep only the best trend lines"""
        if not trend_lines:
            return []

        # Sort by strength (descending)
        trend_lines.sort(key=lambda x: x['strength'], reverse=True)

        # Keep only the top lines, avoiding too much overlap
        filtered_lines = []
        for line in trend_lines:
            if len(filtered_lines) >= max_lines:
                break

            # Check if this line overlaps significantly with existing lines
            overlaps = False
            for existing_line in filtered_lines:
                if (line['type'] == existing_line['type'] and
                    abs(line['slope'] - existing_line['slope']) < 0.0001 and
                        abs(line['intercept'] - existing_line['intercept']) < line['start_price'] * 0.01):
                    overlaps = True
                    break

            if not overlaps:
                filtered_lines.append(line)

        return filtered_lines

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

        # First detect BOS if not already done
        if 'bullish_bos' not in df.columns or 'bearish_bos' not in df.columns:
            df = self.detect_break_of_structure(df)

        # Initialize order block columns
        df['bullish_ob'] = False
        df['bearish_ob'] = False
        df['ob_high'] = np.nan
        df['ob_low'] = np.nan

        for i, row in df.iterrows():
            if i < lookback_period:
                continue

            # Detect Bullish Order Block - check if column exists and value is True
            if 'bullish_bos' in df.columns and row.get('bullish_bos', False):
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

            # Detect Bearish Order Block - check if column exists and value is True
            if 'bearish_bos' in df.columns and row.get('bearish_bos', False):
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
                    'entry_price': float(round(entry_price, 2)),
                    'entry_zone_high': float(round(entry_zone_high, 2)),
                    'entry_zone_low': float(round(entry_zone_low, 2)),
                    'stop_loss': float(round(stop_loss, 2)),
                    'take_profit': float(round(take_profit, 2)),
                    'risk_percentage': float(round(risk_percentage, 2)),
                    'reward_percentage': float(round(reward_percentage, 2)),
                    'rr_ratio': '1:2',
                    'timestamp': ob['timestamp'].isoformat() if hasattr(ob['timestamp'], 'isoformat') else str(ob['timestamp']),
                    'status': 'ACTIVE' if current_price <= entry_zone_high * 1.02 else 'MISSED',
                    'description': f'Long từ Bullish OB tại {float(round(entry_price, 2))}'
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
                    'entry_price': float(round(entry_price, 2)),
                    'entry_zone_high': float(round(entry_zone_high, 2)),
                    'entry_zone_low': float(round(entry_zone_low, 2)),
                    'stop_loss': float(round(stop_loss, 2)),
                    'take_profit': float(round(take_profit, 2)),
                    'risk_percentage': float(round(risk_percentage, 2)),
                    'reward_percentage': float(round(reward_percentage, 2)),
                    'rr_ratio': '1:2',
                    'timestamp': ob['timestamp'].isoformat() if hasattr(ob['timestamp'], 'isoformat') else str(ob['timestamp']),
                    'status': 'ACTIVE' if current_price >= entry_zone_low * 0.98 else 'MISSED',
                    'description': f'Short từ Bearish OB tại {float(round(entry_price, 2))}'
                }
                signals.append(signal)

        return signals

    def create_chart(self, df, symbol, theme='dark'):
        """Create interactive Plotly chart with Order Blocks and Trend Lines"""
        fig = make_subplots(
            rows=2, cols=1,
            shared_xaxes=True,
            vertical_spacing=0.03,
            subplot_titles=(
                f'{symbol} Price Chart with Order Blocks & Trend Lines', 'Volume'),
            row_width=[0.7, 0.3]
        )

        # Candlestick chart - make sure it's prominent
        fig.add_trace(
            go.Candlestick(
                x=df['timestamp'],
                open=df['open'],
                high=df['high'],
                low=df['low'],
                close=df['close'],
                name='Price Candles',
                increasing_line_color='#26a69a',
                decreasing_line_color='#ef5350',
                increasing_fillcolor='#26a69a',
                decreasing_fillcolor='#ef5350',
                line=dict(width=1),
                opacity=0.9,
                showlegend=True
            ),
            row=1, col=1
        )

        # Detect and add trend lines
        trend_lines = self.detect_trend_lines(df)
        for trend_line in trend_lines:
            # Calculate start and end points for the line
            start_idx = int(trend_line['start_index'])
            # Extend line forward
            end_idx = min(int(trend_line['end_index']) + 50, len(df) - 1)

            start_price = trend_line['slope'] * \
                start_idx + trend_line['intercept']
            end_price = trend_line['slope'] * end_idx + trend_line['intercept']

            start_timestamp = df.iloc[start_idx]['timestamp']
            end_timestamp = df.iloc[end_idx]['timestamp']

            # Choose color based on trend line type
            # Gold for resistance, Deep Sky Blue for support
            line_color = '#FFD700' if trend_line['type'] == 'resistance' else '#00BFFF'

            fig.add_trace(
                go.Scatter(
                    x=[start_timestamp, end_timestamp],
                    y=[start_price, end_price],
                    mode='lines',
                    line=dict(
                        color=line_color,
                        width=2,
                        dash='dash'  # Make dashed so candlesticks are more visible
                    ),
                    opacity=0.8,  # Slightly transparent so candlesticks show through
                    name=f"{trend_line['type'].title()} Line ({trend_line['touches']} touches)",
                    showlegend=True,
                    hovertemplate=f"<b>{trend_line['type'].title()} Line</b><br>" +
                    f"Touches: {trend_line['touches']}<br>" +
                    f"Strength: {trend_line['strength']:.2f}<br>" +
                    f"Price: $%{{y:.2f}}<extra></extra>"
                ),
                row=1, col=1
            )

            # Add touch points markers
            # Show max 5 touch points
            touch_indices = trend_line['touch_points'][:5]
            if touch_indices:
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
                                size=8,
                                symbol='circle',
                                line=dict(color='white', width=1)
                            ),
                            name=f"{trend_line['type'].title()} Touch Points",
                            showlegend=False,
                            hovertemplate=f"<b>Touch Point</b><br>Price: $%{{y:.2f}}<extra></extra>"
                        ),
                        row=1, col=1
                    )

        # Add Order Blocks
        bullish_obs = df[df['bullish_ob']]
        bearish_obs = df[df['bearish_ob']]

        # Bullish Order Blocks (green rectangles) - behind candlesticks
        for idx, ob in bullish_obs.iterrows():
            fig.add_shape(
                type="rect",
                x0=ob['timestamp'],
                y0=ob['ob_low'],
                # Extend 20 candles forward
                x1=df.iloc[min(idx + 20, len(df) - 1)]['timestamp'],
                y1=ob['ob_high'],
                line=dict(color="rgba(0, 255, 0, 0.4)", width=1),
                fillcolor="rgba(0, 255, 0, 0.15)",
                layer="below",  # Draw behind candlesticks
                row=1, col=1
            )

        # Bearish Order Blocks (red rectangles) - behind candlesticks
        for idx, ob in bearish_obs.iterrows():
            fig.add_shape(
                type="rect",
                x0=ob['timestamp'],
                y0=ob['ob_low'],
                # Extend 20 candles forward
                x1=df.iloc[min(idx + 20, len(df) - 1)]['timestamp'],
                y1=ob['ob_high'],
                line=dict(color="rgba(255, 0, 0, 0.4)", width=1),
                fillcolor="rgba(255, 0, 0, 0.15)",
                layer="below",  # Draw behind candlesticks
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

<<<<<<< HEAD
        # Apply theme
        template = 'plotly_dark' if theme == 'dark' else 'plotly_white'

=======
        # Enhanced chart layout with free scrolling/zooming
>>>>>>> 2fae4d85f3ae6e749160bb59b550d1ee529e7b16
        fig.update_layout(
            title=f'{symbol} - Price Chart with Order Blocks & Trend Lines',
            xaxis_rangeslider_visible=False,
            height=800,
            showlegend=True,
<<<<<<< HEAD
            template=template,
            # Add crosshair cursor for price measurement
            hovermode='x unified',
            # Enable crossfilter for better interaction
            dragmode='zoom',
            # Ensure proper spacing and visibility
            margin=dict(l=50, r=50, t=80, b=50),
            # Make sure candlesticks are prominent
            xaxis=dict(
                title='Time',
                showgrid=True,
                gridcolor='rgba(128,128,128,0.2)'
            ),
            yaxis=dict(
                title='Price (USDT)',
                showgrid=True,
                gridcolor='rgba(128,128,128,0.2)',
                side='right'
            ),
            # Volume chart styling
            xaxis2=dict(
                title='Time',
                showgrid=True,
                gridcolor='rgba(128,128,128,0.2)'
            ),
            yaxis2=dict(
                title='Volume',
                showgrid=True,
                gridcolor='rgba(128,128,128,0.2)',
                side='right'
            )
        )

        # Update x-axis to show crosshair
        fig.update_xaxes(
            showspikes=True,
            spikecolor="orange",
            spikesnap="cursor",
            spikemode="across",
            spikethickness=1
        )

        # Update y-axis to show crosshair and price levels
        fig.update_yaxes(
            showspikes=True,
            spikecolor="orange",
            spikesnap="cursor",
            spikemode="across",
            spikethickness=1,
            row=1, col=1
=======
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
>>>>>>> 2fae4d85f3ae6e749160bb59b550d1ee529e7b16
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
        theme = data.get('theme', 'dark')  # Add theme parameter

        # Log analysis activity
        user_logger.log_activity(
            username=username,
            action='ANALYZE',
            symbol=symbol,
            timeframe=timeframe,
            details=f'Analyzed {symbol} on {timeframe} timeframe with {theme} theme',
            ip_address=request.remote_addr
        )

        # Fetch data
        df = detector.fetch_ohlcv_data(symbol, timeframe)
        if df is None:
            return jsonify({'error': 'Failed to fetch data and generate sample data'}), 500

        # Check if we used sample data (sample data will have predictable patterns)
        using_sample_data = len(
            df) == 500 and df['timestamp'].iloc[-1] > datetime.now() - timedelta(hours=1)

        # Process data
        df = detector.find_swing_highs_lows(df)
        df = detector.detect_break_of_structure(df)
        df = detector.detect_order_blocks(df)

        # Detect trend lines
        trend_lines = detector.detect_trend_lines(df)

        # Generate trading signals
        trading_signals = detector.generate_trading_signals(df)

        # Create chart with theme
        fig = detector.create_chart(df, symbol, theme)

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

        # Convert numpy/pandas types to Python native types for JSON serialization
        def convert_to_python_types(obj):
            """Convert numpy/pandas types to Python native types"""
            if hasattr(obj, 'item'):  # numpy scalar
                return obj.item()
            elif hasattr(obj, 'tolist'):  # numpy array
                return obj.tolist()
            elif isinstance(obj, dict):
                return {k: convert_to_python_types(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [convert_to_python_types(item) for item in obj]
            else:
                return obj

        # Convert trend lines to JSON-serializable format
        serializable_trend_lines = convert_to_python_types(trend_lines)

        return jsonify({
            'chart': chart_json,
            'stats': {
                'bullish_obs': int(bullish_obs),
                'bearish_obs': int(bearish_obs),
                'bullish_bos': int(bullish_bos),
                'bearish_bos': int(bearish_bos),
                'total_candles': int(len(df)),
                'current_price': float(round(current_price, 2)),
                'price_change': float(round(price_change, 2)),
                'trend_lines': int(len(trend_lines)),
                'support_lines': int(len([tl for tl in trend_lines if tl['type'] == 'support'])),
                'resistance_lines': int(len([tl for tl in trend_lines if tl['type'] == 'resistance']))
            },
            'trading_signals': trading_signals,
            'trend_lines': serializable_trend_lines,
            'using_sample_data': using_sample_data
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/symbols')
def get_symbols():
    """Get available trading symbols"""
    try:
        # Try to get symbols from exchange
        if detector.exchange is None:
            detector.init_exchange()

        if detector.exchange is not None:
            try:
                markets = detector.exchange.load_markets()
                symbols = [symbol for symbol in markets.keys()
                           if '/USDT' in symbol]
                # Limit to top 50 for performance
                symbols = sorted(symbols[:50])
                logger.info(f"Loaded {len(symbols)} symbols from exchange")
                return jsonify({'symbols': symbols})
            except Exception as e:
                logger.error(f"Failed to load symbols from exchange: {e}")

        # Fallback to predefined symbols if exchange fails
        fallback_symbols = [
            'BTC/USDT', 'ETH/USDT', 'BNB/USDT', 'ADA/USDT', 'DOT/USDT',
            'SOL/USDT', 'MATIC/USDT', 'LINK/USDT', 'UNI/USDT', 'LTC/USDT',
            'BCH/USDT', 'XRP/USDT', 'DOGE/USDT', 'SHIB/USDT', 'AVAX/USDT',
            'ATOM/USDT', 'FTM/USDT', 'NEAR/USDT', 'ALGO/USDT', 'VET/USDT'
        ]
        logger.info(f"Using fallback symbols: {len(fallback_symbols)} symbols")
        return jsonify({'symbols': fallback_symbols})

    except Exception as e:
        logger.error(f"Symbols endpoint error: {e}")
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
