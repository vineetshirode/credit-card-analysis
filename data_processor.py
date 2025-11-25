import pandas as pd
import numpy as np
from datetime import datetime
import os

class CreditCardDataProcessor:
    def __init__(self, data_path='data/cleaned_data.xlsx'):
        """Initialize and load the dataset"""
        self.data_path = data_path
        self.df = None
        self.load_data()
        
    def load_data(self):
        """Load and preprocess the dataset"""
        try:
            self.df = pd.read_excel(self.data_path)
            
            # Convert date columns
            self.df['Birthdate'] = pd.to_datetime(self.df['Birthdate'], format='%d-%m-%Y', errors='coerce')
            self.df['Date'] = pd.to_datetime(self.df['Date'], format='%d-%m-%Y', errors='coerce')
            
            # Calculate age
            current_date = pd.Timestamp.now()
            self.df['Age'] = ((current_date - self.df['Birthdate']).dt.days / 365.25).astype(int)
            
            # Extract temporal features
            self.df['Month'] = self.df['Date'].dt.month
            self.df['Year'] = self.df['Date'].dt.year
            self.df['Day_Name'] = self.df['Date'].dt.strftime('%A')
            self.df['Month_Name'] = self.df['Date'].dt.strftime('%B')
            
            print(f"✓ Dataset loaded successfully: {len(self.df)} records")
            return True
        except Exception as e:
            print(f"✗ Error loading dataset: {e}")
            return False
    
    def get_merchant_trust_score(self, merchant_name):
        try:
            # DEBUG: Print search info
            print(f"Searching for merchant: '{merchant_name}'")
            print(f"Total merchants in database: {self.df['Merchant_Name'].nunique()}")
            print(f"Sample merchants: {self.df['Merchant_Name'].unique()[:5]}")
            
            # Filter merchant data (case-insensitive search)
            merchant_df = self.df[self.df['Merchant_Name'].str.contains(merchant_name, case=False, na=False)]
            
            print(f"Found {len(merchant_df)} matching transactions")
            
            if merchant_df.empty:
                return None
            
            # Calculate metrics
            total_transactions = len(merchant_df)
            avg_amount = merchant_df['Transaction_Amount'].mean()
            total_amount = merchant_df['Transaction_Amount'].sum()
            category = merchant_df['Category'].mode()[0] if not merchant_df['Category'].mode().empty else 'Unknown'
            
            # Calculate trust score (0-100)
            # Based on: transaction count (40%), amount consistency (30%), time span (30%)
            count_score = min(total_transactions / 10 * 40, 40)
            
            # Amount consistency (lower std dev = higher score)
            amount_std = merchant_df['Transaction_Amount'].std()
            amount_mean = merchant_df['Transaction_Amount'].mean()
            cv = (amount_std / amount_mean) if amount_mean > 0 else 1
            consistency_score = max(0, 30 - (cv * 10))
            
            # Time span score
            date_range = (merchant_df['Date'].max() - merchant_df['Date'].min()).days
            time_score = min(date_range / 30 * 30, 30)
            
            trust_score = int(count_score + consistency_score + time_score)
            trust_score = min(trust_score, 100)
            
            return {
                'merchant_name': merchant_df['Merchant_Name'].iloc[0],
                'trust_score': trust_score,
                'total_transactions': int(total_transactions),
                'avg_amount': float(round(avg_amount, 2)),
                'total_amount': float(round(total_amount, 2)),
                'category': category,
                'rating': 'Excellent' if trust_score >= 85 else 'Good' if trust_score >= 70 else 'Fair' if trust_score >= 50 else 'Poor'
            }
        except Exception as e:
            print(f"Error in get_merchant_trust_score: {e}")
            return None
    
    def get_customer_analysis(self, customer_id):
        """Analyze customer spending behavior"""
        try:
            customer_df = self.df[self.df['Customer ID'] == int(customer_id)]
            
            if customer_df.empty:
                return None
            
            total_spending = customer_df['Transaction_Amount'].sum()
            transaction_count = len(customer_df)
            avg_transaction = customer_df['Transaction_Amount'].mean()
            
            # Determine spending level
            overall_avg = self.df['Transaction_Amount'].mean()
            if avg_transaction > overall_avg * 1.5:
                spending_level = 'High'
            elif avg_transaction > overall_avg * 0.8:
                spending_level = 'Medium'
            else:
                spending_level = 'Low'
            
            # Get customer details
            name = f"{customer_df['Name'].iloc[0]}"
            age = int(customer_df['Age'].iloc[0]) if pd.notna(customer_df['Age'].iloc[0]) else None
            gender = customer_df['Gender'].iloc[0]
            
            # Favorite category
            fav_category = customer_df['Category'].mode()[0] if not customer_df['Category'].mode().empty else 'Various'
            
            return {
                'customer_id': int(customer_id),
                'name': name,
                'age': age,
                'gender': gender,
                'total_spending': float(round(total_spending, 2)),
                'transaction_count': int(transaction_count),
                'avg_transaction': float(round(avg_transaction, 2)),
                'spending_level': spending_level,
                'favorite_category': fav_category
            }
        except Exception as e:
            print(f"Error in get_customer_analysis: {e}")
            return None
    
    def get_category_insights(self, category):
        """Get insights for a specific category"""
        try:
            category_df = self.df[self.df['Category'] == category]
            
            if category_df.empty:
                return None
            
            avg_amount = category_df['Transaction_Amount'].mean()
            total_transactions = len(category_df)
            total_amount = category_df['Transaction_Amount'].sum()
            
            # Calculate trend (compare recent vs older transactions)
            category_df_sorted = category_df.sort_values('Date')
            mid_point = len(category_df_sorted) // 2
            
            if mid_point > 0:
                recent_avg = category_df_sorted.tail(mid_point)['Transaction_Amount'].mean()
                older_avg = category_df_sorted.head(mid_point)['Transaction_Amount'].mean()
                
                if recent_avg > older_avg * 1.1:
                    trend = 'increasing'
                elif recent_avg < older_avg * 0.9:
                    trend = 'decreasing'
                else:
                    trend = 'stable'
            else:
                trend = 'stable'
            
            # Popularity
            total_records = len(self.df)
            popularity_pct = (total_transactions / total_records) * 100
            
            if popularity_pct > 20:
                popularity = 'Very High'
            elif popularity_pct > 15:
                popularity = 'High'
            elif popularity_pct > 10:
                popularity = 'Moderate'
            else:
                popularity = 'Low'
            
            return {
                'category': category,
                'avg_amount': float(round(avg_amount, 2)),
                'total_transactions': int(total_transactions),
                'total_amount': float(round(total_amount, 2)),
                'trend': trend,
                'popularity': popularity,
                'market_share': float(round(popularity_pct, 1))
            }
        except Exception as e:
            print(f"Error in get_category_insights: {e}")
            return None
    
    def assess_transaction_risk(self, amount, category):
        """Assess risk level for a transaction"""
        try:
            category_df = self.df[self.df['Category'] == category]
            
            if category_df.empty:
                return None
            
            category_avg = category_df['Transaction_Amount'].mean()
            category_std = category_df['Transaction_Amount'].std()
            
            # Calculate deviation
            deviation = ((amount - category_avg) / category_avg * 100) if category_avg > 0 else 0
            
            # Calculate z-score
            z_score = ((amount - category_avg) / category_std) if category_std > 0 else 0
            
            # Determine risk level
            if abs(z_score) < 1:
                risk_level = 'Low Risk'
                risk_score = 25
            elif abs(z_score) < 2:
                risk_level = 'Medium Risk'
                risk_score = 55
            else:
                risk_level = 'High Risk'
                risk_score = 85
            
            return {
                'amount': float(amount),
                'category': category,
                'category_avg': float(round(category_avg, 2)),
                'deviation': float(round(deviation, 1)),
                'risk_level': risk_level,
                'risk_score': int(risk_score),
                'z_score': float(round(z_score, 2))
            }
        except Exception as e:
            print(f"Error in assess_transaction_risk: {e}")
            return None
    
    def get_city_analysis(self, city_name):
        """Analyze transactions for a specific city"""
        try:
            city_df = self.df[self.df['City'].str.contains(city_name, case=False, na=False)]
            
            if city_df.empty:
                return None
            
            total_transactions = len(city_df)
            total_volume = city_df['Transaction_Amount'].sum()
            avg_transaction = city_df['Transaction_Amount'].mean()
            
            # Determine activity level
            overall_city_avg = self.df.groupby('City').size().mean()
            if total_transactions > overall_city_avg * 1.5:
                activity_level = 'Very High'
            elif total_transactions > overall_city_avg:
                activity_level = 'High'
            else:
                activity_level = 'Moderate'
            
            # Top category
            top_category = city_df['Category'].mode()[0] if not city_df['Category'].mode().empty else 'Various'
            
            return {
                'city': city_df['City'].iloc[0],
                'total_transactions': int(total_transactions),
                'total_volume': float(round(total_volume, 2)),
                'avg_transaction': float(round(avg_transaction, 2)),
                'activity_level': activity_level,
                'top_category': top_category
            }
        except Exception as e:
            print(f"Error in get_city_analysis: {e}")
            return None
    
    def predict_spending(self, age, gender):
        """Predict spending based on demographics"""
        try:
            # Filter similar demographics
            demo_df = self.df[(self.df['Age'] >= age - 5) & (self.df['Age'] <= age + 5)]
            
            if gender in ['M', 'F']:
                demo_df = demo_df[demo_df['Gender'] == gender]
            
            if demo_df.empty:
                demo_df = self.df  # Fallback to all data
            
            # Calculate predictions
            avg_monthly_spending = demo_df.groupby('Customer ID')['Transaction_Amount'].sum().mean()
            avg_frequency = demo_df.groupby('Customer ID').size().mean()
            
            # Determine age group
            if age <= 25:
                age_group = '18-25'
            elif age <= 35:
                age_group = '26-35'
            elif age <= 50:
                age_group = '36-50'
            elif age <= 65:
                age_group = '51-65'
            else:
                age_group = '65+'
            
            # Top category for this demographic
            top_category = demo_df['Category'].mode()[0] if not demo_df['Category'].mode().empty else 'Various'
            
            # Confidence (based on sample size)
            confidence = min(len(demo_df) / 100 * 100, 95)
            
            return {
                'age': int(age),
                'gender': 'Male' if gender == 'M' else 'Female',
                'age_group': age_group,
                'predicted_monthly_spending': float(round(avg_monthly_spending, 2)),
                'predicted_frequency': int(round(avg_frequency)),
                'top_category': top_category,
                'confidence': float(round(confidence, 1))
            }
        except Exception as e:
            print(f"Error in predict_spending: {e}")
            return None
    
    def get_dashboard_stats(self):
        """Get overall dashboard statistics"""
        try:
            return {
                'total_transactions': int(len(self.df)),
                'total_customers': int(self.df['Customer ID'].nunique()),
                'total_merchants': int(self.df['Merchant_Name'].nunique()),
                'total_volume': float(round(self.df['Transaction_Amount'].sum(), 2)),
                'avg_transaction': float(round(self.df['Transaction_Amount'].mean(), 2)),
                'categories': self.df['Category'].unique().tolist(),
                'cities': self.df['City'].unique().tolist()
            }
        except Exception as e:
            print(f"Error in get_dashboard_stats: {e}")
            return None