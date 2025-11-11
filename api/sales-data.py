from http.server import BaseHTTPRequestHandler
import json
import random
from datetime import datetime, timedelta

class handler(BaseHTTPRequestHandler):
    
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
        
        data = self.generate_sales_data()
        
        self.wfile.write(json.dumps(data).encode())
        return
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
        return
    
    def generate_sales_data(self):
        """Generate realistic sales CRM data"""
        
        stages = ['Prospecting', 'Qualification', 'Proposal', 'Negotiation', 'Closed Won', 'Closed Lost']
        products = ['Fiber Internet', 'Dark Fiber', 'Ethernet', 'Cloud Connect', 'Managed Services']
        regions = ['Northwest', 'Mountain West', 'Pacific', 'Southwest']
        reps = ['Sarah Johnson', 'Mike Chen', 'Emily Rodriguez', 'David Kim', 'Jessica Taylor', 'Alex Martinez', 'Chris Lee', 'Jordan Smith']
        industries = ['Technology', 'Healthcare', 'Finance', 'Manufacturing', 'Retail', 'Education']
        
        opportunities = []
        current_date = datetime.now()
        
        stage_weights = [0.25, 0.25, 0.20, 0.15, 0.10, 0.05]
        
        for i in range(200):
            days_ago = random.randint(0, 180)
            created_date = current_date - timedelta(days=days_ago)
            
            days_to_close = random.randint(30, 120)
            close_date = created_date + timedelta(days=days_to_close)
            
            rand = random.random()
            cum_weight = 0
            stage_index = 0
            for j, weight in enumerate(stage_weights):
                cum_weight += weight
                if rand <= cum_weight:
                    stage_index = j
                    break
            
            stage = stages[stage_index]
            
            if stage == 'Closed Won':
                probability = 100
            elif stage == 'Closed Lost':
                probability = 0
            elif stage == 'Negotiation':
                probability = 75
            elif stage == 'Proposal':
                probability = 50
            elif stage == 'Qualification':
                probability = 25
            else:
                probability = 10
            
            base_amounts = [2500, 15000, 1800, 3200, 5000]
            base_amount = random.choice(base_amounts)
            amount = int(base_amount * random.uniform(0.5, 3.0) * random.randint(1, 10))
            
            days_in_stage = random.randint(5, 45) + (stage_index * 5)
            
            opportunities.append({
                'id': f'OPP-{3000 + i}',
                'accountName': f'Company {i + 1}',
                'stage': stage,
                'product': random.choice(products),
                'amount': amount,
                'probability': probability,
                'region': random.choice(regions),
                'owner': random.choice(reps),
                'industry': random.choice(industries),
                'createdDate': created_date.strftime('%Y-%m-%d'),
                'closeDate': close_date.strftime('%Y-%m-%d'),
                'daysInStage': days_in_stage
            })
        
        return {
            'opportunities': opportunities,
            'generated_at': current_date.isoformat(),
            'count': len(opportunities)
        }