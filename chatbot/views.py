"""
Views for chatbot API endpoints
"""
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.conf import settings
from django.http import HttpResponse
import pandas as pd
import re
import os
import io

from utils.data_processor import RealEstateDataProcessor


class ChatQueryView(APIView):
    """Handle chat queries and return analysis"""
    
    def post(self, request):
        """Process chat query"""
        query = request.data.get('query', '').strip()
        
        if not query:
            return Response(
                {'error': 'Query is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            data_processor = RealEstateDataProcessor(settings.DATA_FILE_PATH)
            
            # Parse query to determine intent and extract areas
            intent, areas = self._parse_query(query, data_processor)
            
            if not areas:
                available_areas = data_processor.get_available_areas()
                suggestion = ', '.join(available_areas[:5]) if len(available_areas) > 0 else 'No areas found'
                
                return Response({
                    'summary': f"❓ I couldn't identify any area in your query.\n\n**Available areas:** {suggestion}...\n\nPlease try asking about a specific area like 'Analyze Wakad' or 'Show me price trends for Aundh'.",
                    'chart': None,
                    'table': [],
                    'query': query
                }, status=status.HTTP_200_OK)
            
            # Handle different query types
            if intent == 'compare' and len(areas) > 1:
                result = self._handle_comparison(areas, query, data_processor)
            else:
                result = self._handle_single_area_analysis(areas[0], intent, data_processor)
            
            result['query'] = query
            return Response(result, status=status.HTTP_200_OK)
        
        except Exception as e:
            print(f"Error processing query: {e}")
            return Response(
                {'error': f'Error processing query: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def _parse_query(self, query, data_processor):
        """Parse user query to determine intent and extract area names"""
        query_lower = query.lower()
        
        # Get available areas
        available_areas = data_processor.get_available_areas()
        
        # Find mentioned areas (case-insensitive)
        mentioned_areas = []
        for area in available_areas:
            if area.lower() in query_lower:
                mentioned_areas.append(area)
        
        # Determine intent
        intent = 'analysis'  # default
        
        compare_keywords = ['compare', 'comparison', 'versus', 'vs', 'vs.', 'compare to']
        demand_keywords = ['demand', 'demands', 'popularity']
        price_keywords = ['price', 'cost', 'growth', 'appreciation', 'value']
        
        if any(word in query_lower for word in compare_keywords):
            intent = 'compare'
        elif any(word in query_lower for word in demand_keywords):
            intent = 'demand'
        elif any(word in query_lower for word in price_keywords):
            intent = 'price'
        
        return intent, mentioned_areas
    
    def _handle_single_area_analysis(self, area, intent, data_processor):
        """Handle analysis for a single area"""
        # Get statistics
        stats = data_processor.get_summary_stats(area)
        
        if 'error' in stats:
            return {
                'summary': data_processor.generate_summary(area, stats, None),
                'chart': None,
                'table': [],
                'stats': stats
            }
        
        # Get trend data based on intent
        if intent == 'demand':
            chart_data = data_processor.get_demand_trend(area)
        else:
            chart_data = data_processor.get_price_trend(area)
        
        # Generate summary
        summary = data_processor.generate_summary(area, stats, chart_data)
        
        # Get table data
        table_data = data_processor.get_filtered_table_data(area, limit=20)
        
        return {
            'summary': summary,
            'chart': chart_data,
            'table': table_data,
            'stats': stats
        }
    
    def _handle_comparison(self, areas, query, data_processor):
        """Handle comparison between multiple areas"""
        query_lower = query.lower()
        
        # Determine comparison metric
        metric = 'price'
        if 'demand' in query_lower:
            metric = 'demand'
        
        # Get comparison data
        chart_data = data_processor.compare_areas(areas, metric)
        
        # Generate comparison summary
        summary = f"# 📊 Comparison: {' vs '.join(areas)}\n\n"
        summary += f"**Comparing {metric} trends across {len(areas)} areas:**\n\n"
        
        for area in areas:
            stats = data_processor.get_summary_stats(area)
            if 'error' not in stats:
                summary += f"## 📍 {area}\n"
                
                if 'avg_price' in stats and metric == 'price':
                    summary += f"• Average Price: ₹{stats['avg_price']:,.0f}\n"
                    if 'price_growth_pct' in stats:
                        growth_emoji = "📈" if stats['price_growth_pct'] > 0 else "📉"
                        summary += f"• Growth: {growth_emoji} {stats['price_growth_pct']:.2f}%\n"
                
                if 'avg_demand' in stats and metric == 'demand':
                    demand_emoji = "🔥" if stats['avg_demand'] > 70 else "⚡"
                    summary += f"• Demand Index: {demand_emoji} {stats['avg_demand']:.2f}\n"
                
                summary += "\n"
        
        # Get table data for first area
        table_data = data_processor.get_filtered_table_data(areas[0], limit=10)
        
        return {
            'summary': summary,
            'chart': chart_data,
            'table': table_data,
            'comparison': True
        }


class AreasListView(APIView):
    """Get list of available areas"""
    
    def get(self, request):
        """Return list of available areas"""
        try:
            data_processor = RealEstateDataProcessor(settings.DATA_FILE_PATH)
            areas = data_processor.get_available_areas()
            
            return Response({
                'areas': areas,
                'count': len(areas)
            }, status=status.HTTP_200_OK)
        
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class FileUploadView(APIView):
    """Handle Excel file upload"""
    
    def post(self, request):
        """Upload and process Excel file"""
        if 'file' not in request.FILES:
            return Response(
                {'error': 'No file provided'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        uploaded_file = request.FILES['file']
        
        # Validate file extension
        if not uploaded_file.name.endswith(('.xlsx', '.xls')):
            return Response(
                {'error': 'Please upload an Excel file (.xlsx or .xls)'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            # Save file temporarily
            upload_dir = os.path.join(settings.BASE_DIR, 'uploads')
            os.makedirs(upload_dir, exist_ok=True)
            
            file_path = os.path.join(upload_dir, uploaded_file.name)
            
            with open(file_path, 'wb+') as destination:
                for chunk in uploaded_file.chunks():
                    destination.write(chunk)
            
            # Process the file
            data_processor = RealEstateDataProcessor(file_path)
            areas = data_processor.get_available_areas()
            
            return Response({
                'message': 'File uploaded successfully! ✅',
                'areas': areas,
                'records': len(data_processor.df),
                'filename': uploaded_file.name
            }, status=status.HTTP_200_OK)
        
        except Exception as e:
            return Response(
                {'error': f'Error processing file: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class DownloadDataView(APIView):
    """Download filtered data as Excel"""
    
    def post(self, request):
        """Generate and return Excel file"""
        area = request.data.get('area', '')
        
        if not area:
            return Response(
                {'error': 'Area is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            data_processor = RealEstateDataProcessor(settings.DATA_FILE_PATH)
            filtered_df = data_processor.filter_by_area(area)
            
            if filtered_df.empty:
                return Response(
                    {'error': f'No data found for {area}'},
                    status=status.HTTP_404_NOT_FOUND
                )
            
            # Create Excel file in memory
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                filtered_df.to_excel(writer, sheet_name=area, index=False)
            
            output.seek(0)
            
            response = HttpResponse(
                output.read(),
                content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )
            response['Content-Disposition'] = f'attachment; filename="{area}_data.xlsx"'
            
            return response
        
        except Exception as e:
            return Response(
                {'error': f'Error generating download: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class HealthCheckView(APIView):
    """Health check endpoint"""
    
    def get(self, request):
        """Check if API is working"""
        try:
            data_processor = RealEstateDataProcessor(settings.DATA_FILE_PATH)
            areas = data_processor.get_available_areas()
            
            return Response({
                'status': 'healthy',
                'message': 'API is working! ✅',
                'data_loaded': True,
                'areas_count': len(areas)
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                'status': 'unhealthy',
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)