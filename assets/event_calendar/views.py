from django.shortcuts import render, redirect
from django.http import JsonResponse
from .models import Event
from .forms import EventForm
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.utils.dateparse import parse_datetime
from django.utils.timezone import make_aware

# Display events on the calendar
@login_required
def calendar_view(request):
    # Fetch events for the logged-in user, or all events if needed
    events = Event.objects.all()  # You can filter based on user roles or access rights if needed
    return render(request, 'calendar.html', context={'events': events})

# Add a new event
# calendar/views.py
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.dateparse import parse_datetime
from .models import Event

@csrf_exempt  # You can remove this if you're using CSRF token correctly in JS
def add_event(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        start_time = parse_datetime(request.POST.get('start_time'))
        end_time = parse_datetime(request.POST.get('end_time'))
        category = request.POST.get('category')
        color = request.POST.get('color')

        if not all([title, start_time, end_time]):
            return JsonResponse({'success': False, 'message': 'Missing required fields'})

        event = Event.objects.create(
            title=title,
            start_time=start_time,
            end_time=end_time,
            category=category,
            color=color
        )

        return JsonResponse({
            'success': True,
            'event': {
                'id': event.id,
                'title': event.title,
                'start_time': event.start_time.isoformat(),
                'end_time': event.end_time.isoformat(),
                'color': event.color
            }
        })
    return JsonResponse({'success': False, 'message': 'Invalid request method'})

# Edit an event
@login_required
def edit_event(request, event_id):
    try:
        event = Event.objects.get(id=event_id)

        if request.method == 'POST':
            event.title = request.POST.get('title', event.title)
            event.start_time = make_aware(parse_datetime(request.POST.get('start_time', event.start_time)))
            event.end_time = make_aware(parse_datetime(request.POST.get('end_time', event.end_time)))
            event.color = request.POST.get('color', event.color)
            
            event.save()

            return JsonResponse({
                'success': True,
                'message': 'Event updated successfully.',
                'event': {
                    'id': event.id,
                    'title': event.title,
                    'start_time': event.start_time.isoformat(),
                    'end_time': event.end_time.isoformat(),
                    'color': event.color,
                }
            })
    except Event.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Event not found.'})

    return JsonResponse({'success': False, 'message': 'Invalid request method.'})

# Delete an event
@login_required
def delete_event(request, event_id):
    try:
        event = Event.objects.get(id=event_id)
        event.delete()
        return JsonResponse({'success': True, 'message': 'Event deleted successfully.'})
    except Event.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Event not found.'})

# Get all events
def all_events(request):
    events = Event.objects.all()
    event_list = []
    for event in events:
        event_list.append({
            "title": event.title,
            "start": event.start_time.isoformat(),
            "end": event.end_time.isoformat(),
            "color": event.color,
        })
    return JsonResponse(event_list, safe=False)

# Get events (can be used for a specific user's view if needed)
def get_events(request):
    events = Event.objects.all()
    data = []
    for event in events:
        data.append({
            "title": event.title,
            "start": event.start_time.isoformat(),
            "end": event.end_time.isoformat(),
            "color": event.color,
        })
    return JsonResponse(data,safe=False)
