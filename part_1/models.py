from django.db import models
# ORM object relational mapping for tables in the database

class FoodEntry(models.Model):
    user_name = models.CharField(max_length=100, db_index=True)  
    food_name = models.CharField(max_length=100, db_index=True)
    meal_type = models.CharField(max_length=20, db_index=True)
    carbs = models.FloatField()
    protein = models.FloatField()
    fats = models.FloatField()
    calories = models.FloatField(db_index=True)

    class Meta:
        indexes = [
            models.Index(fields=['user_name', 'meal_type']),
            models.Index(fields=['food_name', 'calories']), 
        ]

    def __str__(self):
        return f"{self.user_name} - {self.food_name} - {self.meal_type}"
    

class UserData(models.Model):
    name = models.CharField(max_length=255, unique=True, db_index=True)
    weight = models.DecimalField(max_digits=5, decimal_places=2)

    def __str__(self):
        return f"{self.name} - {self.weight} kg"

class DayPlan(models.Model):
    user_name = models.CharField(max_length=100, db_index=True)
    date = models.DateField(db_index=True)
    food_entry = models.ForeignKey(FoodEntry, on_delete=models.CASCADE)
    meal_type = models.CharField(max_length=20, db_index=True)

    class Meta:
        indexes = [
            models.Index(fields=['user_name', 'date']),
            models.Index(fields=['date', 'meal_type']),
        ]

    def __str__(self):
        return f"{self.user_name} - {self.date} - {self.food_entry.food_name}"
