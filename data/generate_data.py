"""
StreamFlow Demo Data Generator
Generates realistic streaming platform data for CEO Agent demo
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random
import os
from pathlib import Path

# Configuration
CONFIG = {
    'start_date': datetime(2024, 4, 1),
    'end_date': datetime(2026, 4, 30),
    'num_customers': 50000,
    'output_dir': Path(__file__).parent / 'output',
    'random_seed': 42
}

# Set random seed for reproducibility
np.random.seed(CONFIG['random_seed'])
random.seed(CONFIG['random_seed'])


def generate_dim_date():
    """Generate date dimension table"""
    dates = pd.date_range(start=CONFIG['start_date'], end=CONFIG['end_date'], freq='D')
    
    df = pd.DataFrame({
        'date_key': dates.strftime('%Y%m%d').astype(int),
        'date': dates.strftime('%Y-%m-%d'),
        'day_of_week': dates.day_name(),
        'day_of_week_num': dates.dayofweek,
        'week_number': dates.isocalendar().week,
        'month': dates.month,
        'month_name': dates.strftime('%B'),
        'quarter': dates.quarter,
        'year': dates.year,
        'is_weekend': dates.dayofweek >= 5,
        'fiscal_year': np.where(dates.month >= 4, dates.year, dates.year - 1)
    })
    
    return df


def generate_dim_geography():
    """Generate geography dimension table"""
    return pd.DataFrame({
        'geo_key': [1, 2, 3, 4, 5],
        'region': ['Europe West', 'Europe East', 'Americas', 'Africa', 'Asia Pacific'],
        'country_code': ['EU-W', 'EU-E', 'AM', 'AF', 'APAC'],
        'currency': ['EUR', 'EUR', 'USD', 'EUR', 'USD'],
        'timezone': ['Europe/Paris', 'Europe/Warsaw', 'America/New_York', 'Africa/Lagos', 'Asia/Singapore'],
        'market_weight': [0.45, 0.15, 0.20, 0.10, 0.10]
    })


def generate_dim_offer():
    """Generate offer/subscription tier dimension"""
    return pd.DataFrame({
        'offer_key': [1, 2, 3, 4],
        'offer_name': ['Basic', 'Standard', 'Premium', 'Ultimate'],
        'monthly_price': [9.99, 14.99, 19.99, 24.99],
        'annual_price': [99.99, 149.99, 199.99, 249.99],
        'max_screens': [1, 2, 4, 6],
        'has_4k': [False, False, True, True],
        'has_download': [False, True, True, True],
        'offer_weight': [0.20, 0.30, 0.35, 0.15]
    })


def generate_dim_content():
    """Generate content catalog dimension"""
    content_types = ['Movie', 'Series', 'Sports', 'Documentary', 'Live Event']
    genres = ['Action', 'Comedy', 'Drama', 'Thriller', 'Sports', 'History', 'Science', 'Music']
    
    # Featured content with realistic names (fictional)
    featured = [
        ('The Crown Protocol', 'Series', 'Thriller', 55, 2500000, True),
        ('Champions League Final', 'Sports', 'Sports', 120, 5000000, False),
        ('Horizon: New Dawn', 'Movie', 'Action', 125, 8000000, True),
        ('Ocean Mysteries', 'Documentary', 'Science', 90, 1500000, True),
        ('Rugby World Cup', 'Sports', 'Sports', 100, 500000, False),
        ('Comedy Central Live', 'Series', 'Comedy', 30, 3000000, True),
        ('Midnight Chase', 'Movie', 'Action', 140, 0, False),
        ('Global Music Awards', 'Live Event', 'Music', 180, 1000000, True),
        ('Formula Racing GP', 'Sports', 'Sports', 150, 2000000, False),
        ('Detective Files S3', 'Series', 'Thriller', 50, 2800000, True),
    ]
    
    content_list = []
    for i, (title, ctype, genre, duration, cost, original) in enumerate(featured):
        content_list.append({
            'content_key': 500 + i,
            'title': title,
            'type': ctype,
            'genre': genre,
            'duration_minutes': duration,
            'production_cost': cost,
            'release_date': (CONFIG['start_date'] + timedelta(days=random.randint(0, 700))).strftime('%Y-%m-%d'),
            'is_original': original
        })
    
    # Generate additional content
    for i in range(10, 100):
        ctype = random.choice(content_types)
        content_list.append({
            'content_key': 500 + i,
            'title': f'{random.choice(["The", "A", "Into", "Beyond", "Dark", "Bright"])} {random.choice(["Night", "Journey", "Secret", "Promise", "Dream", "Storm"])} {random.choice(["", "II", "III", "Returns", "Chronicles"])}',
            'type': ctype,
            'genre': random.choice(genres),
            'duration_minutes': random.randint(30, 180),
            'production_cost': random.randint(100000, 5000000),
            'release_date': (CONFIG['start_date'] + timedelta(days=random.randint(0, 700))).strftime('%Y-%m-%d'),
            'is_original': random.choice([True, False])
        })
    
    return pd.DataFrame(content_list)


def generate_dim_customer(geo_df, offer_df):
    """Generate customer dimension"""
    channels = ['Organic Search', 'Paid Search', 'Social Media', 'TV Advertising', 
                'Partner Referral', 'Direct', 'Email Marketing']
    segments = ['Young Adults', 'Families', 'Premium Users', 'Sports Fans', 'Movie Lovers']
    age_groups = ['18-24', '25-34', '35-44', '45-54', '55+']
    devices = ['Smart TV', 'Mobile', 'Tablet', 'Desktop', 'Gaming Console']
    
    n = CONFIG['num_customers']
    
    return pd.DataFrame({
        'customer_key': range(1000, 1000 + n),
        'acquisition_channel': np.random.choice(channels, n, p=[0.15, 0.20, 0.15, 0.20, 0.10, 0.10, 0.10]),
        'acquisition_date': [(CONFIG['start_date'] + timedelta(days=random.randint(0, 700))).strftime('%Y-%m-%d') for _ in range(n)],
        'segment': np.random.choice(segments, n),
        'age_group': np.random.choice(age_groups, n, p=[0.15, 0.30, 0.25, 0.20, 0.10]),
        'device_preference': np.random.choice(devices, n, p=[0.45, 0.25, 0.15, 0.10, 0.05])
    })


def generate_fact_subscriptions(customer_df, geo_df, offer_df):
    """Generate subscription fact table"""
    n = len(customer_df)
    
    geo_weights = geo_df['market_weight'].values
    offer_weights = offer_df['offer_weight'].values
    prices = dict(zip(offer_df['offer_key'], offer_df['monthly_price']))
    
    # Regional churn rates (higher in emerging markets)
    churn_rates = {1: 0.019, 2: 0.022, 3: 0.021, 4: 0.035, 5: 0.028}
    
    df = pd.DataFrame({
        'subscription_id': range(1, n + 1),
        'date_key': 20260401,  # Snapshot date
        'customer_key': customer_df['customer_key'],
        'geo_key': np.random.choice(geo_df['geo_key'], n, p=geo_weights),
        'offer_key': np.random.choice(offer_df['offer_key'], n, p=offer_weights),
        'billing_type': np.random.choice(['Monthly', 'Annual'], n, p=[0.70, 0.30]),
        'tenure_months': np.random.randint(1, 48, n)
    })
    
    # Add monthly fee
    df['monthly_fee'] = df['offer_key'].map(prices)
    
    # Add status based on regional churn rates
    df['churn_prob'] = df['geo_key'].map(churn_rates)
    df['status'] = np.where(
        np.random.random(n) < df['churn_prob'],
        'Churned', 'Active'
    )
    df = df.drop('churn_prob', axis=1)
    
    return df


def generate_fact_content_views(customer_df, content_df, geo_df, subscriptions_df):
    """Generate content views fact table"""
    devices = ['Smart TV', 'Mobile', 'Tablet', 'Desktop', 'Gaming Console']
    
    views_list = []
    view_id = 1
    
    # Get customer-geo mapping
    cust_geo = dict(zip(subscriptions_df['customer_key'], subscriptions_df['geo_key']))
    content_duration = dict(zip(content_df['content_key'], content_df['duration_minutes']))
    
    # Generate views for each month
    date_range = pd.date_range(start=CONFIG['start_date'], end=CONFIG['end_date'], freq='MS')
    
    print("Generating content views (this may take a moment)...")
    
    for month_start in date_range:
        month_key = int(month_start.strftime('%Y%m01'))
        
        # Growth factor (more views over time)
        months_elapsed = (month_start.year - CONFIG['start_date'].year) * 12 + (month_start.month - CONFIG['start_date'].month)
        base_views = 50000 + months_elapsed * 3000
        
        # Seasonality (more views in winter)
        seasonal_factor = 1.2 if month_start.month in [11, 12, 1, 2] else 1.0
        num_views = int(base_views * seasonal_factor)
        
        # Sample views
        for _ in range(min(num_views, 100000)):  # Cap for performance
            customer = np.random.choice(customer_df['customer_key'].values)
            content = np.random.choice(content_df['content_key'].values)
            geo_key = cust_geo.get(customer, 1)
            
            duration = content_duration.get(content, 60)
            watch_time = min(int(np.random.beta(2, 1.5) * duration * 1.1), duration)
            completion = watch_time / duration if duration > 0 else 0
            
            views_list.append({
                'view_id': view_id,
                'date_key': month_key,
                'customer_key': customer,
                'content_key': content,
                'geo_key': geo_key,
                'views': 1,
                'watch_time_minutes': watch_time,
                'completion_rate': round(completion, 2),
                'device': np.random.choice(devices, p=[0.45, 0.25, 0.15, 0.10, 0.05])
            })
            view_id += 1
    
    return pd.DataFrame(views_list)


def generate_fact_marketing(geo_df):
    """Generate marketing campaign fact table"""
    channels = ['Paid Search', 'Social Media', 'TV Advertising', 'Display', 'Email', 'Partner']
    
    marketing_list = []
    campaign_id = 1
    
    date_range = pd.date_range(start=CONFIG['start_date'], end=CONFIG['end_date'], freq='MS')
    
    for month_start in date_range:
        month_key = int(month_start.strftime('%Y%m01'))
        
        for geo_key in geo_df['geo_key']:
            for channel in channels:
                # Budget varies by channel and region
                base_spend = {
                    'Paid Search': 15000, 'Social Media': 8000, 'TV Advertising': 50000,
                    'Display': 5000, 'Email': 2000, 'Partner': 3000
                }[channel]
                
                geo_multiplier = {1: 1.0, 2: 0.5, 3: 0.8, 4: 0.3, 5: 0.4}[geo_key]
                spend = base_spend * geo_multiplier * (1 + np.random.uniform(-0.2, 0.2))
                
                impressions = int(spend * np.random.uniform(20, 50))
                ctr = np.random.uniform(0.01, 0.03) if channel != 'TV Advertising' else 0
                clicks = int(impressions * ctr)
                conversion = np.random.uniform(0.01, 0.05)
                acquisitions = int(clicks * conversion) if clicks > 0 else int(spend / 100 * conversion)
                
                marketing_list.append({
                    'campaign_id': campaign_id,
                    'date_key': month_key,
                    'geo_key': geo_key,
                    'channel': channel,
                    'spend': round(spend, 2),
                    'impressions': impressions,
                    'clicks': clicks,
                    'acquisitions': max(1, acquisitions),
                    'conversion_rate': round(acquisitions / max(clicks, 1), 4)
                })
                campaign_id += 1
    
    return pd.DataFrame(marketing_list)


def generate_fact_surveys(customer_df, subscriptions_df):
    """Generate NPS survey fact table"""
    categories = ['Content', 'Price', 'App Quality', 'Customer Service', 'Features']
    
    # Sample 20% of customers for surveys
    survey_customers = customer_df.sample(frac=0.2)['customer_key'].values
    
    surveys_list = []
    survey_id = 1
    
    date_range = pd.date_range(start=CONFIG['start_date'], end=CONFIG['end_date'], freq='QE')
    
    for quarter_start in date_range:
        quarter_key = int(quarter_start.strftime('%Y%m01'))
        
        for customer in np.random.choice(survey_customers, size=min(2500, len(survey_customers)), replace=False):
            # NPS score (0-10) with slight positive bias
            score = min(10, max(0, int(np.random.normal(7.5, 2))))
            
            surveys_list.append({
                'survey_id': survey_id,
                'date_key': quarter_key,
                'customer_key': customer,
                'score': score,
                'category': np.random.choice(categories)
            })
            survey_id += 1
    
    return pd.DataFrame(surveys_list)


def main():
    """Generate all demo data"""
    print("=" * 60)
    print("StreamFlow Demo Data Generator")
    print("=" * 60)
    
    # Create output directory
    output_dir = CONFIG['output_dir']
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Generate dimensions
    print("\n📊 Generating dimension tables...")
    
    dim_date = generate_dim_date()
    print(f"  ✅ dim_date: {len(dim_date):,} rows")
    
    dim_geography = generate_dim_geography()
    print(f"  ✅ dim_geography: {len(dim_geography):,} rows")
    
    dim_offer = generate_dim_offer()
    print(f"  ✅ dim_offer: {len(dim_offer):,} rows")
    
    dim_content = generate_dim_content()
    print(f"  ✅ dim_content: {len(dim_content):,} rows")
    
    dim_customer = generate_dim_customer(dim_geography, dim_offer)
    print(f"  ✅ dim_customer: {len(dim_customer):,} rows")
    
    # Generate facts
    print("\n📈 Generating fact tables...")
    
    fact_subscriptions = generate_fact_subscriptions(dim_customer, dim_geography, dim_offer)
    print(f"  ✅ fact_subscriptions: {len(fact_subscriptions):,} rows")
    print(f"     Active: {(fact_subscriptions['status'] == 'Active').sum():,}")
    print(f"     Churned: {(fact_subscriptions['status'] == 'Churned').sum():,}")
    
    fact_content_views = generate_fact_content_views(dim_customer, dim_content, dim_geography, fact_subscriptions)
    print(f"  ✅ fact_content_views: {len(fact_content_views):,} rows")
    
    fact_marketing = generate_fact_marketing(dim_geography)
    print(f"  ✅ fact_marketing: {len(fact_marketing):,} rows")
    
    fact_surveys = generate_fact_surveys(dim_customer, fact_subscriptions)
    print(f"  ✅ fact_surveys: {len(fact_surveys):,} rows")
    
    # Save to CSV
    print("\n💾 Saving CSV files...")
    
    dim_date.to_csv(output_dir / 'dim_date.csv', index=False)
    dim_geography.to_csv(output_dir / 'dim_geography.csv', index=False)
    dim_offer.to_csv(output_dir / 'dim_offer.csv', index=False)
    dim_content.to_csv(output_dir / 'dim_content.csv', index=False)
    dim_customer.to_csv(output_dir / 'dim_customer.csv', index=False)
    fact_subscriptions.to_csv(output_dir / 'fact_subscriptions.csv', index=False)
    fact_content_views.to_csv(output_dir / 'fact_content_views.csv', index=False)
    fact_marketing.to_csv(output_dir / 'fact_marketing.csv', index=False)
    fact_surveys.to_csv(output_dir / 'fact_surveys.csv', index=False)
    
    print(f"\n✅ All files saved to: {output_dir}")
    
    # Summary statistics
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    
    total_mrr = fact_subscriptions[fact_subscriptions['status'] == 'Active']['monthly_fee'].sum()
    active_subs = (fact_subscriptions['status'] == 'Active').sum()
    churn_rate = (fact_subscriptions['status'] == 'Churned').sum() / len(fact_subscriptions)
    
    print(f"📊 Total MRR: €{total_mrr:,.2f}")
    print(f"👥 Active Subscribers: {active_subs:,}")
    print(f"📉 Churn Rate: {churn_rate:.1%}")
    print(f"🎬 Total Content Views: {len(fact_content_views):,}")
    print(f"📢 Marketing Campaigns: {len(fact_marketing):,}")
    print(f"📝 Survey Responses: {len(fact_surveys):,}")
    
    print("\n🎉 Data generation complete!")


if __name__ == "__main__":
    main()
