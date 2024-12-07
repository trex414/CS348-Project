from decimal import ROUND_HALF_UP, Decimal
from sqlite3 import IntegrityError
from django.db import connection
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render, redirect
from .models import FoodEntry
from .models import UserData
import csv
from django.shortcuts import redirect
from django.views.decorators.http import require_POST
from datetime import datetime
from django.utils import timezone
from .models import DayPlan
from django.db import transaction
from django.contrib import messages

# 12 done with ORM and 5 done with prepared statements

# welcome page using ORM
def welcome_page(request):
    # if the user submits a form
    if request.method == "POST":
        # grab the name and weight from the form
        user_name = request.POST.get('name')
        weight = request.POST.get('weight')
        # if they are not empty
        if user_name and weight:
            request.session['user_name'] = user_name
            request.session['weight'] = weight
            return redirect('main')
    return render(request, 'welcome.html')

# main page using ORM
def main_page(request):
    user_name = request.session.get('user_name')
    if not user_name:
        return redirect('welcome')

    if request.method == "POST":
        food_name = request.POST.get('food_name')
        carbs = float(request.POST.get('carbs'))
        protein = float(request.POST.get('protein'))
        fats = float(request.POST.get('fats'))
        calories = float(request.POST.get('calories'))
        meal_type = request.POST.get('meal_type')

        FoodEntry.objects.create(
            user_name=user_name,
            food_name=food_name,
            carbs=carbs,
            protein=protein,
            fats=fats,
            calories=calories,
            meal_type=meal_type
        )
        return redirect('main')

    # Using composite index (user_name, meal_type) for efficient filtering
    breakfast_entries = FoodEntry.objects.filter(
        meal_type="breakfast"
    ).order_by('food_name')
    
    lunch_entries = FoodEntry.objects.filter(
        meal_type="lunch"
    ).order_by('food_name')
    
    dinner_entries = FoodEntry.objects.filter(
        meal_type="dinner"
    ).order_by('food_name')
    
    snack_entries = FoodEntry.objects.filter(
        meal_type="snack"
    ).order_by('food_name')

    context = {
        'user_name': user_name,
        'breakfast_entries': breakfast_entries,
        'lunch_entries': lunch_entries,
        'dinner_entries': dinner_entries,
        'snack_entries': snack_entries,
    }
    return render(request, 'main.html', context)

# remove food with Prepared Statments
def remove_food(request):
    try:
        user_name = request.session.get('user_name')
        entry_id = request.POST.get('entry_id')
        
        if user_name and entry_id:
            # Get the specific entry and verify it belongs to the user
            entry = get_object_or_404(FoodEntry, id=entry_id, user_name=user_name)
            entry.delete()
            
        return redirect('main')
    except Exception as e:
        return redirect('main')

# edit food using ORM
def edit_food(request, entry_id):
    entry = get_object_or_404(FoodEntry, id=entry_id)
    user_name = request.session.get('user_name')

    if request.method == "POST":
        # Update all fields using ORM
        entry.user_name = request.POST.get('user_name')
        entry.food_name = request.POST.get('food_name')
        entry.carbs = float(request.POST.get('carbs'))
        entry.protein = float(request.POST.get('protein'))
        entry.fats = float(request.POST.get('fats'))
        entry.calories = float(request.POST.get('calories'))
        entry.meal_type = request.POST.get('meal_type')
        entry.save() 
        
        return redirect('main')
    
    context = {
        'entry': entry,
        'user_name': user_name
    }
    return render(request, 'edit_food.html', context)

#  create an account using some prepared statements
def create_account(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        weight = request.POST.get('weight')

        if name and weight:
            try:
                # Check if account exists
                with connection.cursor() as cursor:
                    cursor.execute("""SELECT name 
                                    FROM part_1_userdata 
                        WHERE name = %s""", [name])
                    if cursor.fetchone():
                        return render(request, 'welcome.html', {
                            'error': f"Account '{name}' already exists. Please login instead.",
                            'show_error': True})

                # Create new account
                with connection.cursor() as cursor:
                    cursor.execute("""INSERT INTO part_1_userdata (name, weight) 
                                    VALUES (%s, %s)""", [name, weight])
                    connection.commit()
                
                request.session['user_name'] = name
                request.session['weight'] = float(weight)
                
                # Export accounts to CSV
                with connection.cursor() as cursor:
                    cursor.execute(""" SELECT name, weight 
                                        FROM part_1_userdata 
                                        ORDER BY name""")
                    
                    with open('accounts_list.csv', 'w', newline='') as file:
                        writer = csv.writer(file)
                        writer.writerow(['Name', 'Weight'])
                        for row in cursor.fetchall():
                            writer.writerow(row)
                
                return redirect('main')
                
            except Exception as e:
                print(f"Error creating account: {e}")
                return render(request, 'welcome.html', {
                    'error': 'An error occurred while creating the account.',
                    'show_error': True
                })
    return redirect('welcome')

#  log in using ORM 
def login(request):
    if request.method == "POST":
        user_name = request.POST.get('name')
        weight = request.POST.get('weight')
        
        try:
            # Try to get the user from UserData model
            user = UserData.objects.get(name=user_name)
            
            # Check if weight matches
            if float(weight) == float(user.weight):
                request.session['user_name'] = user_name
                request.session['weight'] = weight
                return redirect('main')
            else:
                return render(request, 'welcome.html', {
                    'error': 'Incorrect weight.',
                    'show_error': True
                })
                
        except UserData.DoesNotExist:
            return render(request, 'welcome.html', {
                'error': 'Account does not exist. Please create an account first.',
                'show_error': True
            })
    
    return redirect('welcome')

# export accounts to a csv file using prepared statements
def export_accounts_to_file(request):
    with open('accounts_list.csv', 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['Name', 'Weight'])
        
        with connection.cursor() as cursor:
            cursor.execute("SELECT name, weight FROM part_1_userdata")
            for row in cursor.fetchall():
                writer.writerow(row)  

    return

# ORM
def day_planner(request):
    user_name = request.session.get('user_name')
    if not user_name:
        return redirect('welcome')
        
    selected_date = request.GET.get('date')
    if selected_date:
        selected_date = datetime.strptime(selected_date, '%Y-%m-%d').date()
    else:
        selected_date = datetime.now().date()

    day_plans = DayPlan.objects.filter(
        user_name=user_name,
        date=selected_date
    ).select_related('food_entry')

    available_foods = FoodEntry.objects.all().order_by('food_name')

    total_carbs = sum(plan.food_entry.carbs for plan in day_plans)
    total_protein = sum(plan.food_entry.protein for plan in day_plans)
    total_fats = sum(plan.food_entry.fats for plan in day_plans)
    total_calories = sum(plan.food_entry.calories for plan in day_plans)

    context = {
        'user_name': user_name,
        'selected_date': selected_date,
        'available_foods': available_foods,
        'day_plans': day_plans,
        'total_carbs': total_carbs,
        'total_protein': total_protein,
        'total_fats': total_fats,
        'total_calories': total_calories,
    }
    return render(request, 'day_planner.html', context)

# ORM
def add_to_plan(request):
    try:
        user_name = request.session.get('user_name')
        date = request.POST.get('date')
        food_entry_id = request.POST.get('food_entry')
        meal_type = request.POST.get('meal_type')

        if user_name and date and food_entry_id and meal_type:
            # Using primary key index for efficient lookup
            food_entry = get_object_or_404(FoodEntry, id=food_entry_id)
            date_obj = datetime.strptime(date, '%Y-%m-%d').date()

            # Create new day plan entry using indexed fields
            DayPlan.objects.create(
                user_name=user_name,
                date=date_obj,
                food_entry=food_entry,
                meal_type=meal_type
            )

            # Redirect back to the same date
            return redirect(f'/part_1/day-planner/?date={date}')
    except Exception as e:
        pass
    
    return redirect('day_planner')

# ORM
def remove_from_plan(request, plan_id):
    try:
        user_name = request.session.get('user_name')
        plan = get_object_or_404(DayPlan, id=plan_id, user_name=user_name)
        plan.delete()
        return redirect('day_planner')
    except Exception as e:
        return redirect('day_planner')

# ORM
def add_meal(request):
    if request.method == "POST":
        user_name = request.session.get('user_name')
        food_name = request.POST.get('food_name')
        carbs = float(request.POST.get('carbs'))
        protein = float(request.POST.get('protein'))
        fats = float(request.POST.get('fats'))
        calories = float(request.POST.get('calories'))
        meal_type = request.POST.get('meal_type')

        if user_name and food_name and meal_type:
            FoodEntry.objects.create(
                user_name=user_name,
                food_name=food_name,
                carbs=carbs,
                protein=protein,
                fats=fats,
                calories=calories,
                meal_type=meal_type
            )
        return redirect('main')
    return redirect('main')

# done with ORM
def export_day_plan(request):
    user_name = request.session.get('user_name')
    if not user_name:
        return redirect('welcome')

    # Get selected date
    date_str = request.GET.get('date')
    try:
        selected_date = datetime.strptime(date_str, '%Y-%m-%d').date()
    except (ValueError, TypeError):
        selected_date = timezone.now().date()

    # Create the HttpResponse object with CSV header
    response = HttpResponse(
        content_type='text/csv',
        headers={'Content-Disposition': f'attachment; filename="{user_name}_day_planner_{selected_date}.csv"'},
    )

    writer = csv.writer(response)
    
    # Write headers
    writer.writerow([f'Day Planner for {user_name}'])
    writer.writerow([f'Date: {selected_date.strftime("%B %d, %Y")}'])
    writer.writerow([])  # Empty row for spacing
    writer.writerow([
        'Meal Type',
        'Food Name',
        'Added By',
        'Carbs (g)',
        'Protein (g)',
        'Fats (g)',
        'Calories'
    ])

    # Get day plan entries using prepared statement
    with connection.cursor() as cursor:
        query = """
            SELECT 
                dp.meal_type,
                f.food_name,
                f.user_name,
                f.carbs,
                f.protein,
                f.fats,
                f.calories
            FROM part_1_dayplan dp
            JOIN part_1_foodentry f ON dp.food_entry_id = f.id
            WHERE dp.user_name = %s
            AND dp.date = %s
            ORDER BY 
                CASE 
                    WHEN dp.meal_type = 'breakfast' THEN 1
                    WHEN dp.meal_type = 'lunch' THEN 2
                    WHEN dp.meal_type = 'dinner' THEN 3
                    WHEN dp.meal_type = 'snack' THEN 4
                END,
                f.food_name
        """
        cursor.execute(query, [user_name, selected_date])
        day_plan_entries = cursor.fetchall()

        # Write entries by meal type
        current_meal_type = None
        for entry in day_plan_entries:
            if current_meal_type != entry[0]:  # New meal type section
                writer.writerow([])  # Add spacing
                writer.writerow([f'{entry[0].upper()} ENTRIES'])
                current_meal_type = entry[0]
            
            writer.writerow([
                entry[0].title(),  # meal_type
                entry[1],          # food_name
                entry[2],          # user_name
                entry[3],          # carbs
                entry[4],          # protein
                entry[5],          # fats
                entry[6]           # calories
            ])

        # Calculate totals for the day
        totals_query = """
            SELECT 
                SUM(f.carbs) as total_carbs,
                SUM(f.protein) as total_protein,
                SUM(f.fats) as total_fats,
                SUM(f.calories) as total_calories
            FROM part_1_dayplan dp
            JOIN part_1_foodentry f ON dp.food_entry_id = f.id
            WHERE dp.user_name = %s
            AND dp.date = %s
        """
        cursor.execute(totals_query, [user_name, selected_date])
        totals = cursor.fetchone()

        # Write daily totals
        writer.writerow([])  # Empty row for spacing
        writer.writerow(['DAILY TOTALS'])
        writer.writerow([
            'Total',
            '',
            '',
            round(totals[0] or 0, 2),  # total_carbs
            round(totals[1] or 0, 2),  # total_protein
            round(totals[2] or 0, 2),  # total_fats
            round(totals[3] or 0, 2)   # total_calories
        ])

    return response

# done with prepared statments
def export_all_entries(request):
    user_name = request.session.get('user_name')
    if not user_name:
        return redirect('welcome')

    # Create the HttpResponse object with CSV header
    response = HttpResponse(
        content_type='text/csv',
        headers={'Content-Disposition': f'attachment; filename="{user_name}_all_entries.csv"'},
    )

    writer = csv.writer(response)
    
    # Write headers
    writer.writerow([f'Food Entries for {user_name}'])
    writer.writerow([])  # Empty row for spacing
    writer.writerow([
        'Meal Type',
        'Food Name',
        'Added By',
        'Carbs (g)',
        'Protein (g)',
        'Fats (g)',
        'Calories'
    ])

    # Get all entries using prepared statement
    with connection.cursor() as cursor:
        query = """
            SELECT meal_type, food_name, user_name, carbs, protein, fats, calories 
            FROM part_1_foodentry 
            ORDER BY meal_type, food_name
        """
        cursor.execute(query)
        all_entries = cursor.fetchall()

        # Write all entries
        for entry in all_entries:
            writer.writerow([
                entry[0].title(),  # meal_type
                entry[1],          # food_name
                entry[2],          # user_name
                entry[3],          # carbs
                entry[4],          # protein
                entry[5],          # fats
                entry[6]           # calories
            ])

        # Calculate totals
        totals_query = """
            SELECT 
                SUM(carbs) as total_carbs,
                SUM(protein) as total_protein,
                SUM(fats) as total_fats,
                SUM(calories) as total_calories
            FROM part_1_foodentry
        """
        cursor.execute(totals_query)
        totals = cursor.fetchone()

        # Write totals
        writer.writerow([])  # Empty row for spacing
        writer.writerow(['TOTALS'])
        writer.writerow([
            'Total',
            '',
            '',
            round(totals[0] or 0, 2),  # total_carbs
            round(totals[1] or 0, 2),  # total_protein
            round(totals[2] or 0, 2),  # total_fats
            round(totals[3] or 0, 2)   # total_calories
        ])

    return response
# ORM
def create_food_entry(request):
    try:
        with transaction.atomic():
            connection.set_isolation_level(transaction.ISOLATION_LEVEL_SERIALIZABLE)
            
            user_name = request.session.get('user_name')
            food_name = request.POST.get('food_name')
            carbs = float(request.POST.get('carbs', 0))
            protein = float(request.POST.get('protein', 0))
            fats = float(request.POST.get('fats', 0))
            calories = float(request.POST.get('calories', 0))
            meal_type = request.POST.get('meal_type')

            if user_name and food_name and meal_type:
                FoodEntry.objects.create(
                    user_name=user_name,
                    food_name=food_name,
                    carbs=carbs,
                    protein=protein,
                    fats=fats,
                    calories=calories,
                    meal_type=meal_type
                )
                
    except IntegrityError:
        # Handle concurrent modification
        messages.error(request, "Error creating food entry. Please try again.")
        return redirect('main')
    except ValueError:
        # Handle invalid numeric values
        messages.error(request, "Invalid values provided. Please check your input.")
        return redirect('main')
    
    return redirect('main')
# ORM
def move_plan_entry(request, plan_id):
    try:
        user_name = request.session.get('user_name')
        new_date = request.POST.get('new_date')
        
        if user_name and new_date:
            with transaction.atomic():
                # REPEATABLE READ is appropriate here
                connection.set_isolation_level(transaction.ISOLATION_LEVEL_REPEATABLE_READ)
                plan = DayPlan.objects.select_for_update().get(
                    id=plan_id, 
                    user_name=user_name
                )
                
                new_date_obj = datetime.strptime(new_date, '%Y-%m-%d').date()
                plan.date = new_date_obj
                plan.save()
                
                return redirect(f'/part_1/day-planner/?date={new_date}')
    except Exception as e:
        pass
    
    return redirect('day_planner')
# ORM
def update_user_data(request):
    try:
        user_name = request.session.get('user_name')
        with transaction.atomic():
            connection.set_isolation_level(transaction.ISOLATION_LEVEL_REPEATABLE_READ)
            user = UserData.objects.select_for_update().get(name=user_name)
            user.save()
    except IntegrityError:
        return redirect('welcome')
# ORM
def modify_day_plan(request, plan_id):
    try:
        with transaction.atomic():
            connection.set_isolation_level(transaction.ISOLATION_LEVEL_REPEATABLE_READ)
            plan = DayPlan.objects.select_for_update().get(id=plan_id)
            plan.save()
    except IntegrityError:
        return redirect('day_planner')
