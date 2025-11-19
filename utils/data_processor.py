"""
Data processing utilities for real estate analysis
"""
import pandas as pd
import numpy as np
from typing import Dict, List


class RealEstateDataProcessor:
    def __init__(self, file_path: str):
        """Initialize the data processor with Excel file path"""
        self.file_path = file_path
        self.df = None
        self.load_data()
    
    def load_data(self):
        """Load data from Excel file"""
        try:
            self.df = pd.read_excel(self.file_path)
            # Clean column names - remove spaces and make lowercase
            self.df.columns = self.df.columns.str.strip().str.lower().str.replace(' ', '_')
            print(f"✓ Data loaded successfully. Shape: {self.df.shape}")
            print(f"✓ Columns: {list(self.df.columns)}")
        except Exception as e:
            print(f"✗ Error loading data: {e}")
            raise
    
    def get_available_areas(self) -> List[str]:
        """Get list of unique areas in the dataset"""
        area_columns = [col for col in self.df.columns if 'area' in col.lower() or 'location' in col.lower()]
        if area_columns:
            return sorted(self.df[area_columns[0]].dropna().unique().tolist())
        return []
    
    def filter_by_area(self, area: str) -> pd.DataFrame:
        """Filter data by area name (case-insensitive)"""
        area_columns = [col for col in self.df.columns if 'area' in col.lower() or 'location' in col.lower()]
        
        if not area_columns:
            return pd.DataFrame()
        
        area_col = area_columns[0]
        filtered = self.df[self.df[area_col].str.lower() == area.lower()]
        return filtered
    
    def get_price_trend(self, area: str) -> Dict:
        """Get price trend data for chart"""
        filtered = self.filter_by_area(area)
        
        if filtered.empty:
            return {'labels': [], 'data': [], 'error': f'No data found for {area}'}
        
        # Find year and price columns
        year_col = next((col for col in filtered.columns if 'year' in col.lower()), None)
        price_col = next((col for col in filtered.columns if 'price' in col.lower()), None)
        
        if year_col and price_col:
            trend = filtered.groupby(year_col)[price_col].mean().reset_index()
            trend = trend.sort_values(year_col)
            
            return {
                'labels': [int(y) for y in trend[year_col].tolist()],
                'data': [round(float(p), 2) for p in trend[price_col].tolist()],
                'title': f'Price Trend for {area}',
                'type': 'price'
            }
        
        return {'labels': [], 'data': [], 'error': 'Price or year data not available'}
    
    def get_demand_trend(self, area: str) -> Dict:
        """Get demand trend data for chart"""
        filtered = self.filter_by_area(area)
        
        if filtered.empty:
            return {'labels': [], 'data': [], 'error': f'No data found for {area}'}
        
        year_col = next((col for col in filtered.columns if 'year' in col.lower()), None)
        demand_col = next((col for col in filtered.columns if 'demand' in col.lower()), None)
        
        if year_col and demand_col:
            trend = filtered.groupby(year_col)[demand_col].mean().reset_index()
            trend = trend.sort_values(year_col)
            
            return {
                'labels': [int(y) for y in trend[year_col].tolist()],
                'data': [round(float(d), 2) for d in trend[demand_col].tolist()],
                'title': f'Demand Trend for {area}',
                'type': 'demand'
            }
        
        return {'labels': [], 'data': [], 'error': 'Demand or year data not available'}
    
    def compare_areas(self, areas: List[str], metric: str = 'price') -> Dict:
        """Compare multiple areas"""
        result = {
            'labels': [],
            'datasets': [],
            'title': f'{metric.capitalize()} Comparison'
        }
        
        year_col = next((col for col in self.df.columns if 'year' in col.lower()), None)
        metric_col = next((col for col in self.df.columns if metric.lower() in col.lower()), None)
        
        if not year_col or not metric_col:
            return result
        
        all_years = set()
        
        for area in areas:
            filtered = self.filter_by_area(area)
            if not filtered.empty:
                trend = filtered.groupby(year_col)[metric_col].mean().reset_index()
                trend = trend.sort_values(year_col)
                
                years = [int(y) for y in trend[year_col].tolist()]
                all_years.update(years)
                
                result['datasets'].append({
                    'label': area,
                    'data': [round(float(v), 2) for v in trend[metric_col].tolist()]
                })
        
        result['labels'] = sorted(list(all_years))
        return result
    
    def get_summary_stats(self, area: str) -> Dict:
        """Get summary statistics for an area"""
        filtered = self.filter_by_area(area)
        
        if filtered.empty:
            return {'error': f'No data found for {area}'}
        
        stats = {
            'area': area,
            'total_records': len(filtered),
        }
        
        # Find relevant columns
        price_col = next((col for col in filtered.columns if 'price' in col.lower()), None)
        demand_col = next((col for col in filtered.columns if 'demand' in col.lower()), None)
        size_col = next((col for col in filtered.columns if 'size' in col.lower() or 'area' in col.lower() and col != self._get_area_column()), None)
        year_col = next((col for col in filtered.columns if 'year' in col.lower()), None)
        
        # Calculate price statistics
        if price_col:
            stats['avg_price'] = float(filtered[price_col].mean())
            stats['min_price'] = float(filtered[price_col].min())
            stats['max_price'] = float(filtered[price_col].max())
            
            # Calculate price growth
            if year_col:
                yearly = filtered.groupby(year_col)[price_col].mean().sort_index()
                if len(yearly) > 1:
                    growth = ((yearly.iloc[-1] - yearly.iloc[0]) / yearly.iloc[0]) * 100
                    stats['price_growth_pct'] = float(growth)
                    stats['years_analyzed'] = f"{int(yearly.index[0])}-{int(yearly.index[-1])}"
        
        # Calculate demand statistics
        if demand_col:
            stats['avg_demand'] = float(filtered[demand_col].mean())
            stats['min_demand'] = float(filtered[demand_col].min())
            stats['max_demand'] = float(filtered[demand_col].max())
        
        # Calculate size statistics
        if size_col:
            stats['avg_size'] = float(filtered[size_col].mean())
        
        return stats
    
    def _get_area_column(self) -> str:
        """Get the area column name"""
        area_columns = [col for col in self.df.columns if 'area' in col.lower() or 'location' in col.lower()]
        return area_columns[0] if area_columns else ''
    
    def get_filtered_table_data(self, area: str, limit: int = 20) -> List[Dict]:
        """Get filtered table data as list of dictionaries"""
        filtered = self.filter_by_area(area)
        
        if filtered.empty:
            return []
        
        # Select relevant columns and limit records
        filtered = filtered.head(limit)
        
        # Convert to list of dictionaries
        return filtered.to_dict('records')
    
    def generate_summary(self, area: str, stats: Dict, chart_data: Dict) -> str:
        """Generate a comprehensive summary"""
        if 'error' in stats:
            return f"❌ I couldn't find any data for **{area}**. Please check the spelling or try another area.\n\nAvailable areas: {', '.join(self.get_available_areas()[:5])}..."
        
        summary = f"# 📊 Real Estate Analysis for {area}\n\n"
        summary += f"**Analysis based on {stats['total_records']} records**"
        
        if 'years_analyzed' in stats:
            summary += f" ({stats['years_analyzed']})"
        
        summary += "\n\n"
        
        # Price Information
        if 'avg_price' in stats:
            summary += "## 💰 Price Analysis\n"
            summary += f"• **Average Price:** ₹{stats['avg_price']:,.0f}\n"
            summary += f"• **Price Range:** ₹{stats['min_price']:,.0f} - ₹{stats['max_price']:,.0f}\n"
            
            if 'price_growth_pct' in stats:
                growth = stats['price_growth_pct']
                trend_emoji = "📈" if growth > 0 else "📉" if growth < 0 else "➡️"
                trend_word = "increased" if growth > 0 else "decreased" if growth < 0 else "remained stable"
                
                summary += f"• **Growth Trend:** {trend_emoji} Prices have {trend_word} by **{abs(growth):.2f}%**\n"
            
            summary += "\n"
        
        # Demand Information
        if 'avg_demand' in stats:
            summary += "## 📈 Demand Analysis\n"
            demand_level = "High" if stats['avg_demand'] > 70 else "Moderate" if stats['avg_demand'] > 40 else "Low"
            demand_emoji = "🔥" if stats['avg_demand'] > 70 else "⚡" if stats['avg_demand'] > 40 else "💤"
            
            summary += f"• **Demand Level:** {demand_emoji} {demand_level} (Index: {stats['avg_demand']:.2f})\n"
            summary += f"• **Demand Range:** {stats['min_demand']:.2f} - {stats['max_demand']:.2f}\n\n"
        
        # Property Size Information
        if 'avg_size' in stats:
            summary += f"**Average Property Size:** {stats['avg_size']:.0f} sq ft\n\n"
        
        # Investment Insight
        summary += "## 💡 Key Insights\n"
        
        if 'price_growth_pct' in stats:
            if stats['price_growth_pct'] > 5:
                summary += f"✅ **{area}** shows strong growth potential with {stats['price_growth_pct']:.1f}% price appreciation.\n"
            elif stats['price_growth_pct'] > 0:
                summary += f"✅ **{area}** shows steady growth with {stats['price_growth_pct']:.1f}% price increase.\n"
            else:
                summary += f"⚠️ **{area}** has experienced a price decline of {abs(stats['price_growth_pct']):.1f}%.\n"
        
        if 'avg_demand' in stats:
            if stats['avg_demand'] > 70:
                summary += f"🔥 High demand indicates strong market activity and investment interest.\n"
            elif stats['avg_demand'] > 40:
                summary += f"⚡ Moderate demand suggests stable market conditions.\n"
        
        return summary