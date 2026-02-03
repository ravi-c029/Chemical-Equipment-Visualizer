from django.db import models
import os

class UploadedDataset(models.Model):
    file = models.FileField(upload_to='csvs/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    # Storing summary stats to avoid recalculating later
    total_count = models.IntegerField(null=True, blank=True)
    avg_flowrate = models.FloatField(null=True, blank=True)
    avg_pressure = models.FloatField(null=True, blank=True)
    avg_temperature = models.FloatField(null=True, blank=True)

    def save(self, *args, **kwargs):
        # Logic to keep only the last 5 datasets
        # We check count BEFORE saving the new one
        objects = UploadedDataset.objects.all().order_by('-uploaded_at')
        if objects.count() >= 5:
            # Get the datasets that exceed the limit (keep 4, so this new one becomes the 5th)
            excess_datasets = objects[4:] 
            for dataset in excess_datasets:
                # Delete the actual file from disk
                if dataset.file and os.path.isfile(dataset.file.path):
                    os.remove(dataset.file.path)
                # Delete the database record
                dataset.delete()
        
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Dataset {self.id} - {self.uploaded_at}"