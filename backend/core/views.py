import pandas as pd
import io
from django.http import FileResponse
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework import status, permissions, authentication
from .models import UploadedDataset
from .serializers import DatasetSerializer

# 1. AUTHENTICATION: Restrict access to registered users only
class BaseAuthView(APIView):
    authentication_classes = [authentication.BasicAuthentication]
    permission_classes = [permissions.IsAuthenticated]

class FileUploadView(BaseAuthView): # Inherit from BaseAuthView
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request, *args, **kwargs):
        file_serializer = DatasetSerializer(data=request.data)
        if file_serializer.is_valid():
            dataset_instance = file_serializer.save()
            try:
                df = pd.read_csv(dataset_instance.file.path)
                
                # Check columns
                required_columns = ['Equipment Name', 'Type', 'Flowrate', 'Pressure', 'Temperature']
                if not all(col in df.columns for col in required_columns):
                     dataset_instance.delete()
                     return Response({"error": "Missing columns"}, status=status.HTTP_400_BAD_REQUEST)

                # Calculate Stats
                dataset_instance.total_count = len(df)
                dataset_instance.avg_flowrate = df['Flowrate'].mean()
                dataset_instance.avg_pressure = df['Pressure'].mean()
                dataset_instance.avg_temperature = df['Temperature'].mean()
                dataset_instance.save()
                
                type_dist = df['Type'].value_counts().to_dict()
                raw_data = df.head(50).fillna('').to_dict(orient='records')
                
                return Response({
                    "message": "File processed successfully",
                    "id": dataset_instance.id,
                    "summary": {
                        "total_count": dataset_instance.total_count,
                        "avg_flowrate": round(dataset_instance.avg_flowrate, 2),
                        "avg_pressure": round(dataset_instance.avg_pressure, 2),
                        "avg_temperature": round(dataset_instance.avg_temperature, 2),
                    },
                    "type_distribution": type_dist,
                    "table_data": raw_data
                }, status=status.HTTP_201_CREATED)
                
            except Exception as e:
                dataset_instance.delete()
                return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(file_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class HistoryView(BaseAuthView): # Inherit from BaseAuthView
    def get(self, request):
        datasets = UploadedDataset.objects.all().order_by('-uploaded_at')[:5]
        serializer = DatasetSerializer(datasets, many=True)
        return Response(serializer.data)

# 2. PDF GENERATION: New View
class PDFReportView(BaseAuthView):
    def get(self, request, pk):
        try:
            dataset = UploadedDataset.objects.get(pk=pk)
            
            # Create a PDF buffer
            buffer = io.BytesIO()
            p = canvas.Canvas(buffer, pagesize=letter)
            
            # Write content
            p.setFont("Helvetica-Bold", 16)
            p.drawString(100, 750, f"Chemical Equipment Report (ID: {dataset.id})")
            
            p.setFont("Helvetica", 12)
            p.drawString(100, 720, f"Uploaded At: {dataset.uploaded_at}")
            p.drawString(100, 700, f"Total Equipment Count: {dataset.total_count}")
            p.drawString(100, 680, f"Avg Flowrate: {dataset.avg_flowrate}")
            p.drawString(100, 660, f"Avg Pressure: {dataset.avg_pressure}")
            p.drawString(100, 640, f"Avg Temperature: {dataset.avg_temperature}")
            
            p.showPage()
            p.save()
            
            buffer.seek(0)
            return FileResponse(buffer, as_attachment=True, filename=f'report_{pk}.pdf')
            
        except UploadedDataset.DoesNotExist:
            return Response({"error": "Dataset not found"}, status=status.HTTP_404_NOT_FOUND)
        
from django.http import HttpResponse
from django.contrib.auth.models import User

def create_admin_user(request):
    # Check if admin already exists
    if User.objects.filter(username='admin').exists():
        return HttpResponse("Admin user already exists! You can login now.")
    
    # Create the admin user
    User.objects.create_superuser('admin', 'admin@example.com', 'password123')
    return HttpResponse("SUCCESS: Admin user 'admin' created with password 'password123'.")