"""
Stock demand forecasting using linear regression.
Uses past 30-day sales data to predict the next 7 days demand per product.
"""

from datetime import date, timedelta
import numpy as np
from models import db
from models.models import SalesAnalytics, StockForecast, Product


def forecast_stock():
    """
    For each product, fit a linear trend on the last 30 days of sales.
    Predict the next 7 days and store in stock_forecast table.
    """
    products = Product.query.filter_by(is_active=True).all()

    # Clear old forecasts
    StockForecast.query.delete()

    today = date.today()
    last_30 = [(today - timedelta(days=i)) for i in range(29, -1, -1)]

    for product in products:
        # Collect daily sales for last 30 days
        daily_sales = []
        for d in last_30:
            rows = SalesAnalytics.query.filter_by(product_id=product.id, date=d).all()
            total = sum(r.quantity_sold for r in rows)
            daily_sales.append(total)

        if sum(daily_sales) == 0:
            continue  # No sales data — skip forecasting

        x = np.array(range(len(daily_sales)), dtype=float)
        y = np.array(daily_sales, dtype=float)

        # Linear regression: y = mx + b
        n = len(x)
        m = (n * np.dot(x, y) - x.sum() * y.sum()) / (n * np.dot(x, x) - x.sum() ** 2)
        b = (y.sum() - m * x.sum()) / n

        # Forecast next 7 days
        for i in range(1, 8):
            future_x = len(daily_sales) + i
            predicted = max(0, int(round(m * future_x + b)))
            forecast_date = today + timedelta(days=i)

            forecast = StockForecast(
                product_id=product.id,
                predicted_demand=predicted,
                forecast_date=forecast_date
            )
            db.session.add(forecast)

    db.session.commit()
