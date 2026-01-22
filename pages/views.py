from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.db import transaction # Important for safe database saving
from django.contrib.auth.decorators import login_required

# Import your models
from .models import Farmer, Hotel, Product
# Import your form (Make sure you have created forms.py, otherwise comment this line out)
# from .forms import ProductForm 

# --- 1. STATIC PAGE VIEWS ---
def home(request):
    return render(request, 'pages/home.html')

def login_hotel(request):
    return render(request, "pages/login_hotel.html")

def login_farmer(request):
    return render(request, "pages/login_farmer.html")

def register_view(request):
    return render(request, "pages/register.html")

def orders(request):
    return render(request, "pages/orders.html")

def profile(request):
    return render(request, "pages/profile.html")

# --- 3. REGISTRATION API (FIXED) ---
@csrf_exempt
def register_api(request):
    if request.method == 'POST':
        print("--- Register API Triggered ---")
        
        # 1. Get data using the names EXACTLY as sent by your JavaScript
        email = request.POST.get('email')
        password = request.POST.get('password')
        role = request.POST.get('role')       # "Farmer" or "Hotel"
        
        # JS sends 'full_name' and 'entity_name' (farm/hotel name)
        full_name = request.POST.get('full_name') 
        entity_name = request.POST.get('entity_name') 
        phone = request.POST.get('phone')

        print(f"Data Received: {email} | {role} | {entity_name} | {full_name}")

        # 2. Check if email exists
        if User.objects.filter(username=email).exists():
            return HttpResponse("Email already registered")

        try:
            with transaction.atomic(): # Safe saving
                # Create the Login User
                user = User.objects.create_user(username=email, email=email, password=password)
                print(f"--- User Created: {user.username} ---")

                # Create the Specific Profile
                if role == 'Farmer':
                    # Note: Ensure your models.py fields match these names (full_name, farm_name)
                    Farmer.objects.create(
                        user=user, 
                        full_name=full_name, 
                        farm_name=entity_name, 
                        phone=phone,
                        email=email,
                        password=password
                    )
                    print("--- Farmer Table Updated ---")
                
                elif role == 'Hotel':
                    Hotel.objects.create(
                        user=user, 
                        full_name=full_name, 
                        hotel_name=entity_name, 
                        phone=phone,
                        email=email,
                        password=password
                    )
                    print("--- Hotel Table Updated ---")

            return HttpResponse("success")
        
        except Exception as e:
            print(f"--- CRITICAL ERROR: {e} ---")
            return HttpResponse(f"Server Error: {e}")

    return HttpResponse("Invalid request")

# --- 4. DASHBOARD VIEWS ---
def dashboard_view(request):
    products_list = Product.objects.all()
    
    context = {
        "products": products_list,
        # "form": form
    }
    return render(request, "pages/manage_products.html", context)

@login_required(login_url='login_farmer') # Protect this page
def farmer_dashboard_view(request):
    products = Product.objects.filter(farmer=request.user)
    
    context = {
        'products': products
    }
    return render(request, 'pages/farmer_dashboard.html', context)

def manage_produce_view(request):
    return render(request, "pages/manage_produce.html")

def order_requests_view(request):
    return render(request, "pages/order_requests.html")

def hotel_dashboard(request):
    products = Product.objects.all().order_by('-id')
    # We are sending 'products', NOT 'pages_products'
    context = {
        'products': products 
    }
    return render(request, 'pages/hotel_dashboard.html', context)
    
@login_required(login_url='login_hotel') # Protect this page
def browse_farmer(request):
    # 1. Fetch all farmers from the database
    farmers = Farmer.objects.all()

    # 2. Send them to the template
    context = {
        'farmers': farmers
    }
    return render(request, 'pages/browse_farmer.html', context)

def my_cart(request):
    return render(request , "pages/my_cart.html")

def hotel_profile(request):
    return render(request , "pages/hotel_profile.html")

def smart_login_view(request):
    if request.method == 'POST':
        email = request.POST.get('username')  # The input name in HTML
        password = request.POST.get('password')

        # 1. Check if Email/Password matches Auth User table
        user = authenticate(request, username=email, password=password)

        if user is not None:
            # 2. Log them in
            login(request, user)

            # 3. Check Role & Redirect
            # Django checks if this user ID exists in the 'farmer' table
            if hasattr(user, 'farmer'):
                return redirect('farmer_dashboard')
            
            # Django checks if this user ID exists in the 'hotel' table
            elif hasattr(user, 'hotel'):
                return redirect('hotel_dashboard')
            
            # Fallback for admins or users with no profile
            else:
                return redirect('home')

        else:
            messages.error(request, "Invalid email or password.")
            # If you are using a modal, we usually reload home 
            # and let JS show the error, or redirect to a dedicated login page.
            return redirect('home') 

    # If someone tries to go to /login/ directly, just show home
    return redirect('home')

from django.contrib.auth.decorators import user_passes_test

# 1. Define the check: Must be a Superuser
def is_superuser(user):
    return user.is_authenticated and user.is_superuser

# 2. The View with the redirect logic
# 'login_url' tells Django: "If they aren't logged in, send them HERE."
@user_passes_test(is_superuser, login_url='/admin/login/') 
def admin_dashboard(request):
    
    # ... (Your existing logic to get counts/data) ...
    total_farmers = Farmer.objects.count()
    total_hotels = Hotel.objects.count()
    total_users = User.objects.count()

    recent_farmers = Farmer.objects.all().order_by('-id')[:5]
    recent_hotels = Hotel.objects.all().order_by('-id')[:5]

    context = {
        'total_farmers': total_farmers,
        'total_hotels': total_hotels,
        'total_users': total_users,
        'recent_farmers': recent_farmers,
        'recent_hotels': recent_hotels,
    }
    return render(request, 'pages/admin_dashboard.html', context)

def manage_farmers(request):
    farmers = Farmer.objects.all()
    context = {'farmers': farmers}
    return render(request, 'pages/manage_farmers.html', context)

def manage_hotels(request):
    hotels = Hotel.objects.all()
    context = {'hotels': hotels}
    return render(request, 'pages/manage_hotels.html', context)

def add_farmers(request):
    if request.method == 'POST':
        full_name = request.POST.get('full_name')
        farm_name = request.POST.get('farm_name')
        phone = request.POST.get('phone')
        email = request.POST.get('email')
        password = request.POST.get('password')

        # Create User
        user = User.objects.create_user(username=email, email=email, password=password)

        # Create Farmer Profile
        Farmer.objects.create(
            user=user,
            full_name=full_name,
            farm_name=farm_name,
            phone=phone,
            email=email,
            password=password
        )

        return redirect('manage_farmers')

    return render(request, 'pages/add_farmers.html')

def add_hotels(request):
    if request.method == 'POST':
        full_name = request.POST.get('full_name')
        hotel_name = request.POST.get('hotel_name')
        phone = request.POST.get('phone')
        email = request.POST.get('email')
        password = request.POST.get('password')

        # Create User
        user = User.objects.create_user(username=email, email=email, password=password)

        # Create Hotel Profile
        Hotel.objects.create(
            user=user,
            full_name=full_name,
            hotel_name=hotel_name,
            phone=phone,
            email=email,
            password=password
        )

        return redirect('manage_hotels')

    return render(request, 'pages/add_hotels.html')

def export_report(request):
    # Logic to generate and export report
    return HttpResponse("Report exported successfully.")

from django.shortcuts import render
from django.db.models import Sum
from django.db.models.functions import TruncDay, TruncMonth
from django.utils import timezone
from datetime import timedelta
import json
from .models import Order, Profile, Product
from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.models import User
from .forms import AddFarmerForm, AddHotelForm # Import the forms we just made
from django.contrib import messages
import csv
from django.http import HttpResponse
from django.utils import timezone
from datetime import timedelta
# ... existing views ...
from .forms import AddFarmerForm, AddHotelForm # <--- Add AddHotelForm here
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages # To show error messages


# ... existing views ...

def delete_user(request, user_id):
    # Get the user or show 404 error
    user = get_object_or_404(User, id=user_id)
    
    # Check role to decide where to redirect after deleting
    # We use a try/except block in case the user has no profile
    try:
        role = user.profile.role
    except:
        role = 'farmer' # Default fallback

    # Delete the user (This deletes Profile, Products, and Orders automatically)
    user.delete()
    
    # Redirect back to the correct page
    if role == 'hotel':
        return redirect('manage_hotels')
    return redirect('manage_farmers')


def manage_products(request):
    products = Product.objects.all()
    # We pass 'products' to the HTML file
    return render(request, 'pages/manage_products.html', {'products': products})

# Don't forget the delete logic we added earlier!
def delete_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    product.delete()
    return redirect('manage_products')


def export_report(request):
    # 1. Get the time period from the URL (default to 'monthly')
    period = request.GET.get('period', 'monthly')

    # 2. Calculate the date range
    today = timezone.now()
    if period == 'weekly':
        start_date = today - timedelta(days=7)
        filename = "report_weekly.csv"
    elif period == 'yearly':
        start_date = today - timedelta(days=365)
        filename = "report_yearly.csv"
    else: # monthly
        start_date = today - timedelta(days=30)
        filename = "report_monthly.csv"

    # 3. Create the CSV Response Object
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'

    # 4. Create the CSV Writer
    writer = csv.writer(response)

    # 5. Write the Header Row
    writer.writerow(['Date Joined', 'Username', 'Role', 'Email', 'Phone', 'Status'])

    # 6. Query the Database (Filter by date joined)
    # Note: We are filtering Profile based on the User's join date
    users = Profile.objects.select_related('user').filter(user__date_joined__gte=start_date)

    # 7. Write the Data Rows
    for profile in users:
        writer.writerow([
            profile.user.date_joined.strftime("%Y-%m-%d %H:%M"), # Date
            profile.user.username,                               # Name
            profile.role.capitalize(),                           # Role (Farmer/Hotel)
            profile.user.email,                                  # Email
            profile.phone,                                       # Phone
            "Active" if profile.is_approved else "Pending"       # Status
        ])

    return response

#register form for farmer and hotel

def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            # 1. Create User
            user = User.objects.create_user(
                username=form.cleaned_data['username'],
                email=form.cleaned_data['email'],
                password=form.cleaned_data['password']
            )
            user.first_name = form.cleaned_data['first_name']
            user.last_name = form.cleaned_data['last_name']
            user.save()

            # 2. Create Profile
            Profile.objects.create(
                user=user,
                role=form.cleaned_data['role'],
                phone=form.cleaned_data['phone'],
                address=form.cleaned_data['address'],
                is_approved=True  # Auto-approve for now so you can test easily
            )
            
            messages.success(request, 'Account created! Please login.')
            return redirect('login')
    else:
        form = RegisterForm()
    
    return render(request, 'pages/register.html', {'form': form})

from .forms import RegisterForm


# pages/views.py
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from .models import Product, Farmer

# pages/views.py
import json
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt # Optional if using CSRF token in header
from .models import Product

# pages/views.py

@login_required
def add_inventory_api(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            
            # --- FIX IS HERE ---
            # Don't use this: farmer_profile = request.user.farmer
            
            Product.objects.create(
                # The DB expects a User, so we give it the logged-in User
                farmer=request.user,  
                
                name=data.get('name'),
                category=data.get('category'),
                unit=data.get('unit'),
                quantity=data.get('qty'),
                price=data.get('price')
            )
            
            return JsonResponse({'message': 'Product added!'}, status=201)
            
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)

def add_product_page(request):
    return render(request, 'pages/add_product.html')

from .models import CartItem


@login_required
def add_to_cart(request, product_id):
    if request.method == 'POST':
        product_obj = get_object_or_404(Product, id=product_id)
        
        if not hasattr(request.user, 'hotel'):
             return JsonResponse({'error': 'For Hotels only'}, status=403)
        
        # WE USE 'produce=' BECAUSE YOUR MODEL FIELD IS NAMED 'produce'
        cart_item, created = CartItem.objects.get_or_create(
            hotel=request.user.hotel, 
            product=product_obj  
        )
        
        if not created:
            # Note: Your model expects Decimal (kg), so we add 1.0
            cart_item.quantity += 1 
            cart_item.save()
            
        return JsonResponse({'message': 'Added!'})
