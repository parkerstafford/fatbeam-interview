import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random
from faker import Faker
import sqlite3
import json

fake = Faker()
np.random.seed(42)
random.seed(42)

class SalesDataGenerator:
    def __init__(self):
        self.stages = ['Prospecting', 'Qualification', 'Proposal', 'Negotiation', 'Closed Won', 'Closed Lost']
        self.stage_probabilities = [10, 25, 50, 75, 100, 0]
        self.products = [
            ('PROD-001', 'Fiber Internet', 'Connectivity', 2500, True),
            ('PROD-002', 'Dark Fiber', 'Infrastructure', 15000, True),
            ('PROD-003', 'Ethernet', 'Connectivity', 1800, True),
            ('PROD-004', 'Cloud Connect', 'Cloud Services', 3200, True),
            ('PROD-005', 'Managed Services', 'Professional Services', 5000, False),
        ]
        self.regions = [
            ('TERR-NW', 'Northwest', 'Pacific Northwest', 500000),
            ('TERR-MW', 'Mountain West', 'Mountain', 450000),
            ('TERR-PAC', 'Pacific', 'West Coast', 600000),
            ('TERR-SW', 'Southwest', 'Southwest', 480000),
        ]
        self.industries = ['Technology', 'Healthcare', 'Finance', 'Manufacturing', 'Retail', 'Education']

    def generate_territories(self):
        """Generate territory data"""
        return pd.DataFrame([
            {
                'territory_id': t[0],
                'territory_name': t[1],
                'region': t[2],
                'quota_monthly': t[3],
                'active': True
            }
            for t in self.regions
        ])

    def generate_sales_reps(self, n_reps=8):
        """Generate sales rep data"""
        reps = []
        territories = [t[0] for t in self.regions]

        for i in range(n_reps):
            reps.append({
                'rep_id': f'REP-{1000+i}',
                'first_name': fake.first_name(),
                'last_name': fake.last_name(),
                'email': fake.email(),
                'territory_id': territories[i % len(territories)],
                'hire_date': fake.date_between(start_date='-3y', end_date='-6m'),
                'role': 'Account Executive',
                'quota_annual': np.random.randint(1000000, 2000000),
                'active': True
            })

        return pd.DataFrame(reps)

    def generate_products(self):
        """Generate product data"""
        return pd.DataFrame([
            {
                'product_id': p[0],
                'product_name': p[1],
                'product_category': p[2],
                'unit_price': p[3],
                'recurring': p[4],
                'active': True
            }
            for p in self.products
        ])

    def generate_accounts(self, n_accounts=100):
        """Generate account/company data"""
        accounts = []
        territories = [t[0] for t in self.regions]

        for i in range(n_accounts):
            accounts.append({
                'account_id': f'ACC-{2000+i}',
                'account_name': fake.company(),
                'industry': random.choice(self.industries),
                'company_size': random.choice(['Small (1-50)', 'Medium (51-200)', 'Large (201-1000)', 'Enterprise (1000+)']),
                'territory_id': random.choice(territories),
                'annual_revenue': np.random.randint(1000000, 50000000),
                'website': fake.url(),
                'primary_contact_name': fake.name(),
                'primary_contact_email': fake.email(),
                'account_status': 'Active',
                'created_date': fake.date_time_between(start_date='-2y', end_date='-1y')
            })

        return pd.DataFrame(accounts)

    def generate_opportunities(self, accounts_df, reps_df, products_df, n_opportunities=200):
        """Generate opportunity data with realistic patterns"""
        opportunities = []

        for i in range(n_opportunities):
            created_date = fake.date_time_between(start_date='-6m', end_date='now')

            stage_weights = [0.25, 0.25, 0.20, 0.15, 0.10, 0.05]
            stage = random.choices(self.stages, weights=stage_weights)[0]
            stage_idx = self.stages.index(stage)
            probability = self.stage_probabilities[stage_idx]

            product = products_df.sample(1).iloc[0]

            base_amount = product['unit_price']
            amount = base_amount * np.random.uniform(0.5, 3.0) * np.random.randint(1, 10)

            if stage == 'Closed Won' or stage == 'Closed Lost':
                close_date = created_date + timedelta(days=np.random.randint(30, 120))
            else:
                close_date = datetime.now() + timedelta(days=np.random.randint(15, 90))

            days_in_stage = np.random.randint(5, 45) + (stage_idx * 5)

            opportunities.append({
                'opportunity_id': f'OPP-{3000+i}',
                'account_id': accounts_df.sample(1).iloc[0]['account_id'],
                'rep_id': reps_df.sample(1).iloc[0]['rep_id'],
                'opportunity_name': f"{fake.catch_phrase()} - {product['product_name']}",
                'stage': stage,
                'product_id': product['product_id'],
                'amount': round(amount, 2),
                'probability': probability,
                'expected_revenue': round(amount * probability / 100, 2),
                'close_date': close_date,
                'created_date': created_date,
                'last_modified_date': datetime.now(),
                'days_in_stage': days_in_stage,
                'previous_stage': self.stages[stage_idx-1] if stage_idx > 0 else None,
                'lead_source': random.choice(['Website', 'Referral', 'Cold Call', 'Trade Show', 'Partner'])
            })

        return pd.DataFrame(opportunities)

    def generate_activities(self, opportunities_df, reps_df, n_activities=500):
        """Generate sales activity data"""
        activities = []
        activity_types = ['Call', 'Email', 'Meeting', 'Demo', 'Proposal Review']

        for i in range(n_activities):
            opp = opportunities_df.sample(1).iloc[0]

            activities.append({
                'activity_id': f'ACT-{4000+i}',
                'opportunity_id': opp['opportunity_id'],
                'account_id': opp['account_id'],
                'rep_id': opp['rep_id'],
                'activity_type': random.choice(activity_types),
                'activity_date': fake.date_time_between(
                    start_date=opp['created_date'], 
                    end_date='now'
                ),
                'duration_minutes': np.random.randint(15, 120),
                'outcome': random.choice(['Positive', 'Neutral', 'Needs Follow-up', 'No Response'])
            })

        return pd.DataFrame(activities)

class SalesAnalytics:
    """Perform advanced sales analytics"""

    def __init__(self, opportunities_df, accounts_df, reps_df, territories_df):
        self.opps = opportunities_df
        self.accounts = accounts_df
        self.reps = reps_df
        self.territories = territories_df

    def calculate_key_metrics(self):
        """Calculate core sales metrics"""
        open_opps = self.opps[~self.opps['stage'].isin(['Closed Won', 'Closed Lost'])]
        closed_opps = self.opps[self.opps['stage'].isin(['Closed Won', 'Closed Lost'])]
        won_opps = self.opps[self.opps['stage'] == 'Closed Won']

        metrics = {
            'total_pipeline': open_opps['amount'].sum(),
            'weighted_pipeline': open_opps['expected_revenue'].sum(),
            'total_revenue': won_opps['amount'].sum(),
            'win_rate': len(won_opps) / len(closed_opps) * 100 if len(closed_opps) > 0 else 0,
            'avg_deal_size': self.opps['amount'].mean(),
            'total_opportunities': len(self.opps),
            'open_opportunities': len(open_opps),
            'closed_won': len(won_opps),
            'avg_sales_cycle': self._calculate_avg_sales_cycle()
        }

        return metrics

    def _calculate_avg_sales_cycle(self):
        """Calculate average days from created to closed"""
        closed = self.opps[self.opps['stage'].isin(['Closed Won', 'Closed Lost'])].copy()
        closed['cycle_days'] = (closed['close_date'] - closed['created_date']).dt.days
        return closed['cycle_days'].mean()

    def sales_velocity(self):
        """Calculate sales velocity: (# of opps * avg deal size * win rate) / sales cycle length"""
        metrics = self.calculate_key_metrics()

        velocity = (
            metrics['open_opportunities'] * 
            metrics['avg_deal_size'] * 
            (metrics['win_rate'] / 100)
        ) / max(metrics['avg_sales_cycle'], 1)

        return velocity

    def pipeline_by_stage(self):
        """Analyze pipeline by stage"""
        return self.opps.groupby('stage').agg({
            'amount': 'sum',
            'opportunity_id': 'count'
        }).rename(columns={'opportunity_id': 'count'})

    def rep_performance(self):
        """Analyze performance by sales rep"""
        rep_stats = []

        for rep_id in self.opps['rep_id'].unique():
            rep_opps = self.opps[self.opps['rep_id'] == rep_id]
            rep_info = self.reps[self.reps['rep_id'] == rep_id].iloc[0]

            open_opps = rep_opps[~rep_opps['stage'].isin(['Closed Won', 'Closed Lost'])]
            won_opps = rep_opps[rep_opps['stage'] == 'Closed Won']
            closed_opps = rep_opps[rep_opps['stage'].isin(['Closed Won', 'Closed Lost'])]

            rep_stats.append({
                'rep_id': rep_id,
                'rep_name': f"{rep_info['first_name']} {rep_info['last_name']}",
                'territory': rep_info['territory_id'],
                'pipeline_value': open_opps['amount'].sum(),
                'revenue': won_opps['amount'].sum(),
                'win_rate': len(won_opps) / len(closed_opps) * 100 if len(closed_opps) > 0 else 0,
                'avg_deal_size': rep_opps['amount'].mean(),
                'total_opps': len(rep_opps)
            })

        return pd.DataFrame(rep_stats).sort_values('revenue', ascending=False)

    def forecast_next_quarter(self):
        """Simple forecast based on weighted pipeline"""
        open_opps = self.opps[~self.opps['stage'].isin(['Closed Won', 'Closed Lost'])]

        today = datetime.now()
        next_quarter = today + timedelta(days=90)

        forecast_opps = open_opps[
            (open_opps['close_date'] >= today) & 
            (open_opps['close_date'] <= next_quarter)
        ]

        return {
            'forecast_best_case': forecast_opps['amount'].sum(),
            'forecast_weighted': forecast_opps['expected_revenue'].sum(),
            'forecast_conservative': forecast_opps[forecast_opps['probability'] >= 75]['amount'].sum(),
            'opportunities_in_forecast': len(forecast_opps)
        }

    def data_quality_report(self):
        """Generate data quality report"""
        issues = []

        missing_product = len(self.opps[self.opps['product_id'].isna()])
        if missing_product > 0:
            issues.append(f"Missing product: {missing_product} opportunities")

        open_past_due = len(self.opps[
            (~self.opps['stage'].isin(['Closed Won', 'Closed Lost'])) &
            (self.opps['close_date'] < datetime.now())
        ])
        if open_past_due > 0:
            issues.append(f"Past close date in open stage: {open_past_due} opportunities")

        zero_amount = len(self.opps[self.opps['amount'] == 0])
        if zero_amount > 0:
            issues.append(f"Zero amount: {zero_amount} opportunities")

        stale_deals = len(self.opps[self.opps['days_in_stage'] > 60])
        if stale_deals > 0:
            issues.append(f"Stale deals (>60 days): {stale_deals} opportunities")

        return issues if issues else ["No data quality issues found"]

def main():
    generator = SalesDataGenerator()

    territories = generator.generate_territories()
    print(f"Generated {len(territories)} territories")

    reps = generator.generate_sales_reps(8)
    print(f"Generated {len(reps)} sales reps")

    products = generator.generate_products()
    print(f"Generated {len(products)} products")

    accounts = generator.generate_accounts(100)
    print(f"Generated {len(accounts)} accounts")

    opportunities = generator.generate_opportunities(accounts, reps, products, 200)
    print(f"Generated {len(opportunities)} opportunities")

    activities = generator.generate_activities(opportunities, reps, 500)
    print(f"Generated {len(activities)} activities")

    territories.to_csv('territories.csv', index=False)
    reps.to_csv('sales_reps.csv', index=False)
    products.to_csv('products.csv', index=False)
    accounts.to_csv('accounts.csv', index=False)
    opportunities.to_csv('opportunities.csv', index=False)
    activities.to_csv('activities.csv', index=False)
 
    analytics = SalesAnalytics(opportunities, accounts, reps, territories)

    metrics = analytics.calculate_key_metrics()
    print("\n Key Metrics:")
    print(f"  Total Pipeline: ${metrics['total_pipeline']:,.0f}")
    print(f"  Weighted Pipeline: ${metrics['weighted_pipeline']:,.0f}")
    print(f"  Total Revenue: ${metrics['total_revenue']:,.0f}")
    print(f"  Win Rate: {metrics['win_rate']:.1f}%")
    print(f"  Avg Deal Size: ${metrics['avg_deal_size']:,.0f}")
    print(f"  Avg Sales Cycle: {metrics['avg_sales_cycle']:.0f} days")
    print(f"  Sales Velocity: ${analytics.sales_velocity():,.0f}/day")

    print("\nForecast (Next 90 Days):")
    forecast = analytics.forecast_next_quarter()
    for key, value in forecast.items():
        if 'forecast' in key:
            print(f"  {key.replace('_', ' ').title()}: ${value:,.0f}")
        else:
            print(f"  {key.replace('_', ' ').title()}: {value}")

    print("\nTop 3 Performers:")
    rep_perf = analytics.rep_performance()
    print(rep_perf.head(3)[['rep_name', 'revenue', 'win_rate', 'pipeline_value']].to_string(index=False))

    print("\nData Quality Check:")
    quality_issues = analytics.data_quality_report()
    for issue in quality_issues:
        print(f"  - {issue}")

    print("\nAnalysis complete!")

if __name__ == "__main__":
    main()